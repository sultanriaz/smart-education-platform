from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass
from typing import Any

from smartedu_contracts import EventEnvelope

try:
    import aio_pika
    from aio_pika import DeliveryMode, ExchangeType, Message
except ImportError:  # pragma: no cover - integration dependency
    aio_pika = None  # type: ignore[assignment]
    DeliveryMode = ExchangeType = Message = None  # type: ignore[assignment]

from .settings import MessagingSettings


@dataclass(frozen=True, slots=True)
class QueueBinding:
    queue_name: str
    retry_queue_name: str
    retry_routing_key: str
    routing_keys: tuple[str, ...]
    dead_letter_queue_name: str


def service_queue_name(prefix: str, service_name: str) -> str:
    clean = service_name.strip().replace("_", "-")
    return f"{prefix}.{clean}.events"


def retry_queue_name(prefix: str, service_name: str) -> str:
    return f"{service_queue_name(prefix, service_name)}.retry"


def retry_routing_key(prefix: str, service_name: str) -> str:
    clean = service_name.strip().replace("_", "-")
    return f"{prefix}.retry.{clean}"


def dead_letter_queue_name(prefix: str, service_name: str) -> str:
    clean = service_name.strip().replace("_", "-")
    return f"{prefix}.{clean}.events.dlq"


def binding_plan(
    *,
    prefix: str,
    service_name: str,
    routing_keys: Iterable[str],
) -> QueueBinding:
    keys = tuple(dict.fromkeys(key.strip() for key in routing_keys if key.strip()))
    if not keys:
        raise ValueError("At least one event routing key is required")
    return QueueBinding(
        queue_name=service_queue_name(prefix, service_name),
        retry_queue_name=retry_queue_name(prefix, service_name),
        retry_routing_key=retry_routing_key(prefix, service_name),
        routing_keys=keys,
        dead_letter_queue_name=dead_letter_queue_name(prefix, service_name),
    )


class RabbitEventBus:
    def __init__(
        self,
        *,
        service_name: str,
        settings: MessagingSettings,
    ):
        self.service_name = service_name
        self.settings = settings
        self._connection = None
        self._channel = None
        self._event_exchange = None
        self._retry_exchange = None
        self._dlx = None
        self._plan: QueueBinding | None = None

    async def connect(self) -> None:
        if aio_pika is None:
            raise RuntimeError("aio-pika is required for RabbitEventBus")

        self._connection = await aio_pika.connect_robust(self.settings.rabbitmq_url)
        self._channel = await self._connection.channel(
            publisher_confirms=True,
            on_return_raises=True,
        )
        await self._channel.set_qos(prefetch_count=self.settings.prefetch_count)

        self._event_exchange = await self._channel.declare_exchange(
            self.settings.event_exchange,
            ExchangeType.TOPIC,
            durable=True,
        )
        self._retry_exchange = await self._channel.declare_exchange(
            self.settings.retry_exchange,
            ExchangeType.DIRECT,
            durable=True,
        )
        self._dlx = await self._channel.declare_exchange(
            self.settings.dead_letter_exchange,
            ExchangeType.DIRECT,
            durable=True,
        )

    async def close(self) -> None:
        if self._channel is not None and not self._channel.is_closed:
            await self._channel.close()
        if self._connection is not None and not self._connection.is_closed:
            await self._connection.close()

    async def _ensure_connected(self) -> None:
        if self._connection is None or self._connection.is_closed:
            await self.connect()

    async def publish(self, envelope: EventEnvelope) -> None:
        await self._ensure_connected()
        assert self._event_exchange is not None

        payload = envelope.model_dump(mode="json")
        message = Message(
            body=json.dumps(payload, separators=(",", ":")).encode(),
            content_type="application/json",
            delivery_mode=DeliveryMode.PERSISTENT,
            message_id=str(envelope.event_id),
            correlation_id=envelope.correlation_id,
            headers={
                "event_type": envelope.event_type,
                "event_version": envelope.event_version,
                "source": envelope.source,
                "x-smartedu-attempt": 1,
            },
        )

        await asyncio.wait_for(
            self._event_exchange.publish(
                message,
                routing_key=envelope.event_type,
                mandatory=True,
            ),
            timeout=self.settings.publish_timeout_seconds,
        )

    async def declare_consumer_queue(
        self,
        routing_keys: Iterable[str],
    ):
        await self._ensure_connected()
        assert self._channel is not None
        assert self._event_exchange is not None
        assert self._retry_exchange is not None
        assert self._dlx is not None

        plan = binding_plan(
            prefix=self.settings.queue_prefix,
            service_name=self.service_name,
            routing_keys=routing_keys,
        )
        self._plan = plan

        dlq = await self._channel.declare_queue(
            plan.dead_letter_queue_name,
            durable=True,
        )
        await dlq.bind(
            self._dlx,
            routing_key=plan.dead_letter_queue_name,
        )

        retry_queue = await self._channel.declare_queue(
            plan.retry_queue_name,
            durable=True,
            arguments={
                "x-message-ttl": self.settings.retry_delay_ms,
                "x-dead-letter-exchange": self.settings.event_exchange,
                "x-dead-letter-routing-key": plan.retry_routing_key,
            },
        )
        await retry_queue.bind(
            self._retry_exchange,
            routing_key=plan.retry_routing_key,
        )

        queue = await self._channel.declare_queue(
            plan.queue_name,
            durable=True,
        )
        for key in plan.routing_keys:
            await queue.bind(self._event_exchange, routing_key=key)

        # Retry messages return here using one service-specific routing key.
        await queue.bind(
            self._event_exchange,
            routing_key=plan.retry_routing_key,
        )
        return queue

    def _copy_message(
        self,
        original,
        *,
        headers: dict[str, Any],
    ):
        return Message(
            body=original.body,
            content_type=original.content_type or "application/json",
            content_encoding=original.content_encoding,
            delivery_mode=DeliveryMode.PERSISTENT,
            message_id=original.message_id,
            correlation_id=original.correlation_id,
            timestamp=original.timestamp,
            type=original.type,
            app_id=original.app_id,
            headers=headers,
        )

    async def _retry_or_dead_letter(self, message) -> None:
        assert self._plan is not None
        assert self._retry_exchange is not None
        assert self._dlx is not None

        headers = dict(message.headers or {})
        try:
            attempt = int(headers.get("x-smartedu-attempt", 1))
            if attempt < 1:
                raise ValueError("Invalid delivery attempt")
        except (TypeError, ValueError, OverflowError):
            # Poison headers must not create an endless unacknowledged loop.
            attempt = self.settings.max_delivery_attempts

        if attempt >= self.settings.max_delivery_attempts:
            headers["x-smartedu-final-attempt"] = attempt
            dead = self._copy_message(message, headers=headers)
            await asyncio.wait_for(
                self._dlx.publish(
                    dead,
                    routing_key=self._plan.dead_letter_queue_name,
                    mandatory=True,
                ),
                timeout=self.settings.publish_timeout_seconds,
            )
            await message.ack()
            return

        headers["x-smartedu-attempt"] = attempt + 1
        retry = self._copy_message(message, headers=headers)
        await asyncio.wait_for(
            self._retry_exchange.publish(
                retry,
                routing_key=self._plan.retry_routing_key,
                mandatory=True,
            ),
            timeout=self.settings.publish_timeout_seconds,
        )
        await message.ack()

    async def consume(
        self,
        routing_keys: Iterable[str],
        handler: Callable[[EventEnvelope], Awaitable[None]],
    ) -> None:
        queue = await self.declare_consumer_queue(routing_keys)

        async def on_message(message):
            try:
                payload: Any = json.loads(message.body)
                envelope = EventEnvelope.model_validate(payload)
                await handler(envelope)
            except Exception:
                try:
                    await self._retry_or_dead_letter(message)
                except Exception:
                    # Preserve the original delivery if the broker cannot confirm
                    # its durable retry/DLQ copy. Reconnect will also redeliver it.
                    await message.nack(requeue=True)
            else:
                await message.ack()

        await queue.consume(on_message, no_ack=False)


class EventRouter:
    def __init__(self):
        self._handlers: dict[str, Callable[[EventEnvelope], Awaitable[None]]] = {}

    def register(
        self,
        event_type: str,
        handler: Callable[[EventEnvelope], Awaitable[None]],
    ) -> None:
        if event_type in self._handlers:
            raise ValueError(f"Handler already registered for {event_type}")
        self._handlers[event_type] = handler

    @property
    def routing_keys(self) -> tuple[str, ...]:
        return tuple(sorted(self._handlers))

    async def handle(self, envelope: EventEnvelope) -> None:
        handler = self._handlers.get(envelope.event_type)
        if handler is None:
            raise ValueError(f"Unsupported event type: {envelope.event_type}")
        await handler(envelope)

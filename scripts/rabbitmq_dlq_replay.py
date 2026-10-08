from __future__ import annotations

import argparse
import asyncio
import json

from smartedu_contracts import EventEnvelope
from smartedu_infra import (
    MessagingSettings,
    RabbitEventBus,
    dead_letter_queue_name,
)

try:
    import aio_pika
except ImportError as exc:  # pragma: no cover
    raise SystemExit("aio-pika is required") from exc


async def replay(service_name: str, limit: int) -> None:
    settings = MessagingSettings()
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await connection.channel(publisher_confirms=True)
    dlq_name = dead_letter_queue_name(settings.queue_prefix, service_name)
    dlq = await channel.declare_queue(dlq_name, durable=True, passive=True)

    bus = RabbitEventBus(service_name=service_name, settings=settings)
    await bus.connect()

    count = 0
    try:
        while count < limit:
            message = await dlq.get(fail=False)
            if message is None:
                break

            try:
                payload = json.loads(message.body)
                envelope = EventEnvelope.model_validate(payload)
                await bus.publish(envelope)
            except Exception:
                await message.reject(requeue=True)
                raise
            else:
                await message.ack()
                count += 1
    finally:
        await bus.close()
        await channel.close()
        await connection.close()

    print(f"Replayed {count} messages from {dlq_name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("service_name")
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()
    asyncio.run(replay(args.service_name, args.limit))


if __name__ == "__main__":
    main()

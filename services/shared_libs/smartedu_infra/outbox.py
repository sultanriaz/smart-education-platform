from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass
from typing import Any

from smartedu_contracts import EventEnvelope

from .messaging import RabbitEventBus


@dataclass(frozen=True, slots=True)
class OutboxItem:
    record_id: Any
    envelope: EventEnvelope


class OutboxPublisher:
    """
    Domain-neutral publisher loop.

    The owning service supplies transactional fetch/mark callbacks backed by its
    own outbox table. This class deliberately knows nothing about another
    service's ORM schema.
    """

    def __init__(
        self,
        bus: RabbitEventBus,
        *,
        fetch_batch: Callable[[int], Awaitable[Sequence[OutboxItem]]],
        mark_published: Callable[[Any], Awaitable[None]],
        mark_failed: Callable[[Any, str], Awaitable[None]],
    ):
        self.bus = bus
        self.fetch_batch = fetch_batch
        self.mark_published = mark_published
        self.mark_failed = mark_failed

    async def run_once(self, *, batch_size: int = 100) -> int:
        items = await self.fetch_batch(batch_size)
        published = 0

        for item in items:
            try:
                await self.bus.publish(item.envelope)
            except Exception as exc:
                await self.mark_failed(item.record_id, exc.__class__.__name__)
            else:
                await self.mark_published(item.record_id)
                published += 1

        return published

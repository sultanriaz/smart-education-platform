from __future__ import annotations

import uuid

import pytest
from smartedu_contracts import EventEnvelope

from smartedu_infra.outbox import OutboxItem, OutboxPublisher


class FakeBus:
    def __init__(self):
        self.published = []

    async def publish(self, envelope):
        self.published.append(envelope)


@pytest.mark.asyncio
async def test_outbox_publisher_marks_success_only_after_publish():
    event = EventEnvelope(
        event_type="schedule.changed",
        source="scheduling-service",
        correlation_id="flow-1",
        data={"schedule_id": "s1"},
    )
    item = OutboxItem(record_id=uuid.uuid4(), envelope=event)
    published_ids = []
    failed = []

    async def fetch_batch(_limit):
        return [item]

    async def mark_published(record_id):
        published_ids.append(record_id)

    async def mark_failed(record_id, reason):
        failed.append((record_id, reason))

    bus = FakeBus()
    publisher = OutboxPublisher(
        bus,
        fetch_batch=fetch_batch,
        mark_published=mark_published,
        mark_failed=mark_failed,
    )

    count = await publisher.run_once()

    assert count == 1
    assert bus.published == [event]
    assert published_ids == [item.record_id]
    assert failed == []

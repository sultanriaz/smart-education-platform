from __future__ import annotations

from sqlalchemy import select

from app.domain.models import OutboxEvent, ScheduleAudit


def test_create_writes_audit_and_outbox(client, db, schedule_payload):
    response = client.post("/api/v1/schedules", json=schedule_payload)
    assert response.status_code == 201
    audits = list(db.scalars(select(ScheduleAudit)).all())
    events = list(db.scalars(select(OutboxEvent)).all())
    assert len(audits) == 1
    assert audits[0].action == "schedule.created"
    assert len(events) == 1
    assert events[0].event_type == "schedule.created"

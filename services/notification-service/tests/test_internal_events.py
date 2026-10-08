from __future__ import annotations

from app.domain.models import InboxEvent, Notification
from app.schemas.notification import InternalEventIn
from app.services.event_service import EventService


def test_internal_event_requires_token(client):
    response = client.post(
        "/api/v1/internal/events",
        json={
            "event_id": "evt-1",
            "source_service": "scheduling",
            "event_type": "schedule.updated",
        },
    )
    assert response.status_code == 401


def test_internal_event_is_idempotent(client, dispatcher):
    payload = {
        "event_id": "evt-2",
        "source_service": "scheduling",
        "event_type": "schedule.updated",
        "targets": {"user_ids": []},
        "payload": {"title": "Changed"},
    }
    headers = {"X-Internal-Token": "CHANGE_ME_INTERNAL_EVENT_TOKEN"}
    first = client.post("/api/v1/internal/events", json=payload, headers=headers)
    second = client.post("/api/v1/internal/events", json=payload, headers=headers)
    assert first.status_code == 202
    assert second.status_code == 202
    assert first.json()["duplicate"] is False
    assert second.json()["duplicate"] is True
    assert len(dispatcher.events) == 1


def test_event_processing_creates_notification(db, identities, fake_resolver):
    event, duplicate = EventService(db, fake_resolver).ingest(
        InternalEventIn(
            event_id="evt-3",
            source_service="attendance",
            event_type="attendance.low_attendance_detected",
            targets={"user_ids": [str(identities["student"])]},
            payload={"title": "Attendance warning", "message": "Below threshold"},
        )
    )
    assert duplicate is False
    EventService(db, fake_resolver).process(event.id)
    stored = db.query(Notification).one()
    assert stored.recipient_user_id == identities["student"]
    assert stored.title == "Attendance warning"
    assert db.get(InboxEvent, event.id).status == "PROCESSED"


def test_event_processing_without_recipient_marks_failed(db, fake_resolver):
    event, _ = EventService(db, fake_resolver).ingest(
        InternalEventIn(
            event_id="evt-4",
            source_service="unknown",
            event_type="unknown.event",
            payload={},
            targets={},
        )
    )
    try:
        EventService(db, fake_resolver).process(event.id)
    except Exception:
        pass
    db.expire_all()
    assert db.get(InboxEvent, event.id).status == "FAILED"

from __future__ import annotations

from app.core.config import settings
from app.domain.models import OutboxEvent
from app.workers import outbox_relay


def test_outbox_relay_posts_and_marks_published(db, monkeypatch):
    event = OutboxEvent(
        event_type="facility.booking_approved",
        aggregate_type="booking",
        aggregate_id=__import__("uuid").uuid4(),
        payload={"title": "Approved", "message": "Approved"},
        targets={"user_ids": [str(__import__("uuid").uuid4())]},
    )
    db.add(event)
    db.commit()

    class Response:
        def raise_for_status(self):
            return None

    calls = []

    def fake_post(url, json, headers, timeout):
        calls.append((url, json, headers))
        return Response()

    monkeypatch.setattr(outbox_relay, "SessionLocal", lambda: _Context(db))
    monkeypatch.setattr(outbox_relay.httpx, "post", fake_post)
    monkeypatch.setattr(settings, "NOTIFICATION_INTERNAL_EVENT_TOKEN", "token")
    count = outbox_relay.relay_once()
    assert count == 1
    assert calls[0][1]["source_service"] == "facility-service"
    assert event.published_at is not None


class _Context:
    def __init__(self, db):
        self.db = db

    def __enter__(self):
        return self.db

    def __exit__(self, *args):
        return False

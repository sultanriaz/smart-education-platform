from __future__ import annotations

from datetime import UTC, datetime

import httpx

from app.core.config import settings
from app.db.session import SessionLocal
from app.repositories.resource_repository import ResourceRepository


def relay_once() -> int:
    db = SessionLocal()
    published = 0
    try:
        repo = ResourceRepository(db)
        events = repo.list_unpublished_outbox(settings.OUTBOX_BATCH_SIZE)
        for event in events:
            envelope = {
                "event_id": str(event.id),
                "source_service": "learning-service",
                "event_type": event.event_type,
                "payload": event.payload,
                "targets": {},
            }
            response = httpx.post(
                f"{settings.NOTIFICATION_SERVICE_BASE_URL.rstrip('/')}/api/v1/internal/events",
                json=envelope,
                headers={"X-Internal-Token": settings.NOTIFICATION_INTERNAL_EVENT_TOKEN},
                timeout=5.0,
            )
            response.raise_for_status()
            event.published_at = datetime.now(UTC)
            published += 1
        db.commit()
        return published
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    count = relay_once()
    print(f"Published {count} outbox event(s)")

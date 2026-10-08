from __future__ import annotations

from datetime import UTC, datetime

import httpx
from sqlalchemy import select

from app.core.config import settings
from app.db.session import SessionLocal
from app.domain.entities.models import OutboxEvent


def relay_once() -> int:
    db = SessionLocal()
    sent = 0
    try:
        events = list(
            db.scalars(
                select(OutboxEvent)
                .where(OutboxEvent.published_at.is_(None))
                .order_by(OutboxEvent.created_at)
                .limit(settings.OUTBOX_BATCH_SIZE)
            ).all()
        )

        for event in events:
            response = httpx.post(
                f"{settings.NOTIFICATION_SERVICE_BASE_URL.rstrip('/')}/api/v1/internal/events",
                headers={"X-Internal-Token": settings.NOTIFICATION_INTERNAL_EVENT_TOKEN},
                json={
                    "event_id": str(event.id),
                    "source_service": "assessment-service",
                    "event_type": event.event_type,
                    "payload": event.payload,
                    "targets": {},
                },
                timeout=5,
            )
            response.raise_for_status()
            event.published_at = datetime.now(UTC)
            sent += 1

        db.commit()
        return sent
    finally:
        db.close()


if __name__ == "__main__":
    print(f"relayed={relay_once()}")

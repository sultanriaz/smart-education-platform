from __future__ import annotations

import time

import httpx

from app.core.config import settings
from app.db.session import SessionLocal
from app.repositories.outbox_repository import OutboxRepository


def relay_once() -> int:
    if not settings.NOTIFICATION_INTERNAL_EVENT_TOKEN:
        raise RuntimeError("NOTIFICATION_INTERNAL_EVENT_TOKEN is required for outbox relay")
    delivered = 0
    with SessionLocal() as db:
        repo = OutboxRepository(db)
        events = repo.list_unpublished(settings.OUTBOX_RELAY_BATCH_SIZE)
        for event in events:
            payload = {
                "event_id": str(event.id),
                "source_service": "facility-service",
                "event_type": event.event_type,
                "occurred_at": event.created_at.isoformat(),
                "payload": event.payload or {},
                "targets": event.targets or {},
            }
            try:
                response = httpx.post(
                    f"{settings.NOTIFICATION_SERVICE_BASE_URL.rstrip('/')}/api/v1/internal/events",
                    json=payload,
                    headers={"X-Internal-Token": settings.NOTIFICATION_INTERNAL_EVENT_TOKEN},
                    timeout=5.0,
                )
                response.raise_for_status()
            except httpx.HTTPError:
                db.rollback()
                raise
            repo.mark_published(event)
            db.commit()
            delivered += 1
    return delivered


def main() -> None:
    while True:
        try:
            relay_once()
        except Exception as exc:
            print(f"facility outbox relay error: {exc}", flush=True)
        time.sleep(settings.OUTBOX_RELAY_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()

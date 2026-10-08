from __future__ import annotations

import uuid

from app.db.session import SessionLocal
from app.queue.celery_app import celery_app
from app.services.delivery_service import DeliveryService
from app.services.event_service import EventService


@celery_app.task(name="notification.process_inbox_event", bind=True, max_retries=3)
def process_inbox_event(self, inbox_event_id: str):
    try:
        with SessionLocal() as db:
            pending = EventService(db).process(uuid.UUID(inbox_event_id))
        for attempt_id in pending:
            celery_app.send_task("notification.deliver_attempt", args=[str(attempt_id)])
    except Exception as exc:
        raise self.retry(exc=exc, countdown=min(300, 30 * (2**self.request.retries))) from exc


@celery_app.task(name="notification.deliver_attempt", bind=True, max_retries=3)
def deliver_attempt(self, attempt_id: str):
    try:
        with SessionLocal() as db:
            retry_id = DeliveryService(db).deliver(uuid.UUID(attempt_id))
        if retry_id:
            self.apply_async(args=[str(retry_id)], countdown=60)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=min(300, 30 * (2**self.request.retries))) from exc

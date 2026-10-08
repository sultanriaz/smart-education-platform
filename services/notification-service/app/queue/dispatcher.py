from __future__ import annotations

import uuid
from typing import Protocol

from app.core.config import settings


class TaskDispatcher(Protocol):
    def process_inbox_event(self, inbox_event_id: uuid.UUID) -> None: ...

    def deliver_attempt(self, attempt_id: uuid.UUID) -> None: ...


class CeleryTaskDispatcher:
    def _send(self, task_name: str, value: uuid.UUID) -> None:
        from app.queue.celery_app import celery_app

        celery_app.send_task(task_name, args=[str(value)])

    def process_inbox_event(self, inbox_event_id: uuid.UUID) -> None:
        self._send("notification.process_inbox_event", inbox_event_id)

    def deliver_attempt(self, attempt_id: uuid.UUID) -> None:
        self._send("notification.deliver_attempt", attempt_id)


class InlineTaskDispatcher:
    def process_inbox_event(self, inbox_event_id: uuid.UUID) -> None:
        from app.db.session import SessionLocal
        from app.services.event_service import EventService

        with SessionLocal() as db:
            pending = EventService(db).process(inbox_event_id)
        for attempt_id in pending:
            self.deliver_attempt(attempt_id)

    def deliver_attempt(self, attempt_id: uuid.UUID) -> None:
        from app.db.session import SessionLocal
        from app.services.delivery_service import DeliveryService

        with SessionLocal() as db:
            DeliveryService(db).deliver(attempt_id)


def get_task_dispatcher() -> TaskDispatcher:
    if settings.TASK_MODE.lower() == "celery":
        return CeleryTaskDispatcher()
    return InlineTaskDispatcher()

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.errors import ForbiddenError, NotFoundError
from app.domain.models import Notification, OutboxEvent
from app.repositories.notification_repository import NotificationRepository
from app.repositories.outbox_repository import OutboxRepository


class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = NotificationRepository(db)
        self.outbox = OutboxRepository(db)

    def list_for_user(self, user_id: uuid.UUID, unread_only: bool, offset: int, limit: int):
        return self.repo.list_user_notifications(
            user_id, unread_only=unread_only, offset=offset, limit=limit
        )

    def unread_count(self, user_id: uuid.UUID) -> int:
        return self.repo.count_unread(user_id)

    def get_for_user(self, notification_id: uuid.UUID, user_id: uuid.UUID) -> Notification:
        value = self.repo.get_notification(notification_id)
        if value is None:
            raise NotFoundError("Notification not found")
        if value.recipient_user_id != user_id:
            raise ForbiddenError("Notification belongs to another user")
        return value

    def mark_read(self, notification_id: uuid.UUID, user_id: uuid.UUID) -> Notification:
        value = self.get_for_user(notification_id, user_id)
        if value.status != "READ":
            value.status = "READ"
            value.read_at = datetime.now(UTC)
            self.outbox.add_event(
                OutboxEvent(
                    event_type="notification.read",
                    aggregate_type="notification",
                    aggregate_id=value.id,
                    payload={"recipient_user_id": str(user_id)},
                )
            )
            self.db.commit()
            self.db.refresh(value)
        return value

    def mark_all_read(self, user_id: uuid.UUID) -> int:
        count = self.repo.mark_all_read(user_id)
        if count:
            self.outbox.add_event(
                OutboxEvent(
                    event_type="notification.read_all",
                    aggregate_type="user",
                    aggregate_id=user_id,
                    payload={"count": count},
                )
            )
        self.db.commit()
        return count

    def archive(self, notification_id: uuid.UUID, user_id: uuid.UUID) -> Notification:
        value = self.get_for_user(notification_id, user_id)
        value.status = "ARCHIVED"
        self.db.commit()
        self.db.refresh(value)
        return value

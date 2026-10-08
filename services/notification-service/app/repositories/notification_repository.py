from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, selectinload

from app.domain.models import Notification


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_notification(self, notification: Notification) -> None:
        self.db.add(notification)

    def get_notification(self, notification_id: uuid.UUID) -> Notification | None:
        stmt = (
            select(Notification)
            .options(selectinload(Notification.deliveries))
            .where(Notification.id == notification_id)
        )
        return self.db.scalar(stmt)

    def list_user_notifications(
        self, user_id: uuid.UUID, *, unread_only: bool, offset: int, limit: int
    ) -> tuple[list[Notification], int]:
        filters = [
            Notification.recipient_user_id == user_id,
            Notification.in_app_visible.is_(True),
            Notification.status != "ARCHIVED",
        ]
        if unread_only:
            filters.append(Notification.status == "UNREAD")
        now = datetime.now(UTC)
        filters.append((Notification.expires_at.is_(None)) | (Notification.expires_at > now))
        total = self.db.scalar(select(func.count()).select_from(Notification).where(*filters)) or 0
        stmt = (
            select(Notification)
            .where(*filters)
            .order_by(Notification.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all()), int(total)

    def count_unread(self, user_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(Notification)
            .where(
                Notification.recipient_user_id == user_id,
                Notification.in_app_visible.is_(True),
                Notification.status == "UNREAD",
            )
        )
        return int(self.db.scalar(stmt) or 0)

    def mark_all_read(self, user_id: uuid.UUID) -> int:
        now = datetime.now(UTC)
        result = self.db.execute(
            update(Notification)
            .where(
                Notification.recipient_user_id == user_id,
                Notification.status == "UNREAD",
                Notification.in_app_visible.is_(True),
            )
            .values(status="READ", read_at=now)
        )
        return int(result.rowcount or 0)

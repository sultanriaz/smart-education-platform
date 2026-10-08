from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models import DeliveryAttempt


class DeliveryRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_attempt(self, attempt: DeliveryAttempt) -> None:
        self.db.add(attempt)

    def get_attempt(
        self, attempt_id: uuid.UUID, for_update: bool = False
    ) -> DeliveryAttempt | None:
        stmt = select(DeliveryAttempt).where(DeliveryAttempt.id == attempt_id)
        if for_update:
            stmt = stmt.with_for_update()
        return self.db.scalar(stmt)

    def list_attempts_for_notification(self, notification_id: uuid.UUID) -> list[DeliveryAttempt]:
        stmt = (
            select(DeliveryAttempt)
            .where(DeliveryAttempt.notification_id == notification_id)
            .order_by(DeliveryAttempt.created_at)
        )
        return list(self.db.scalars(stmt).all())

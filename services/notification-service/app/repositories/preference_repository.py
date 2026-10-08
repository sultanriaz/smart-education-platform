from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models import NotificationPreference


class PreferenceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: uuid.UUID) -> NotificationPreference | None:
        return self.db.scalar(
            select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        )

    def add_preference(self, preference: NotificationPreference) -> None:
        self.db.add(preference)

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.config import settings
from app.domain.models import NotificationPreference
from app.repositories.preference_repository import PreferenceRepository
from app.schemas.notification import PreferenceUpdate


class PreferenceService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PreferenceRepository(db)

    def get_or_create(self, user_id: uuid.UUID) -> NotificationPreference:
        value = self.repo.get_by_user_id(user_id)
        if value is not None:
            return value
        value = NotificationPreference(
            user_id=user_id,
            in_app_enabled=settings.DEFAULT_IN_APP_ENABLED,
            email_enabled=settings.DEFAULT_EMAIL_ENABLED,
            muted_categories=[],
        )
        self.repo.add_preference(value)
        self.db.commit()
        self.db.refresh(value)
        return value

    def update(self, user_id: uuid.UUID, payload: PreferenceUpdate) -> NotificationPreference:
        value = self.repo.get_by_user_id(user_id)
        if value is None:
            value = NotificationPreference(
                user_id=user_id,
                in_app_enabled=settings.DEFAULT_IN_APP_ENABLED,
                email_enabled=settings.DEFAULT_EMAIL_ENABLED,
                muted_categories=[],
            )
            self.repo.add_preference(value)
        if payload.in_app_enabled is not None:
            value.in_app_enabled = payload.in_app_enabled
        if payload.email_enabled is not None:
            value.email_enabled = payload.email_enabled
        if payload.muted_categories is not None:
            value.muted_categories = sorted(set(payload.muted_categories))
        self.db.commit()
        self.db.refresh(value)
        return value

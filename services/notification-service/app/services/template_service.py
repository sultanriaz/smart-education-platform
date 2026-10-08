from __future__ import annotations

import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.domain.models import NotificationTemplate
from app.repositories.template_repository import TemplateRepository
from app.schemas.notification import TemplateCreate, TemplateUpdate


class TemplateService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TemplateRepository(db)

    def create(self, payload: TemplateCreate, actor_user_id: uuid.UUID) -> NotificationTemplate:
        value = NotificationTemplate(
            code=payload.code,
            title_template=payload.title_template,
            body_template=payload.body_template,
            default_channels=list(payload.default_channels),
            category=payload.category,
            enabled=payload.enabled,
            created_by_user_id=actor_user_id,
        )
        self.repo.add_template(value)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError("Template code already exists") from exc
        self.db.refresh(value)
        return value

    def update(self, template_id: uuid.UUID, payload: TemplateUpdate) -> NotificationTemplate:
        value = self.repo.get_by_id(template_id)
        if value is None:
            raise NotFoundError("Template not found")
        for name in ["title_template", "body_template", "category", "enabled"]:
            replacement = getattr(payload, name)
            if replacement is not None:
                setattr(value, name, replacement)
        if payload.default_channels is not None:
            value.default_channels = list(payload.default_channels)
        self.db.commit()
        self.db.refresh(value)
        return value

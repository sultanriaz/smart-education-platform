from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models import NotificationTemplate


class TemplateRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_code(self, code: str) -> NotificationTemplate | None:
        return self.db.scalar(select(NotificationTemplate).where(NotificationTemplate.code == code))

    def get_by_id(self, template_id: uuid.UUID) -> NotificationTemplate | None:
        return self.db.get(NotificationTemplate, template_id)

    def list_templates(self) -> list[NotificationTemplate]:
        return list(
            self.db.scalars(select(NotificationTemplate).order_by(NotificationTemplate.code)).all()
        )

    def add_template(self, template: NotificationTemplate) -> None:
        self.db.add(template)

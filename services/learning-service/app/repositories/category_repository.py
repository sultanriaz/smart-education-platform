from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.models import ResourceCategory


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_categories(self) -> list[ResourceCategory]:
        return list(self.db.scalars(select(ResourceCategory).order_by(ResourceCategory.name)).all())

    def get_by_id(self, category_id: uuid.UUID) -> ResourceCategory | None:
        return self.db.get(ResourceCategory, category_id)

    def get_by_slug(self, slug: str) -> ResourceCategory | None:
        return self.db.scalar(select(ResourceCategory).where(ResourceCategory.slug == slug))

    def add(self, category: ResourceCategory) -> ResourceCategory:
        self.db.add(category)
        self.db.flush()
        return category

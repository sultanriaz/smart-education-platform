from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.errors import ConflictError
from app.domain.entities.models import ResourceCategory
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate


class CategoryService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CategoryRepository(db)

    def create_category(self, payload: CategoryCreate) -> ResourceCategory:
        if self.repo.get_by_slug(payload.slug):
            raise ConflictError("Category slug already exists")
        category = ResourceCategory(
            name=payload.name.strip(),
            slug=payload.slug,
            description=payload.description,
        )
        try:
            self.repo.add(category)
            self.db.commit()
            self.db.refresh(category)
            return category
        except Exception:
            self.db.rollback()
            raise

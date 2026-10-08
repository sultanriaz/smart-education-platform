from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models import OutboxEvent


class OutboxRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_event(self, event: OutboxEvent) -> None:
        self.db.add(event)
        self.db.flush()

    def list_unpublished(self, limit: int = 100) -> list[OutboxEvent]:
        stmt = (
            select(OutboxEvent)
            .where(OutboxEvent.published_at.is_(None))
            .order_by(OutboxEvent.created_at)
            .limit(limit)
        )
        if self.db.bind is not None and self.db.bind.dialect.name == "postgresql":
            stmt = stmt.with_for_update(skip_locked=True)
        return list(self.db.scalars(stmt).all())

    def mark_published(self, event: OutboxEvent) -> None:
        event.published_at = datetime.now(UTC)
        self.db.add(event)

from __future__ import annotations

from sqlalchemy.orm import Session

from app.domain.models import OutboxEvent


class OutboxRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_event(self, event: OutboxEvent) -> None:
        self.db.add(event)

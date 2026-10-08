from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models import InboxEvent


class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_event_id(self, event_id: str) -> InboxEvent | None:
        return self.db.scalar(select(InboxEvent).where(InboxEvent.event_id == event_id))

    def get_event(self, event_id: uuid.UUID, for_update: bool = False) -> InboxEvent | None:
        stmt = select(InboxEvent).where(InboxEvent.id == event_id)
        if for_update:
            stmt = stmt.with_for_update()
        return self.db.scalar(stmt)

    def add_event(self, event: InboxEvent) -> None:
        self.db.add(event)

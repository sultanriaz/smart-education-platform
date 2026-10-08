from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, Field


class InternalEventIn(BaseModel):
    event_id: uuid.UUID
    source_service: str = Field(min_length=2, max_length=80)
    event_type: str = Field(min_length=2, max_length=160)
    payload: dict = {}
    targets: dict = {}
    occurred_at: datetime | None = None

    def effective_occurred_at(self) -> datetime:
        return self.occurred_at or datetime.now(UTC)


class InternalEventResult(BaseModel):
    status: str
    event_id: uuid.UUID

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class AvailabilityQuery(BaseModel):
    starts_at: datetime
    ends_at: datetime

    @model_validator(mode="after")
    def valid_interval(self):
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at")
        return self


class AvailabilityConflict(BaseModel):
    kind: str
    id: uuid.UUID
    starts_at: datetime
    ends_at: datetime
    status: str
    description: str | None = None


class AvailabilityOut(BaseModel):
    facility_id: uuid.UUID
    starts_at: datetime
    ends_at: datetime
    available: bool
    conflicts: list[AvailabilityConflict] = Field(default_factory=list)

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FacilityBlockCreate(BaseModel):
    facility_id: uuid.UUID
    starts_at: datetime
    ends_at: datetime
    reason: str = Field(min_length=3, max_length=500)

    @model_validator(mode="after")
    def valid_interval(self):
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at")
        return self


class FacilityBlockOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    facility_id: uuid.UUID
    starts_at: datetime
    ends_at: datetime
    reason: str
    status: str
    created_by_user_id: uuid.UUID
    cancelled_by_user_id: uuid.UUID | None
    cancelled_at: datetime | None
    created_at: datetime

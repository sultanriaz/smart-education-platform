from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ExternalReservationCreate(BaseModel):
    facility_id: uuid.UUID
    source_service: str = Field(min_length=2, max_length=100)
    source_reference_id: str = Field(min_length=1, max_length=160)
    starts_at: datetime
    ends_at: datetime
    metadata: dict = Field(default_factory=dict)

    @model_validator(mode="after")
    def valid_interval(self):
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at")
        return self


class ExternalReservationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: uuid.UUID
    facility_id: uuid.UUID
    source_service: str
    source_reference_id: str
    starts_at: datetime
    ends_at: datetime
    status: str
    metadata: dict = Field(alias="metadata_json")
    created_at: datetime
    cancelled_at: datetime | None

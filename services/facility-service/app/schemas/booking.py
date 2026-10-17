from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BookingCreate(BaseModel):
    facility_id: uuid.UUID
    purpose: str = Field(min_length=3, max_length=500)
    requester_note: str | None = Field(default=None, max_length=2000)
    starts_at: datetime
    ends_at: datetime
    attendees: int = Field(gt=0, le=100000)

    @model_validator(mode="after")
    def valid_interval(self):
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at")
        return self


class BookingDecision(BaseModel):
    note: str | None = Field(default=None, max_length=2000)


class BookingCancel(BaseModel):
    reason: str = Field(min_length=3, max_length=2000)


class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    facility_id: uuid.UUID
    requester_user_id: uuid.UUID
    purpose: str
    requester_note: str | None
    starts_at: datetime
    ends_at: datetime
    attendees: int
    status: str
    requested_at: datetime
    reviewed_by_user_id: uuid.UUID | None
    reviewed_at: datetime | None
    review_note: str | None
    cancelled_by_user_id: uuid.UUID | None
    cancelled_at: datetime | None
    cancellation_reason: str | None
    created_at: datetime
    updated_at: datetime


class BookingHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    booking_id: uuid.UUID
    action: str
    previous_status: str | None
    new_status: str | None
    actor_user_id: uuid.UUID
    note: str | None
    snapshot: dict
    created_at: datetime

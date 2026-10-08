from __future__ import annotations

import uuid
from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ScheduleCreate(BaseModel):
    section_id: uuid.UUID
    teacher_user_id: uuid.UUID | None = None
    room_id: uuid.UUID | None = None
    weekday: int = Field(ge=0, le=6)
    starts_at: time
    ends_at: time
    effective_from: date
    effective_to: date
    timezone_name: str | None = Field(default=None, min_length=1, max_length=64)

    @model_validator(mode="after")
    def validate_window(self):
        if self.starts_at >= self.ends_at:
            raise ValueError("starts_at must be earlier than ends_at")
        if self.effective_from > self.effective_to:
            raise ValueError("effective_from must be on or before effective_to")
        return self


class ScheduleUpdate(BaseModel):
    teacher_user_id: uuid.UUID | None = None
    room_id: uuid.UUID | None = None
    weekday: int | None = Field(default=None, ge=0, le=6)
    starts_at: time | None = None
    ends_at: time | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    timezone_name: str | None = Field(default=None, min_length=1, max_length=64)


class ScheduleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    section_id: uuid.UUID
    course_id: uuid.UUID | None
    semester_id: uuid.UUID | None
    teacher_user_id: uuid.UUID
    room_id: uuid.UUID | None
    weekday: int
    starts_at: time
    ends_at: time
    effective_from: date
    effective_to: date
    timezone_name: str
    status: str
    version: int
    created_by_user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class OverrideCreate(BaseModel):
    occurrence_date: date
    kind: str
    starts_at: time | None = None
    ends_at: time | None = None
    room_id: uuid.UUID | None = None
    reason: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_override(self):
        kind = self.kind.upper()
        if kind not in {"CANCELLED", "RESCHEDULED"}:
            raise ValueError("kind must be CANCELLED or RESCHEDULED")
        self.kind = kind
        if kind == "RESCHEDULED":
            if self.starts_at is None or self.ends_at is None:
                raise ValueError("RESCHEDULED override requires starts_at and ends_at")
            if self.starts_at >= self.ends_at:
                raise ValueError("starts_at must be earlier than ends_at")
        return self


class OverrideOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    schedule_id: uuid.UUID
    occurrence_date: date
    kind: str
    starts_at: time | None
    ends_at: time | None
    room_id: uuid.UUID | None
    reason: str | None
    created_by_user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class OccurrenceOut(BaseModel):
    occurrence_id: uuid.UUID
    schedule_id: uuid.UUID
    occurrence_date: date
    section_id: uuid.UUID
    course_id: uuid.UUID | None
    semester_id: uuid.UUID | None
    teacher_user_id: uuid.UUID
    room_id: uuid.UUID | None
    starts_at: time
    ends_at: time
    timezone_name: str
    source: str


class AuditOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    schedule_id: uuid.UUID | None
    action: str
    actor_user_id: uuid.UUID
    before_data: dict | None
    after_data: dict | None
    created_at: datetime


class CancelRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=500)

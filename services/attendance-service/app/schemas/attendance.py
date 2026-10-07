from __future__ import annotations

from datetime import UTC, date, datetime, time
from typing import Annotated, Any, Self
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

from app.domain.models import AttendanceStatus, SessionStatus

ReasonText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]
Notes = Annotated[str, StringConstraints(max_length=2000)]


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SessionTimes(Input):
    starts_at: time | None = None
    ends_at: time | None = None

    @field_validator("starts_at", "ends_at")
    @classmethod
    def civil_time(cls, value: time | None) -> time | None:
        if value and value.tzinfo is not None:
            raise ValueError("Use institution-local civil times without an offset.")
        return value


class SessionCreate(SessionTimes):
    section_id: UUID
    schedule_occurrence_id: UUID | None = None
    session_date: date

    @model_validator(mode="after")
    def valid_times(self) -> Self:
        if (self.starts_at is None) != (self.ends_at is None):
            raise ValueError("Provide both starts_at and ends_at, or neither.")
        if self.starts_at is not None and self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at.")
        return self


class SessionPatch(SessionTimes):
    reason: ReasonText

    @model_validator(mode="after")
    def has_changes(self) -> Self:
        if not self.model_fields_set.intersection({"starts_at", "ends_at"}):
            raise ValueError("Supply a session time change.")
        return self


class Reason(Input):
    reason: ReasonText


class RecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime
    updated_at: datetime

    @field_validator("*", mode="before")
    @classmethod
    def utc_timestamps(cls, value: Any) -> Any:
        if isinstance(value, datetime):
            return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)
        return value


class SessionRead(RecordRead):
    section_id: UUID
    course_id: UUID
    semester_id: UUID
    schedule_occurrence_id: UUID | None
    session_date: date
    starts_at: time | None
    ends_at: time | None
    created_by_user_id: UUID
    status: SessionStatus
    finalized_at: datetime | None
    finalized_by_user_id: UUID | None


class Mark(Input):
    student_user_id: UUID
    status: AttendanceStatus
    notes: Notes | None = None


class BulkMark(Input):
    records: list[Mark] = Field(min_length=1, max_length=1000)

    @model_validator(mode="after")
    def unique_students(self) -> Self:
        ids = [record.student_user_id for record in self.records]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate student_user_id in attendance payload.")
        return self


class Correction(Input):
    status: AttendanceStatus
    notes: Notes | None = None
    reason: ReasonText


class AttendanceRead(RecordRead):
    attendance_session_id: UUID
    student_user_id: UUID
    status: AttendanceStatus
    marked_by_user_id: UUID
    marked_at: datetime
    notes: str | None


class StudentAttendance(AttendanceRead):
    section_id: UUID
    course_id: UUID
    semester_id: UUID
    session_date: date
    session_status: SessionStatus


class CorrectionRead(RecordRead):
    attendance_record_id: UUID
    previous_status: AttendanceStatus
    new_status: AttendanceStatus
    previous_notes: str | None
    new_notes: str | None
    reason: str
    changed_by_user_id: UUID
    changed_at: datetime


class SessionHistoryRead(RecordRead):
    attendance_session_id: UUID
    action: str
    previous_values: dict
    new_values: dict
    reason: str
    changed_by_user_id: UUID
    changed_at: datetime


class Counts(BaseModel):
    present_sessions: int = 0
    absent_sessions: int = 0
    late_sessions: int = 0
    excused_sessions: int = 0
    total_considered_sessions: int = 0
    attendance_percentage: float | None = None
    is_low_attendance: bool = False


class AttendanceSummary(Counts):
    student_user_id: UUID | None = None
    section_id: UUID | None = None
    course_id: UUID | None = None


class StudentSummary(BaseModel):
    student_user_id: UUID
    totals: Counts
    by_section: list[AttendanceSummary]
    by_course: list[AttendanceSummary]
    limit: int
    offset: int

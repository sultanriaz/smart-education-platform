from __future__ import annotations

from datetime import date, datetime, time
from enum import StrEnum
from typing import Any
from uuid import UUID

from sqlalchemy import JSON, CheckConstraint, DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, Record


class SessionStatus(StrEnum):
    OPEN = "OPEN"
    FINALIZED = "FINALIZED"
    CANCELLED = "CANCELLED"


class AttendanceStatus(StrEnum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"
    EXCUSED = "EXCUSED"


class AttendanceSession(Record, Base):
    __tablename__ = "attendance_sessions"
    __table_args__ = (
        UniqueConstraint("section_id", "session_date", "schedule_occurrence_id"),
        CheckConstraint("status IN ('OPEN','FINALIZED','CANCELLED')", name="valid_status"),
        CheckConstraint(
            "(starts_at IS NULL AND ends_at IS NULL) OR "
            "(starts_at IS NOT NULL AND ends_at IS NOT NULL AND ends_at > starts_at)",
            name="time_range",
        ),
        CheckConstraint(
            "(status = 'FINALIZED' AND finalized_at IS NOT NULL "
            "AND finalized_by_user_id IS NOT NULL) OR (status != 'FINALIZED' "
            "AND finalized_at IS NULL AND finalized_by_user_id IS NULL)",
            name="finalization_metadata",
        ),
        Index("ix_attendance_sessions_section_date", "section_id", "session_date"),
    )
    section_id: Mapped[UUID]
    course_id: Mapped[UUID] = mapped_column(index=True)
    semester_id: Mapped[UUID] = mapped_column(index=True)
    schedule_occurrence_id: Mapped[UUID | None]
    session_date: Mapped[date]
    starts_at: Mapped[time | None]
    ends_at: Mapped[time | None]
    created_by_user_id: Mapped[UUID]
    status: Mapped[str] = mapped_column(
        String(16), default=SessionStatus.OPEN, server_default="OPEN"
    )
    finalized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finalized_by_user_id: Mapped[UUID | None]


# SQL NULLs are distinct in ordinary uniqueness constraints. This index closes the
# unscheduled-session race on both PostgreSQL and SQLite without a sentinel UUID.
Index(
    "uq_attendance_sessions_unscheduled",
    AttendanceSession.section_id,
    AttendanceSession.session_date,
    unique=True,
    postgresql_where=AttendanceSession.schedule_occurrence_id.is_(None),
    sqlite_where=AttendanceSession.schedule_occurrence_id.is_(None),
)


class AttendanceRecord(Record, Base):
    __tablename__ = "attendance_records"
    __table_args__ = (
        UniqueConstraint("attendance_session_id", "student_user_id"),
        CheckConstraint("status IN ('PRESENT','ABSENT','LATE','EXCUSED')", name="valid_status"),
    )
    attendance_session_id: Mapped[UUID] = mapped_column(
        ForeignKey("attendance_sessions.id", ondelete="RESTRICT"), index=True
    )
    student_user_id: Mapped[UUID] = mapped_column(index=True)
    status: Mapped[str] = mapped_column(String(16))
    marked_by_user_id: Mapped[UUID]
    marked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(String(2000))


class AttendanceCorrection(Record, Base):
    __tablename__ = "attendance_corrections"
    __table_args__ = (
        CheckConstraint(
            "previous_status IN ('PRESENT','ABSENT','LATE','EXCUSED')", name="old_status"
        ),
        CheckConstraint("new_status IN ('PRESENT','ABSENT','LATE','EXCUSED')", name="new_status"),
        CheckConstraint("length(trim(reason)) > 0", name="reason_required"),
    )
    attendance_record_id: Mapped[UUID] = mapped_column(
        ForeignKey("attendance_records.id", ondelete="RESTRICT"), index=True
    )
    previous_status: Mapped[str] = mapped_column(String(16))
    new_status: Mapped[str] = mapped_column(String(16))
    previous_notes: Mapped[str | None] = mapped_column(String(2000))
    new_notes: Mapped[str | None] = mapped_column(String(2000))
    reason: Mapped[str] = mapped_column(String(1000))
    changed_by_user_id: Mapped[UUID]
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class SessionHistory(Record, Base):
    __tablename__ = "attendance_session_history"
    __table_args__ = (CheckConstraint("length(trim(reason)) > 0", name="reason_required"),)
    attendance_session_id: Mapped[UUID] = mapped_column(
        ForeignKey("attendance_sessions.id", ondelete="RESTRICT"), index=True
    )
    action: Mapped[str] = mapped_column(String(32))
    previous_values: Mapped[dict[str, Any]] = mapped_column(JSON)
    new_values: Mapped[dict[str, Any]] = mapped_column(JSON)
    reason: Mapped[str] = mapped_column(String(1000))
    changed_by_user_id: Mapped[UUID]
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class OutboxEvent(Record, Base):
    __tablename__ = "outbox_events"
    __table_args__ = (
        CheckConstraint("attempts >= 0", name="nonnegative_attempts"),
        Index("ix_outbox_events_pending", "published_at", "available_at", "locked_until"),
    )
    aggregate_id: Mapped[UUID] = mapped_column(index=True)
    event_type: Mapped[str] = mapped_column(String(100))
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    claimed_by: Mapped[str | None] = mapped_column(String(100))
    attempts: Mapped[int] = mapped_column(default=0, server_default="0")
    last_error: Mapped[str | None] = mapped_column(String(2000))

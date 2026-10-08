from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Float,
    Integer,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), unique=True, index=True)
    source_service: Mapped[str] = mapped_column(String(80), index=True)
    event_type: Mapped[str] = mapped_column(String(160), index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )
    processed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)


class AttendanceProjection(Base):
    __tablename__ = "attendance_projection"
    __table_args__ = (
        UniqueConstraint(
            "attendance_session_id", "student_user_id", name="uq_attendance_session_student"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attendance_session_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    student_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    section_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    course_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(String(24), index=True)
    session_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class AssessmentProjection(Base):
    __tablename__ = "assessment_projection"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attempt_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), unique=True, index=True)
    student_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    quiz_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True, index=True)
    section_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True, index=True
    )
    course_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True, index=True
    )
    percent: Mapped[float] = mapped_column(Float)
    passed: Mapped[bool] = mapped_column(Boolean, index=True)
    graded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class FacilityBookingProjection(Base):
    __tablename__ = "facility_booking_projection"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), unique=True, index=True)
    facility_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    requested_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(String(32), index=True)
    starts_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class NotificationDeliveryProjection(Base):
    __tablename__ = "notification_delivery_projection"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    delivery_id: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    notification_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True, index=True
    )
    channel: Mapped[str] = mapped_column(String(32), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class ScheduleActivityProjection(Base):
    __tablename__ = "schedule_activity_projection"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_event_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), unique=True, index=True)
    section_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True, index=True
    )
    teacher_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True, index=True
    )
    room_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True, index=True)
    activity_type: Mapped[str] = mapped_column(String(80), index=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class EnrollmentProjection(Base):
    __tablename__ = "enrollment_projection"
    __table_args__ = (
        UniqueConstraint("student_user_id", "section_id", name="uq_reporting_student_section"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    section_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    program_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(String(32), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class ReportSnapshot(Base):
    __tablename__ = "report_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_type: Mapped[str] = mapped_column(String(80), index=True)
    filters: Mapped[dict] = mapped_column(JSON, default=dict)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    generated_by_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )


class ExportAudit(Base):
    __tablename__ = "export_audits"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_type: Mapped[str] = mapped_column(String(80), index=True)
    format: Mapped[str] = mapped_column(String(16))
    generated_by_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    row_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )

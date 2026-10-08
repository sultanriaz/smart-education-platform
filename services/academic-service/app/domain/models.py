from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from uuid import UUID

from smartedu_infra.runtime import RelayState
from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, Record


class EnrollmentStatus(StrEnum):
    ENROLLED = "enrolled"
    DROPPED = "dropped"
    COMPLETED = "completed"


class Department(Record, Base):
    __tablename__ = "departments"
    code: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(200))


class Program(Record, Base):
    __tablename__ = "programs"
    __table_args__ = (CheckConstraint("duration_semesters > 0", name="positive_duration"),)
    department_id: Mapped[UUID] = mapped_column(ForeignKey("departments.id"), index=True)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    duration_semesters: Mapped[int]


class AcademicYear(Record, Base):
    __tablename__ = "academic_years"
    __table_args__ = (CheckConstraint("ends_on > starts_on", name="date_range"),)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    starts_on: Mapped[date]
    ends_on: Mapped[date]


class Semester(Record, Base):
    __tablename__ = "semesters"
    __table_args__ = (
        UniqueConstraint("academic_year_id", "number"),
        CheckConstraint("number > 0", name="positive_number"),
        CheckConstraint("ends_on > starts_on", name="date_range"),
    )
    academic_year_id: Mapped[UUID] = mapped_column(ForeignKey("academic_years.id"), index=True)
    number: Mapped[int]
    name: Mapped[str] = mapped_column(String(200))
    starts_on: Mapped[date]
    ends_on: Mapped[date]


class Course(Record, Base):
    __tablename__ = "courses"
    __table_args__ = (
        CheckConstraint("credits > 0", name="positive_credits"),
        CheckConstraint("semester_number > 0", name="positive_semester"),
    )
    program_id: Mapped[UUID] = mapped_column(ForeignKey("programs.id"), index=True)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    title: Mapped[str] = mapped_column(String(200))
    credits: Mapped[int]
    semester_number: Mapped[int]


class Section(Record, Base):
    __tablename__ = "sections"
    __table_args__ = (
        UniqueConstraint("course_id", "semester_id", "code"),
        CheckConstraint("capacity > 0", name="positive_capacity"),
    )
    course_id: Mapped[UUID] = mapped_column(ForeignKey("courses.id"), index=True)
    semester_id: Mapped[UUID] = mapped_column(ForeignKey("semesters.id"), index=True)
    code: Mapped[str] = mapped_column(String(32))
    capacity: Mapped[int]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))


class StudentAcademicProfile(Record, Base):
    __tablename__ = "student_academic_profiles"
    __table_args__ = (CheckConstraint("current_semester > 0", name="positive_semester"),)
    external_user_id: Mapped[UUID] = mapped_column(unique=True)
    student_number: Mapped[str] = mapped_column(String(64), unique=True)
    program_id: Mapped[UUID] = mapped_column(ForeignKey("programs.id"), index=True)
    admission_year_id: Mapped[UUID] = mapped_column(ForeignKey("academic_years.id"), index=True)
    current_semester: Mapped[int]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))


class TeacherAcademicProfile(Record, Base):
    __tablename__ = "teacher_academic_profiles"
    external_user_id: Mapped[UUID] = mapped_column(unique=True)
    employee_number: Mapped[str] = mapped_column(String(64), unique=True)
    department_id: Mapped[UUID] = mapped_column(ForeignKey("departments.id"), index=True)
    designation: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))


class Enrollment(Record, Base):
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("student_profile_id", "section_id"),
        CheckConstraint("status IN ('enrolled', 'dropped', 'completed')", name="valid_status"),
    )
    student_profile_id: Mapped[UUID] = mapped_column(
        ForeignKey("student_academic_profiles.id"), index=True
    )
    section_id: Mapped[UUID] = mapped_column(ForeignKey("sections.id"), index=True)
    status: Mapped[str] = mapped_column(
        String(16), default=EnrollmentStatus.ENROLLED, server_default="enrolled"
    )


class TeacherAssignment(Record, Base):
    __tablename__ = "teacher_assignments"
    __table_args__ = (UniqueConstraint("teacher_profile_id", "section_id"),)
    teacher_profile_id: Mapped[UUID] = mapped_column(
        ForeignKey("teacher_academic_profiles.id"), index=True
    )
    section_id: Mapped[UUID] = mapped_column(ForeignKey("sections.id"), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))


class OutboxEvent(RelayState, Record, Base):
    __tablename__ = "outbox_events"
    event_type: Mapped[str] = mapped_column(String(160), index=True)
    aggregate_id: Mapped[UUID] = mapped_column(index=True)
    payload: Mapped[dict] = mapped_column(JSON)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )

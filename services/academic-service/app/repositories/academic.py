from __future__ import annotations

from typing import Any, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.domain.models import (
    Enrollment,
    EnrollmentStatus,
    Section,
    StudentAcademicProfile,
    TeacherAcademicProfile,
    TeacherAssignment,
)

Model = TypeVar("Model", bound=Base)


class AcademicRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, model: type[Model], record_id: UUID, *, lock: bool = False) -> Model | None:
        query = select(model).where(model.id == record_id)
        if lock:
            query = query.with_for_update().execution_options(populate_existing=True)
        return self.db.scalar(query)

    def list(
        self, model: type[Model], *, limit: int, offset: int, filters: dict[str, Any] | None = None
    ) -> list[Model]:
        query = select(model).filter_by(**(filters or {})).order_by(model.created_at, model.id)
        return list(self.db.scalars(query.limit(limit).offset(offset)))

    def add(self, record: Model) -> Model:
        self.db.add(record)
        self.db.flush()
        return record

    def delete(self, record: Base) -> None:
        self.db.delete(record)
        self.db.flush()

    def count(self, model: type[Base], *conditions: Any) -> int:
        return self.db.scalar(select(func.count()).select_from(model).where(*conditions)) or 0

    def enrollment_count(self, section_id: UUID) -> int:
        return (
            self.db.scalar(
                select(func.count())
                .select_from(Enrollment)
                .where(
                    Enrollment.section_id == section_id,
                    Enrollment.status == EnrollmentStatus.ENROLLED,
                )
            )
            or 0
        )

    def course_enrollment(
        self, student_id: UUID, section: Section, *, exclude: UUID | None = None
    ) -> Enrollment | None:
        query = (
            select(Enrollment)
            .join(Section)
            .where(
                Enrollment.student_profile_id == student_id,
                Section.course_id == section.course_id,
                Section.semester_id == section.semester_id,
                Enrollment.status != EnrollmentStatus.DROPPED,
            )
        )
        if exclude is not None:
            query = query.where(Enrollment.id != exclude)
        return self.db.scalar(query)

    def teacher_profile(self, user_id: UUID) -> TeacherAcademicProfile | None:
        return self.db.scalar(
            select(TeacherAcademicProfile).where(
                TeacherAcademicProfile.external_user_id == user_id,
                TeacherAcademicProfile.is_active.is_(True),
            )
        )

    def teacher_has_section(self, user_id: UUID, section_id: UUID) -> bool:
        return (
            self.db.scalar(
                select(TeacherAssignment.id)
                .join(TeacherAcademicProfile)
                .where(
                    TeacherAcademicProfile.external_user_id == user_id,
                    TeacherAcademicProfile.is_active.is_(True),
                    TeacherAssignment.section_id == section_id,
                    TeacherAssignment.is_active.is_(True),
                )
            )
            is not None
        )

    def teacher_sections(self, user_id: UUID, *, limit: int, offset: int) -> list[Section]:
        query = (
            select(Section)
            .join(TeacherAssignment)
            .join(TeacherAcademicProfile)
            .where(
                TeacherAcademicProfile.external_user_id == user_id,
                TeacherAcademicProfile.is_active.is_(True),
                TeacherAssignment.is_active.is_(True),
            )
            .order_by(Section.created_at, Section.id)
        )
        return list(self.db.scalars(query.limit(limit).offset(offset)))

    def roster(self, section_id: UUID, *, limit: int, offset: int) -> list[Any]:
        query = (
            select(Enrollment.id, StudentAcademicProfile)
            .join(StudentAcademicProfile)
            .where(
                Enrollment.section_id == section_id,
                Enrollment.status == EnrollmentStatus.ENROLLED,
            )
            .order_by(StudentAcademicProfile.student_number, StudentAcademicProfile.id)
        )
        return list(self.db.execute(query.limit(limit).offset(offset)))

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.db.base import Base
from app.domain.models import (
    AcademicYear,
    Course,
    Department,
    Enrollment,
    EnrollmentStatus,
    Program,
    Section,
    Semester,
    StudentAcademicProfile,
    TeacherAcademicProfile,
    TeacherAssignment,
)
from app.repositories.academic import AcademicRepository, Model
from app.schemas.academic import RosterEntry, SectionRoster
from app.security.jwt import Principal
from app.services.transaction import transaction

# Parent links and external identities cannot be repointed by a replacement request.
IMMUTABLE_FIELDS: dict[type[Base], tuple[str, ...]] = {
    Program: ("department_id",),
    Semester: ("academic_year_id", "number"),
    Course: ("program_id", "semester_number"),
    Section: ("course_id", "semester_id"),
    StudentAcademicProfile: ("external_user_id", "program_id", "admission_year_id"),
    TeacherAcademicProfile: ("external_user_id", "department_id"),
}


class AcademicService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = AcademicRepository(db)

    def get(self, model: type[Model], record_id: UUID, *, lock: bool = False) -> Model:
        record = self.repo.get(model, record_id, lock=lock)
        if record is None:
            raise NotFoundError(model.__name__)
        return record

    def list(
        self, model: type[Model], *, limit: int, offset: int, filters: dict[str, Any] | None = None
    ) -> list[Model]:
        return self.repo.list(model, limit=limit, offset=offset, filters=filters)

    def create(self, model: type[Model], payload: BaseModel) -> Model:
        with transaction(self.db):
            values = payload.model_dump()
            self._validate(model, values)
            record = self.repo.add(model(**values))
        return record

    def replace(self, model: type[Model], record_id: UUID, payload: BaseModel) -> Model:
        with transaction(self.db):
            record = self.get(model, record_id, lock=True)
            values = payload.model_dump()
            for field in IMMUTABLE_FIELDS.get(model, ()):
                if values[field] != getattr(record, field):
                    raise ConflictError(f"{field} cannot be changed on an existing record.")
            self._validate(model, values, record_id=record_id)
            for field, value in values.items():
                setattr(record, field, value)
            self.db.flush()
        return record

    def delete(self, model: type[Base], record_id: UUID) -> None:
        with transaction(self.db):
            # All enrollment mutations acquire the section lock before the student lock.
            if model is Enrollment:
                existing = self.get(Enrollment, record_id)
                self.get(Section, existing.section_id, lock=True)
                self.get(StudentAcademicProfile, existing.student_profile_id, lock=True)
            self.repo.delete(self.get(model, record_id, lock=True))

    def _validate(
        self, model: type[Base], values: dict[str, Any], *, record_id: UUID | None = None
    ) -> None:
        if model is Program:
            self.get(Department, values["department_id"])
            if record_id and (
                self.repo.count(
                    Course,
                    Course.program_id == record_id,
                    Course.semester_number > values["duration_semesters"],
                )
                or self.repo.count(
                    StudentAcademicProfile,
                    StudentAcademicProfile.program_id == record_id,
                    StudentAcademicProfile.current_semester > values["duration_semesters"],
                )
            ):
                raise ConflictError("Program duration cannot exclude existing courses or students.")
        elif model is AcademicYear:
            if record_id and self.repo.count(
                Semester,
                Semester.academic_year_id == record_id,
                (Semester.starts_on < values["starts_on"]) | (Semester.ends_on > values["ends_on"]),
            ):
                raise ConflictError("Academic year dates must include all of its semesters.")
        elif model is Semester:
            year = self.get(AcademicYear, values["academic_year_id"], lock=True)
            if values["starts_on"] < year.starts_on or values["ends_on"] > year.ends_on:
                raise ConflictError("Semester dates must be within its academic year.")
        elif model is Course:
            program = self.get(Program, values["program_id"], lock=True)
            if values["semester_number"] > program.duration_semesters:
                raise ConflictError("Course semester exceeds the program duration.")
        elif model is Section:
            self.get(Course, values["course_id"])
            self.get(Semester, values["semester_id"])
            if record_id and values["capacity"] < self.repo.enrollment_count(record_id):
                raise ConflictError("Section capacity cannot be below its active enrollment count.")
        elif model is StudentAcademicProfile:
            program = self.get(Program, values["program_id"], lock=True)
            self.get(AcademicYear, values["admission_year_id"])
            if values["current_semester"] > program.duration_semesters:
                raise ConflictError("Student semester exceeds the program duration.")
            if record_id and self.repo.count(
                Enrollment,
                Enrollment.student_profile_id == record_id,
                Enrollment.status == EnrollmentStatus.ENROLLED,
            ):
                previous = self.get(StudentAcademicProfile, record_id)
                if (
                    not values["is_active"]
                    or values["current_semester"] != previous.current_semester
                ):
                    raise ConflictError(
                        "Resolve active enrollments before advancing or deactivating."
                    )
        elif model is TeacherAcademicProfile:
            self.get(Department, values["department_id"])
            if (
                record_id
                and not values["is_active"]
                and self.repo.count(
                    TeacherAssignment,
                    TeacherAssignment.teacher_profile_id == record_id,
                    TeacherAssignment.is_active.is_(True),
                )
            ):
                raise ConflictError(
                    "Deactivate teacher assignments before deactivating the profile."
                )

    def enroll(self, student_id: UUID, section_id: UUID) -> Enrollment:
        with transaction(self.db):
            section = self.get(Section, section_id, lock=True)
            student = self.get(StudentAcademicProfile, student_id, lock=True)
            self._validate_enrollment(student, section)
            record = self.repo.add(Enrollment(student_profile_id=student_id, section_id=section_id))
        return record

    def _validate_enrollment(
        self, student: StudentAcademicProfile, section: Section, *, exclude: UUID | None = None
    ) -> None:
        course = self.get(Course, section.course_id)
        if not student.is_active or not section.is_active:
            raise ConflictError("Only active students can enroll in active sections.")
        if student.program_id != course.program_id:
            raise ConflictError("Student and course must belong to the same program.")
        if student.current_semester != course.semester_number:
            raise ConflictError("Course must match the student's current curriculum semester.")
        admission = self.get(AcademicYear, student.admission_year_id)
        semester = self.get(Semester, section.semester_id)
        if semester.starts_on < admission.starts_on:
            raise ConflictError("Section semester cannot precede the student's admission year.")
        if self.repo.course_enrollment(student.id, section, exclude=exclude):
            raise ConflictError("Student is already enrolled in this course for this semester.")
        if self.repo.enrollment_count(section.id) >= section.capacity:
            raise ConflictError("Section has reached its capacity.")

    def set_enrollment_status(self, record_id: UUID, status: EnrollmentStatus) -> Enrollment:
        with transaction(self.db):
            existing = self.get(Enrollment, record_id)
            section = self.get(Section, existing.section_id, lock=True)
            student = self.get(StudentAcademicProfile, existing.student_profile_id, lock=True)
            record = self.get(Enrollment, record_id, lock=True)
            if record.status != status:
                if record.status == EnrollmentStatus.COMPLETED:
                    raise ConflictError("Completed enrollment is final.")
                if (
                    status == EnrollmentStatus.COMPLETED
                    and record.status != EnrollmentStatus.ENROLLED
                ):
                    raise ConflictError("Only an enrolled student can complete a course.")
                if status == EnrollmentStatus.ENROLLED:
                    self._validate_enrollment(student, section, exclude=record_id)
                record.status = status
                self.db.flush()
        return record

    def assign(self, teacher_id: UUID, section_id: UUID) -> TeacherAssignment:
        with transaction(self.db):
            section = self.get(Section, section_id, lock=True)
            teacher = self.get(TeacherAcademicProfile, teacher_id, lock=True)
            self._validate_assignment(teacher, section)
            record = self.repo.add(
                TeacherAssignment(
                    teacher_profile_id=teacher_id,
                    section_id=section_id,
                )
            )
        return record

    def _validate_assignment(self, teacher: TeacherAcademicProfile, section: Section) -> None:
        course = self.get(Course, section.course_id)
        program = self.get(Program, course.program_id)
        if not teacher.is_active or not section.is_active:
            raise ConflictError("Only active teachers can be assigned to active sections.")
        if teacher.department_id != program.department_id:
            raise ConflictError("Teacher and course must belong to the same department.")

    def set_assignment_active(self, record_id: UUID, is_active: bool) -> TeacherAssignment:
        with transaction(self.db):
            existing = self.get(TeacherAssignment, record_id)
            section = self.get(Section, existing.section_id, lock=True)
            teacher = self.get(TeacherAcademicProfile, existing.teacher_profile_id, lock=True)
            record = self.get(TeacherAssignment, record_id, lock=True)
            if is_active:
                self._validate_assignment(teacher, section)
            record.is_active = is_active
            self.db.flush()
        return record

    def teacher_profile(self, principal: Principal) -> TeacherAcademicProfile:
        profile = self.repo.teacher_profile(principal.user_id)
        if profile is None:
            raise NotFoundError("Active teacher academic profile")
        return profile

    def check_section_access(self, principal: Principal, section_id: UUID) -> None:
        if not principal.is_admin and not self.repo.teacher_has_section(
            principal.user_id, section_id
        ):
            raise ForbiddenError()
        self.get(Section, section_id)

    def sections(self, principal: Principal, *, limit: int, offset: int) -> list[Section]:
        if principal.is_admin:
            return self.list(Section, limit=limit, offset=offset)
        return self.repo.teacher_sections(principal.user_id, limit=limit, offset=offset)

    def assignments(
        self, principal: Principal, *, limit: int, offset: int
    ) -> list[TeacherAssignment]:
        if principal.is_admin:
            return self.list(TeacherAssignment, limit=limit, offset=offset)
        profile = self.teacher_profile(principal)
        return self.list(
            TeacherAssignment,
            limit=limit,
            offset=offset,
            filters={
                "teacher_profile_id": profile.id,
                "is_active": True,
            },
        )

    def assignment(self, principal: Principal, record_id: UUID) -> TeacherAssignment:
        record = self.get(TeacherAssignment, record_id)
        if not principal.is_admin:
            profile = self.teacher_profile(principal)
            if record.teacher_profile_id != profile.id or not record.is_active:
                raise ForbiddenError()
        return record

    def roster(
        self, principal: Principal, section_id: UUID, *, limit: int, offset: int
    ) -> SectionRoster:
        self.check_section_access(principal, section_id)
        return SectionRoster(
            section_id=section_id,
            total=self.repo.enrollment_count(section_id),
            limit=limit,
            offset=offset,
            students=[
                RosterEntry(
                    enrollment_id=enrollment_id,
                    student_profile_id=student.id,
                    external_user_id=student.external_user_id,
                    student_number=student.student_number,
                )
                for enrollment_id, student in self.repo.roster(
                    section_id, limit=limit, offset=offset
                )
            ],
        )

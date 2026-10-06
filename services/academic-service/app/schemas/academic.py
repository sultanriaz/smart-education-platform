from __future__ import annotations

from datetime import date, datetime
from typing import Annotated, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from app.domain.models import EnrollmentStatus

Code = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=32)]
Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Identifier = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=64)]
PositiveInt = Annotated[int, Field(gt=0, le=10000)]


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime
    updated_at: datetime


class DepartmentWrite(Input):
    code: Code
    name: Name


class DepartmentRead(DepartmentWrite, RecordRead):
    pass


class ProgramWrite(DepartmentWrite):
    department_id: UUID
    duration_semesters: PositiveInt


class ProgramRead(ProgramWrite, RecordRead):
    pass


class DateRange(Input):
    starts_on: date
    ends_on: date

    @model_validator(mode="after")
    def valid_dates(self) -> Self:
        if self.ends_on <= self.starts_on:
            raise ValueError("ends_on must be after starts_on.")
        return self


class AcademicYearWrite(DepartmentWrite, DateRange):
    pass


class AcademicYearRead(AcademicYearWrite, RecordRead):
    pass


class SemesterWrite(DateRange):
    academic_year_id: UUID
    number: PositiveInt
    name: Name


class SemesterRead(SemesterWrite, RecordRead):
    pass


class CourseWrite(Input):
    program_id: UUID
    code: Code
    title: Name
    credits: Annotated[int, Field(gt=0, le=30)]
    semester_number: PositiveInt


class CourseRead(CourseWrite, RecordRead):
    pass


class SectionWrite(Input):
    course_id: UUID
    semester_id: UUID
    code: Code
    capacity: PositiveInt
    is_active: bool = True


class SectionRead(SectionWrite, RecordRead):
    pass


class StudentProfileWrite(Input):
    external_user_id: UUID
    student_number: Identifier
    program_id: UUID
    admission_year_id: UUID
    current_semester: PositiveInt
    is_active: bool = True


class StudentProfileRead(StudentProfileWrite, RecordRead):
    pass


class TeacherProfileWrite(Input):
    external_user_id: UUID
    employee_number: Identifier
    department_id: UUID
    designation: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)
    ]
    is_active: bool = True


class TeacherProfileRead(TeacherProfileWrite, RecordRead):
    pass


class EnrollmentCreate(Input):
    student_profile_id: UUID
    section_id: UUID


class EnrollmentUpdate(Input):
    status: EnrollmentStatus


class EnrollmentRead(EnrollmentCreate, RecordRead):
    status: EnrollmentStatus


class AssignmentCreate(Input):
    teacher_profile_id: UUID
    section_id: UUID


class AssignmentUpdate(Input):
    is_active: bool


class AssignmentRead(AssignmentCreate, RecordRead):
    is_active: bool


class RosterEntry(BaseModel):
    enrollment_id: UUID
    student_profile_id: UUID
    external_user_id: UUID
    student_number: str


class SectionRoster(BaseModel):
    section_id: UUID
    total: int
    limit: int
    offset: int
    students: list[RosterEntry]

from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import func, select

from app.core.exceptions import ConflictError
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
from app.schemas.academic import (
    AcademicYearWrite,
    CourseWrite,
    DepartmentWrite,
    ProgramWrite,
    SectionWrite,
    SemesterWrite,
    StudentProfileWrite,
    TeacherProfileWrite,
)
from app.services.academic import AcademicService


def test_capacity_duplicate_and_restoration(db, academic):
    service = AcademicService(db)
    first = service.enroll(academic.students[0].id, academic.section.id)
    with pytest.raises(ConflictError):
        service.enroll(academic.students[0].id, academic.section.id)
    service.enroll(academic.students[1].id, academic.section.id)
    with pytest.raises(ConflictError, match="capacity"):
        service.enroll(academic.students[2].id, academic.section.id)
    service.set_enrollment_status(first.id, EnrollmentStatus.DROPPED)
    service.enroll(academic.students[2].id, academic.section.id)
    with pytest.raises(ConflictError, match="capacity"):
        service.set_enrollment_status(first.id, EnrollmentStatus.ENROLLED)
    assert service.get(Enrollment, first.id).status == "dropped"
    assert service.repo.enrollment_count(academic.section.id) == 2


def test_duplicate_course_across_sections(db, academic):
    service = AcademicService(db)
    section = service.create(
        Section,
        SectionWrite(
            course_id=academic.course.id,
            semester_id=academic.semester.id,
            code="B",
            capacity=10,
        ),
    )
    first = service.enroll(academic.students[0].id, academic.section.id)
    with pytest.raises(ConflictError, match="already enrolled"):
        service.enroll(academic.students[0].id, section.id)
    service.set_enrollment_status(first.id, EnrollmentStatus.DROPPED)
    service.enroll(academic.students[0].id, section.id)


def test_enrollment_status_transitions(db, academic):
    service = AcademicService(db)
    enrollment = service.enroll(academic.students[0].id, academic.section.id)
    service.set_enrollment_status(enrollment.id, EnrollmentStatus.DROPPED)
    with pytest.raises(ConflictError):
        service.set_enrollment_status(enrollment.id, EnrollmentStatus.COMPLETED)
    service.set_enrollment_status(enrollment.id, EnrollmentStatus.ENROLLED)
    service.set_enrollment_status(enrollment.id, EnrollmentStatus.COMPLETED)
    assert service.repo.enrollment_count(academic.section.id) == 0
    assert (
        service.set_enrollment_status(enrollment.id, EnrollmentStatus.COMPLETED).status
        == "completed"
    )
    with pytest.raises(ConflictError, match="final"):
        service.set_enrollment_status(enrollment.id, EnrollmentStatus.ENROLLED)


def test_program_and_curriculum_compatibility(db, academic):
    service = AcademicService(db)
    second_program = service.create(
        Program,
        ProgramWrite(
            department_id=academic.department.id,
            code="BSSE",
            name="Software Engineering",
            duration_semesters=8,
        ),
    )
    student_payload = StudentProfileWrite.model_validate(academic.students[0], from_attributes=True)
    other_student = service.create(
        StudentAcademicProfile,
        student_payload.model_copy(
            update={
                "external_user_id": uuid4(),
                "student_number": "OTHER",
                "program_id": second_program.id,
            }
        ),
    )
    with pytest.raises(ConflictError, match="same program"):
        service.enroll(other_student.id, academic.section.id)
    service.replace(
        StudentAcademicProfile,
        academic.students[0].id,
        student_payload.model_copy(update={"current_semester": 2}),
    )
    with pytest.raises(ConflictError, match="curriculum semester"):
        service.enroll(academic.students[0].id, academic.section.id)


def test_inactive_profiles_and_sections(db, academic):
    service = AcademicService(db)
    profile = StudentProfileWrite.model_validate(academic.students[0], from_attributes=True)
    service.replace(
        StudentAcademicProfile,
        academic.students[0].id,
        profile.model_copy(update={"is_active": False}),
    )
    with pytest.raises(ConflictError, match="active students"):
        service.enroll(academic.students[0].id, academic.section.id)
    section = SectionWrite.model_validate(academic.section, from_attributes=True)
    service.replace(Section, academic.section.id, section.model_copy(update={"is_active": False}))
    with pytest.raises(ConflictError):
        service.assign(academic.teacher.id, academic.section.id)


def test_assignment_department_uniqueness_and_reactivation(db, academic):
    service = AcademicService(db)
    assignment = service.assign(academic.teacher.id, academic.section.id)
    with pytest.raises(ConflictError):
        service.assign(academic.teacher.id, academic.section.id)
    service.set_assignment_active(assignment.id, False)
    assert service.set_assignment_active(assignment.id, True).is_active
    other_department = service.create(Department, DepartmentWrite(code="EE", name="Engineering"))
    other_teacher = service.create(
        TeacherAcademicProfile,
        TeacherProfileWrite(
            external_user_id=uuid4(),
            employee_number="T2",
            department_id=other_department.id,
            designation="Lecturer",
        ),
    )
    with pytest.raises(ConflictError, match="same department"):
        service.assign(other_teacher.id, academic.section.id)


def test_prevent_invalid_parent_edits(db, academic):
    service = AcademicService(db)
    year = AcademicYearWrite.model_validate(academic.year, from_attributes=True)
    with pytest.raises(ConflictError, match="all of its semesters"):
        service.replace(
            AcademicYear,
            academic.year.id,
            year.model_copy(
                update={
                    "starts_on": academic.semester.ends_on,
                }
            ),
        )
    program = ProgramWrite.model_validate(academic.program, from_attributes=True)
    course = service.create(
        Course,
        CourseWrite(
            program_id=academic.program.id,
            code="CS801",
            title="Capstone",
            credits=3,
            semester_number=8,
        ),
    )
    with pytest.raises(ConflictError, match="duration"):
        service.replace(
            Program, academic.program.id, program.model_copy(update={"duration_semesters": 7})
        )
    assert course.semester_number == 8


def test_semester_and_course_bounds(db, academic):
    service = AcademicService(db)
    with pytest.raises(ConflictError, match="within"):
        service.create(
            Semester,
            SemesterWrite(
                academic_year_id=academic.year.id,
                number=2,
                name="Outside",
                starts_on="2027-08-01",
                ends_on="2027-12-31",
            ),
        )
    with pytest.raises(ConflictError, match="duration"):
        service.create(
            Course,
            CourseWrite(
                program_id=academic.program.id,
                code="CS999",
                title="Invalid",
                credits=3,
                semester_number=9,
            ),
        )


def test_capacity_and_profile_changes_protect_enrollments(db, academic):
    service = AcademicService(db)
    for student in academic.students[:2]:
        service.enroll(student.id, academic.section.id)
    section = SectionWrite.model_validate(academic.section, from_attributes=True)
    with pytest.raises(ConflictError, match="capacity"):
        service.replace(Section, academic.section.id, section.model_copy(update={"capacity": 1}))
    profile = StudentProfileWrite.model_validate(academic.students[0], from_attributes=True)
    for changes in ({"is_active": False}, {"current_semester": 2}, {"external_user_id": uuid4()}):
        with pytest.raises(ConflictError):
            service.replace(
                StudentAcademicProfile, academic.students[0].id, profile.model_copy(update=changes)
            )


def test_deactivation_requires_resolving_assignments(db, academic):
    service = AcademicService(db)
    assignment = service.assign(academic.teacher.id, academic.section.id)
    teacher = TeacherProfileWrite.model_validate(academic.teacher, from_attributes=True)
    with pytest.raises(ConflictError, match="assignments"):
        service.replace(
            TeacherAcademicProfile,
            academic.teacher.id,
            teacher.model_copy(update={"is_active": False}),
        )
    service.set_assignment_active(assignment.id, False)
    service.replace(
        TeacherAcademicProfile, academic.teacher.id, teacher.model_copy(update={"is_active": False})
    )
    with pytest.raises(ConflictError, match="active teachers"):
        service.set_assignment_active(assignment.id, True)


def test_failed_commit_rolls_back_enrollment(db, academic, monkeypatch):
    def fail_commit():
        raise RuntimeError("simulated commit failure")

    monkeypatch.setattr(db, "commit", fail_commit)
    with pytest.raises(RuntimeError, match="commit failure"):
        AcademicService(db).enroll(academic.students[0].id, academic.section.id)
    assert db.scalar(select(func.count()).select_from(Enrollment)) == 0


def test_failed_commit_rolls_back_assignment(db, academic, monkeypatch):
    def fail_commit():
        raise RuntimeError("simulated commit failure")

    monkeypatch.setattr(db, "commit", fail_commit)
    with pytest.raises(RuntimeError):
        AcademicService(db).assign(academic.teacher.id, academic.section.id)
    assert db.scalar(select(func.count()).select_from(TeacherAssignment)) == 0

from uuid import uuid4

import pytest
from pydantic import ValidationError
from sqlalchemy import select

from app.core.exceptions import ConflictError
from app.domain.models import Campus, Course, Department, Enrollment, Section, Semester, StudentAcademicProfile
from app.schemas.academic import (
    BulkEnrollmentCreate, CampusWrite, DepartmentWrite, CourseWrite,
    SectionWrite, SemesterWrite,
)
from app.services.academic import AcademicService


def test_campus_hierarchy_and_invalid_links(db):
    service = AcademicService(db)
    campus = service.create(Campus, CampusWrite(code="SWL", name="Sahiwal"))
    dep = service.create(Department, DepartmentWrite(code="MATH", name="Mathematics", campus_id=campus.id))
    assert dep.campus_id == campus.id
    campus = service.replace(Campus, campus.id, CampusWrite(code="SWL", name="Sahiwal", is_active=False))
    with pytest.raises(ConflictError):
        service.create(Department, DepartmentWrite(code="PHY", name="Physics", campus_id=campus.id))


def test_archived_course_and_inactive_term_block_new_sections_and_enrollments(db, academic):
    service = AcademicService(db)
    course = academic.course
    section = academic.section
    course.is_archived = True
    db.commit()
    with pytest.raises(ConflictError):
        service.enroll(academic.students[0].id, section.id)
    with pytest.raises(ConflictError):
        service.create(Section, SectionWrite(course_id=course.id, semester_id=section.semester_id, code="Z", capacity=2))
    course.is_archived = False
    term = db.get(Semester, section.semester_id)
    term.is_active = False
    db.commit()
    with pytest.raises(ConflictError):
        service.enroll(academic.students[0].id, section.id)


def test_bulk_enrollment_is_atomic_and_capacity_bounded(db, academic):
    service = AcademicService(db)
    student_ids = [s.id for s in academic.students]
    academic.section.capacity = len(student_ids)
    db.commit()
    payload = BulkEnrollmentCreate(section_id=academic.section.id, student_profile_ids=student_ids)
    created = service.bulk_enroll(payload.section_id, payload.student_profile_ids)
    assert len(created) == len(student_ids)
    assert {e.id for e in created} == {e.id for e in db.scalars(select(Enrollment)).all()}
    with pytest.raises((ConflictError, Exception)):
        service.bulk_enroll(payload.section_id, student_ids)
    assert len(db.scalars(select(Enrollment)).all()) == len(student_ids)
    with pytest.raises(ValidationError):
        BulkEnrollmentCreate(section_id=academic.section.id, student_profile_ids=[student_ids[0]] * 2)


def test_bulk_capacity_rolls_back_all(db, academic):
    service = AcademicService(db)
    ids = [s.id for s in academic.students]
    academic.section.capacity = 1
    db.commit()
    with pytest.raises(ConflictError):
        service.bulk_enroll(academic.section.id, ids)
    assert db.scalar(select(Enrollment.id)) is None

"""Read contracts for downstream services; all queries remain Academic-owned."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from smartedu_contracts import internal_auth_dependency
from sqlalchemy import select

from app.api.dependencies import Limit, Offset, Service
from app.domain.models import (
    Enrollment,
    EnrollmentStatus,
    Course,
    Program,
    TeacherAcademicProfile,
    Section,
    StudentAcademicProfile,
)
from app.schemas.academic import RosterEntry, SectionRead, SectionRoster
from app.security.dependencies import get_principal
from app.security.jwt import Principal
from app.sprint16 import internal_token_verifier

router = APIRouter(tags=["academic relationships"])
Actor = Annotated[Principal, Depends(get_principal)]
Internal = Annotated[
    object,
    Depends(
        internal_auth_dependency(
            internal_token_verifier(),
            audience="academic-service",
            required_scopes=("academic:relationships:read",),
        )
    ),
]


def student_sections(service, user_id):
    return list(
        service.db.scalars(
            select(Section)
            .join(Enrollment)
            .join(StudentAcademicProfile)
            .where(
                StudentAcademicProfile.external_user_id == user_id,
                StudentAcademicProfile.is_active.is_(True),
                Enrollment.status == EnrollmentStatus.ENROLLED,
                Section.is_active.is_(True),
            )
            .distinct()
            .order_by(Section.id)
        )
    )


def teacher_sections(service, user_id):
    return service.repo.teacher_sections(user_id, limit=1000, offset=0)


def check_subject(principal, user_id):
    if (not principal.is_admin and "academic.records.read" not in principal.permissions
            and principal.user_id != user_id):
        raise HTTPException(403, "You may only inspect your own academic relationships.")


@router.get("/teachers/{user_id}/sections/{section_id}/assignment")
def teacher_assignment(user_id: UUID, section_id: UUID, service: Service, principal: Actor):
    check_subject(principal, user_id)
    return {"assigned": service.repo.teacher_has_section(user_id, section_id)}


@router.get("/students/{user_id}/sections/{section_id}/enrollment")
def student_enrollment(user_id: UUID, section_id: UUID, service: Service, principal: Actor):
    check_subject(principal, user_id)
    return {
        "enrolled": any(section.id == section_id for section in student_sections(service, user_id))
    }


@router.get("/students/me/sections", response_model=list[SectionRead])
def my_sections(service: Service, principal: Actor):
    return [
        SectionRead.model_validate(section)
        for section in student_sections(service, principal.user_id)
    ]


@router.get("/students/{user_id}/sections")
def student_section_ids(user_id: UUID, service: Service, principal: Actor):
    check_subject(principal, user_id)
    return {"section_ids": [str(section.id) for section in student_sections(service, user_id)]}


@router.get("/teacher-assignments/validate")
def validate_assignment(
    teacher_user_id: UUID, section_id: UUID, service: Service, principal: Actor
):
    return teacher_assignment(teacher_user_id, section_id, service, principal)


@router.get("/enrollments/validate")
def validate_enrollment(
    student_user_id: UUID, section_id: UUID, service: Service, principal: Actor
):
    return student_enrollment(student_user_id, section_id, service, principal)


@router.get("/internal/access/students/{user_id}/targets")
def accessible_targets(user_id: UUID, service: Service, _internal: Internal):
    sections = student_sections(service, user_id)
    return {
        "section_ids": [str(section.id) for section in sections],
        "course_ids": sorted({str(section.course_id) for section in sections}),
    }


@router.get("/internal/access/{kind}/{user_id}/{target_kind}/{target_id}")
def internal_access(
    kind: str,
    user_id: UUID,
    target_kind: str,
    target_id: UUID,
    service: Service,
    _internal: Internal,
):
    if kind not in {"teachers", "students"} or target_kind not in {"courses", "sections"}:
        raise HTTPException(404, "Unknown relationship type.")
    sections = (
        teacher_sections(service, user_id)
        if kind == "teachers"
        else student_sections(service, user_id)
    )
    return {
        "allowed": any(
            (section.id if target_kind == "sections" else section.course_id) == target_id
            for section in sections
        )
    }


@router.get("/internal/sections/{section_id}/roster", response_model=SectionRoster)
def internal_roster(
    section_id: UUID, service: Service, _internal: Internal, limit: Limit = 100, offset: Offset = 0
):
    service.get(Section, section_id)
    return SectionRoster(
        section_id=section_id,
        total=service.repo.enrollment_count(section_id),
        limit=limit,
        offset=offset,
        students=[
            RosterEntry(
                enrollment_id=enrollment_id,
                student_profile_id=student.id,
                external_user_id=student.external_user_id,
                student_number=student.student_number,
            )
            for enrollment_id, student in service.repo.roster(
                section_id, limit=limit, offset=offset
            )
        ],
    )


@router.get("/internal/courses/{course_id}/members")
def course_members(
    course_id: UUID, service: Service, _internal: Internal, limit: Limit = 100, offset: Offset = 0
):
    query = (
        select(StudentAcademicProfile.external_user_id)
        .join(Enrollment)
        .join(Section)
        .where(
            Section.course_id == course_id,
            Section.is_active.is_(True),
            StudentAcademicProfile.is_active.is_(True),
            Enrollment.status == EnrollmentStatus.ENROLLED,
        )
        .distinct()
        .order_by(StudentAcademicProfile.external_user_id)
        .limit(limit)
        .offset(offset)
    )
    return {"student_user_ids": [str(user_id) for user_id in service.db.scalars(query)]}


@router.get("/internal/programs/{program_id}/members")
def program_members(program_id: UUID, service: Service, _internal: Internal,
                    limit: Limit = 100, offset: Offset = 0):
    # Membership is Academic-owned; inactive profiles never appear.
    service.get(Program, program_id)
    stmt = (select(StudentAcademicProfile.external_user_id)
            .where(StudentAcademicProfile.program_id == program_id,
                   StudentAcademicProfile.is_active.is_(True))
            .order_by(StudentAcademicProfile.external_user_id).limit(limit).offset(offset))
    return {"student_user_ids": [str(value) for value in service.db.scalars(stmt)]}


@router.get("/internal/departments/{department_id}/members")
def department_members(department_id: UUID, service: Service, _internal: Internal,
                       limit: Limit = 100, offset: Offset = 0):
    # Aggregate active students and staff; dedupe before paging deterministically.
    from app.domain.models import Department
    service.get(Department, department_id)
    students = (select(StudentAcademicProfile.external_user_id)
                .join(Program, StudentAcademicProfile.program_id == Program.id)
                .where(Program.department_id == department_id,
                       StudentAcademicProfile.is_active.is_(True)))
    teachers = (select(TeacherAcademicProfile.external_user_id)
                .where(TeacherAcademicProfile.department_id == department_id,
                       TeacherAcademicProfile.is_active.is_(True)))
    from sqlalchemy import union
    stmt = (union(students, teachers).order_by("external_user_id").limit(limit).offset(offset))
    return {"student_user_ids": [str(row[0]) for row in service.db.execute(stmt)]}

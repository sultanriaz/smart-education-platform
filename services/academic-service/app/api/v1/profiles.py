from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Response

from app.api.dependencies import Admin, Limit, Offset, Service, Staff
from app.domain.models import StudentAcademicProfile, TeacherAcademicProfile
from app.schemas.academic import (
    StudentProfileRead,
    StudentProfileWrite,
    TeacherProfileRead,
    TeacherProfileWrite,
)

router = APIRouter(tags=["profiles"])


@router.get("/teacher-profiles/me", response_model=TeacherProfileRead)
def my_teacher_profile(service: Service, principal: Staff) -> TeacherProfileRead:
    return TeacherProfileRead.model_validate(service.teacher_profile(principal))


@router.get("/student-profiles", response_model=list[StudentProfileRead])
def list_student_profiles(
    service: Service, _principal: Admin, limit: Limit = 50, offset: Offset = 0
) -> list[StudentProfileRead]:
    return [
        StudentProfileRead.model_validate(row)
        for row in service.list(StudentAcademicProfile, limit=limit, offset=offset)
    ]


@router.post("/student-profiles", response_model=StudentProfileRead, status_code=201)
def create_student_profiles(
    payload: StudentProfileWrite, service: Service, _admin: Admin
) -> StudentProfileRead:
    return StudentProfileRead.model_validate(service.create(StudentAcademicProfile, payload))


@router.get("/student-profiles/{record_id}", response_model=StudentProfileRead)
def get_student_profiles(
    record_id: UUID, service: Service, _principal: Admin
) -> StudentProfileRead:
    return StudentProfileRead.model_validate(service.get(StudentAcademicProfile, record_id))


@router.put("/student-profiles/{record_id}", response_model=StudentProfileRead)
def replace_student_profiles(
    record_id: UUID, payload: StudentProfileWrite, service: Service, _admin: Admin
) -> StudentProfileRead:
    return StudentProfileRead.model_validate(
        service.replace(StudentAcademicProfile, record_id, payload)
    )


@router.delete("/student-profiles/{record_id}", status_code=204)
def delete_student_profiles(record_id: UUID, service: Service, _admin: Admin) -> Response:
    service.delete(StudentAcademicProfile, record_id)
    return Response(status_code=204)


@router.get("/teacher-profiles", response_model=list[TeacherProfileRead])
def list_teacher_profiles(
    service: Service, _principal: Admin, limit: Limit = 50, offset: Offset = 0
) -> list[TeacherProfileRead]:
    return [
        TeacherProfileRead.model_validate(row)
        for row in service.list(TeacherAcademicProfile, limit=limit, offset=offset)
    ]


@router.post("/teacher-profiles", response_model=TeacherProfileRead, status_code=201)
def create_teacher_profiles(
    payload: TeacherProfileWrite, service: Service, _admin: Admin
) -> TeacherProfileRead:
    return TeacherProfileRead.model_validate(service.create(TeacherAcademicProfile, payload))


@router.get("/teacher-profiles/{record_id}", response_model=TeacherProfileRead)
def get_teacher_profiles(
    record_id: UUID, service: Service, _principal: Admin
) -> TeacherProfileRead:
    return TeacherProfileRead.model_validate(service.get(TeacherAcademicProfile, record_id))


@router.put("/teacher-profiles/{record_id}", response_model=TeacherProfileRead)
def replace_teacher_profiles(
    record_id: UUID, payload: TeacherProfileWrite, service: Service, _admin: Admin
) -> TeacherProfileRead:
    return TeacherProfileRead.model_validate(
        service.replace(TeacherAcademicProfile, record_id, payload)
    )


@router.delete("/teacher-profiles/{record_id}", status_code=204)
def delete_teacher_profiles(record_id: UUID, service: Service, _admin: Admin) -> Response:
    service.delete(TeacherAcademicProfile, record_id)
    return Response(status_code=204)


@router.post("/identity-reconciliation/{user_id}")
def reconcile_identity_account(user_id: UUID, service: Service, _admin: Admin) -> dict[str, int]:
    """Idempotent repair; never deletes academic history or Identity state."""
    return service.reconcile_identity(user_id)

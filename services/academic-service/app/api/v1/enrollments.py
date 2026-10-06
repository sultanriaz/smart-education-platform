from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Response

from app.api.dependencies import Admin, Limit, Offset, Service
from app.domain.models import Enrollment
from app.schemas.academic import EnrollmentCreate, EnrollmentRead, EnrollmentUpdate

router = APIRouter(prefix="/enrollments", tags=["enrollments"])


@router.get("", response_model=list[EnrollmentRead])
def list_enrollments(
    service: Service,
    _admin: Admin,
    student_profile_id: UUID | None = None,
    section_id: UUID | None = None,
    limit: Limit = 50,
    offset: Offset = 0,
) -> list[EnrollmentRead]:
    filters = {}
    if student_profile_id is not None:
        filters["student_profile_id"] = student_profile_id
    if section_id is not None:
        filters["section_id"] = section_id
    return [
        EnrollmentRead.model_validate(row)
        for row in service.list(
            Enrollment,
            limit=limit,
            offset=offset,
            filters=filters,
        )
    ]


@router.post("", response_model=EnrollmentRead, status_code=201)
def create_enrollment(payload: EnrollmentCreate, service: Service, _admin: Admin) -> EnrollmentRead:
    return EnrollmentRead.model_validate(
        service.enroll(payload.student_profile_id, payload.section_id)
    )


@router.get("/{record_id}", response_model=EnrollmentRead)
def get_enrollment(record_id: UUID, service: Service, _admin: Admin) -> EnrollmentRead:
    return EnrollmentRead.model_validate(service.get(Enrollment, record_id))


@router.patch("/{record_id}", response_model=EnrollmentRead)
def update_enrollment(
    record_id: UUID, payload: EnrollmentUpdate, service: Service, _admin: Admin
) -> EnrollmentRead:
    return EnrollmentRead.model_validate(service.set_enrollment_status(record_id, payload.status))


@router.delete("/{record_id}", status_code=204)
def delete_enrollment(record_id: UUID, service: Service, _admin: Admin) -> Response:
    service.delete(Enrollment, record_id)
    return Response(status_code=204)

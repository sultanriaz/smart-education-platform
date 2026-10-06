from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Response

from app.api.dependencies import Admin, Limit, Offset, Service, Staff
from app.domain.models import TeacherAssignment
from app.schemas.academic import AssignmentCreate, AssignmentRead, AssignmentUpdate

router = APIRouter(prefix="/teacher-assignments", tags=["teacher assignments"])


@router.get("", response_model=list[AssignmentRead])
def list_assignments(
    service: Service, principal: Staff, limit: Limit = 50, offset: Offset = 0
) -> list[AssignmentRead]:
    return [
        AssignmentRead.model_validate(row)
        for row in service.assignments(
            principal,
            limit=limit,
            offset=offset,
        )
    ]


@router.post("", response_model=AssignmentRead, status_code=201)
def create_assignment(payload: AssignmentCreate, service: Service, _admin: Admin) -> AssignmentRead:
    return AssignmentRead.model_validate(
        service.assign(payload.teacher_profile_id, payload.section_id)
    )


@router.get("/{record_id}", response_model=AssignmentRead)
def get_assignment(record_id: UUID, service: Service, principal: Staff) -> AssignmentRead:
    return AssignmentRead.model_validate(service.assignment(principal, record_id))


@router.patch("/{record_id}", response_model=AssignmentRead)
def update_assignment(
    record_id: UUID, payload: AssignmentUpdate, service: Service, _admin: Admin
) -> AssignmentRead:
    return AssignmentRead.model_validate(
        service.set_assignment_active(record_id, payload.is_active)
    )


@router.delete("/{record_id}", status_code=204)
def delete_assignment(record_id: UUID, service: Service, _admin: Admin) -> Response:
    service.delete(TeacherAssignment, record_id)
    return Response(status_code=204)

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Response

from app.api.dependencies import Admin, Limit, Offset, Service, Staff
from app.domain.models import Section
from app.schemas.academic import SectionRead, SectionRoster, SectionWrite

router = APIRouter(prefix="/sections", tags=["sections"])


@router.get("", response_model=list[SectionRead])
def list_sections(
    service: Service, principal: Staff, limit: Limit = 50, offset: Offset = 0
) -> list[SectionRead]:
    return [
        SectionRead.model_validate(row)
        for row in service.sections(
            principal,
            limit=limit,
            offset=offset,
        )
    ]


@router.post("", response_model=SectionRead, status_code=201)
def create_section(payload: SectionWrite, service: Service, _admin: Admin) -> SectionRead:
    return SectionRead.model_validate(service.create(Section, payload))


@router.get("/{section_id}", response_model=SectionRead)
def get_section(section_id: UUID, service: Service, principal: Staff) -> SectionRead:
    service.check_section_access(principal, section_id)
    return SectionRead.model_validate(service.get(Section, section_id))


@router.put("/{section_id}", response_model=SectionRead)
def replace_section(
    section_id: UUID, payload: SectionWrite, service: Service, _admin: Admin
) -> SectionRead:
    return SectionRead.model_validate(service.replace(Section, section_id, payload))


@router.delete("/{section_id}", status_code=204)
def delete_section(section_id: UUID, service: Service, _admin: Admin) -> Response:
    service.delete(Section, section_id)
    return Response(status_code=204)


@router.get("/{section_id}/roster", response_model=SectionRoster)
def section_roster(
    section_id: UUID, service: Service, principal: Staff, limit: Limit = 50, offset: Offset = 0
) -> SectionRoster:
    return service.roster(principal, section_id, limit=limit, offset=offset)

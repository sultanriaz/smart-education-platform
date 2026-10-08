from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import availability_service, facility_service
from app.db.session import get_db
from app.repositories.facility_repository import FacilityRepository
from app.schemas.availability import AvailabilityOut
from app.schemas.facility import (
    EquipmentCreate,
    EquipmentOut,
    FacilityCreate,
    FacilityDetailOut,
    FacilityEquipmentAssign,
    FacilityEquipmentOut,
    FacilityOut,
    FacilityUpdate,
)
from app.security.auth import Principal, get_current_principal
from app.security.authorization import require_roles
from app.services.availability_service import AvailabilityService
from app.services.facility_service import FacilityService

router = APIRouter(prefix="/facilities", tags=["Facilities"])


def detail(facility) -> FacilityDetailOut:
    base = FacilityOut.model_validate(facility).model_dump()
    equipment = [
        FacilityEquipmentOut(
            equipment_id=link.equipment_id,
            code=link.equipment.code,
            name=link.equipment.name,
            quantity=link.quantity,
        )
        for link in facility.equipment_links
    ]
    return FacilityDetailOut(**base, equipment=equipment)


@router.get("", response_model=list[FacilityOut])
def list_facilities(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    _principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
):
    return FacilityRepository(db).list_facilities(offset=offset, limit=limit, active_only=False)


@router.post("", response_model=FacilityOut, status_code=status.HTTP_201_CREATED)
def create_facility(
    payload: FacilityCreate,
    actor: Principal = Depends(require_roles("admin")),
    service: FacilityService = Depends(facility_service),
):
    return service.create_facility(payload, actor)


@router.get("/{facility_id}", response_model=FacilityDetailOut)
def get_facility(
    facility_id: uuid.UUID,
    _principal: Principal = Depends(get_current_principal),
    service: FacilityService = Depends(facility_service),
):
    return detail(service.get_facility(facility_id))


@router.patch("/{facility_id}", response_model=FacilityOut)
def update_facility(
    facility_id: uuid.UUID,
    payload: FacilityUpdate,
    actor: Principal = Depends(require_roles("admin")),
    service: FacilityService = Depends(facility_service),
):
    return service.update_facility(facility_id, payload, actor)


@router.get("/{facility_id}/availability", response_model=AvailabilityOut)
def availability(
    facility_id: uuid.UUID,
    starts_at: datetime,
    ends_at: datetime,
    _principal: Principal = Depends(get_current_principal),
    service: AvailabilityService = Depends(availability_service),
):
    return service.check(facility_id, starts_at, ends_at)


@router.put("/{facility_id}/equipment", response_model=FacilityEquipmentOut)
def assign_equipment(
    facility_id: uuid.UUID,
    payload: FacilityEquipmentAssign,
    _actor: Principal = Depends(require_roles("admin")),
    service: FacilityService = Depends(facility_service),
    db: Session = Depends(get_db),
):
    link = service.assign_equipment(facility_id, payload)
    equipment = FacilityRepository(db).get_equipment(payload.equipment_id)
    return FacilityEquipmentOut(
        equipment_id=link.equipment_id,
        code=equipment.code,
        name=equipment.name,
        quantity=link.quantity,
    )


equipment_router = APIRouter(prefix="/equipment", tags=["Equipment"])


@equipment_router.get("", response_model=list[EquipmentOut])
def list_equipment(
    _principal: Principal = Depends(get_current_principal), db: Session = Depends(get_db)
):
    return FacilityRepository(db).list_equipment()


@equipment_router.post("", response_model=EquipmentOut, status_code=status.HTTP_201_CREATED)
def create_equipment(
    payload: EquipmentCreate,
    _actor: Principal = Depends(require_roles("admin")),
    service: FacilityService = Depends(facility_service),
):
    return service.create_equipment(payload)

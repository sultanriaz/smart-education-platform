from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import booking_service
from app.db.session import get_db
from app.repositories.booking_repository import BookingRepository
from app.schemas.block import FacilityBlockCreate, FacilityBlockOut
from app.security.auth import Principal
from app.security.authorization import require_roles
from app.services.booking_service import BookingService

router = APIRouter(prefix="/blocks", tags=["Facility Blocks"])


@router.get("", response_model=list[FacilityBlockOut])
def list_blocks(
    facility_id: uuid.UUID | None = None,
    _actor: Principal = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    return BookingRepository(db).list_blocks(facility_id)


@router.post("", response_model=FacilityBlockOut, status_code=status.HTTP_201_CREATED)
def create_block(
    payload: FacilityBlockCreate,
    actor: Principal = Depends(require_roles("admin")),
    service: BookingService = Depends(booking_service),
):
    return service.create_block(payload, actor)


@router.post("/{block_id}/cancel", response_model=FacilityBlockOut)
def cancel_block(
    block_id: uuid.UUID,
    actor: Principal = Depends(require_roles("admin")),
    service: BookingService = Depends(booking_service),
):
    return service.cancel_block(block_id, actor)

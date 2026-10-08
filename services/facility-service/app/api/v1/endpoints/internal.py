from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import internal_reservation_service
from app.schemas.internal import ExternalReservationCreate, ExternalReservationOut
from app.security.internal import verify_internal_service_token
from app.services.internal_reservation_service import InternalReservationService

router = APIRouter(
    prefix="/internal/reservations",
    tags=["Internal Reservations"],
    dependencies=[Depends(verify_internal_service_token)],
)


@router.post("", response_model=ExternalReservationOut, status_code=status.HTTP_201_CREATED)
def create_external_reservation(
    payload: ExternalReservationCreate,
    service: InternalReservationService = Depends(internal_reservation_service),
):
    return service.create(payload)


@router.delete("/{source_service}/{source_reference_id}", response_model=ExternalReservationOut)
def cancel_external_reservation(
    source_service: str,
    source_reference_id: str,
    service: InternalReservationService = Depends(internal_reservation_service),
):
    return service.cancel(source_service, source_reference_id)

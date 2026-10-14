from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import booking_service
from app.db.session import get_db
from app.repositories.booking_repository import BookingRepository
from app.schemas.booking import (
    BookingCancel,
    BookingCreate,
    BookingDecision,
    BookingHistoryOut,
    BookingOut,
)
from app.security.auth import Principal, get_current_principal
from app.security.authorization import require_roles, require_permission
from app.services.booking_service import BookingService

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(
    payload: BookingCreate,
    actor: Principal = Depends(require_roles("student", "teacher", "admin")),
    service: BookingService = Depends(booking_service),
):
    return service.create_booking(payload, actor)


@router.get("", response_model=list[BookingOut])
def list_bookings(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    facility_id: uuid.UUID | None = None,
    booking_status: str | None = Query(default=None, alias="status"),
    actor: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
):
    requester = None if actor.can_review_bookings else actor.user_id
    return BookingRepository(db).list_bookings(
        offset=offset,
        limit=limit,
        requester_user_id=requester,
        facility_id=facility_id,
        status=booking_status.upper() if booking_status else None,
    )


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(
    booking_id: uuid.UUID,
    actor: Principal = Depends(get_current_principal),
    service: BookingService = Depends(booking_service),
):
    return service.get_booking_for_actor(booking_id, actor)


@router.post("/{booking_id}/approve", response_model=BookingOut)
def approve_booking(
    booking_id: uuid.UUID,
    payload: BookingDecision,
    actor: Principal = Depends(require_permission("facility.bookings.review")),
    service: BookingService = Depends(booking_service),
):
    return service.approve(booking_id, payload, actor)


@router.post("/{booking_id}/reject", response_model=BookingOut)
def reject_booking(
    booking_id: uuid.UUID,
    payload: BookingDecision,
    actor: Principal = Depends(require_permission("facility.bookings.review")),
    service: BookingService = Depends(booking_service),
):
    return service.reject(booking_id, payload, actor)


@router.post("/{booking_id}/cancel", response_model=BookingOut)
def cancel_booking(
    booking_id: uuid.UUID,
    payload: BookingCancel,
    actor: Principal = Depends(get_current_principal),
    service: BookingService = Depends(booking_service),
):
    return service.cancel(booking_id, payload, actor)


@router.get("/{booking_id}/history", response_model=list[BookingHistoryOut])
def booking_history(
    booking_id: uuid.UUID,
    actor: Principal = Depends(get_current_principal),
    service: BookingService = Depends(booking_service),
    db: Session = Depends(get_db),
):
    service.get_booking_for_actor(booking_id, actor)
    return BookingRepository(db).list_history(booking_id)

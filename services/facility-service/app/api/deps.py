from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.availability_service import AvailabilityService
from app.services.booking_service import BookingService
from app.services.facility_service import FacilityService
from app.services.internal_reservation_service import InternalReservationService


def facility_service(db: Session = Depends(get_db)) -> FacilityService:
    return FacilityService(db)


def booking_service(db: Session = Depends(get_db)) -> BookingService:
    return BookingService(db)


def availability_service(db: Session = Depends(get_db)) -> AvailabilityService:
    return AvailabilityService(db)


def internal_reservation_service(db: Session = Depends(get_db)) -> InternalReservationService:
    return InternalReservationService(db)

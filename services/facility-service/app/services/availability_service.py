from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.repositories.booking_repository import BookingRepository
from app.repositories.facility_repository import FacilityRepository
from app.schemas.availability import AvailabilityConflict, AvailabilityOut


class AvailabilityService:
    def __init__(self, db: Session):
        self.bookings = BookingRepository(db)
        self.facilities = FacilityRepository(db)

    def check(
        self, facility_id: uuid.UUID, starts_at: datetime, ends_at: datetime
    ) -> AvailabilityOut:
        facility = self.facilities.get_facility(facility_id)
        if not facility:
            raise NotFoundError("Facility not found", code="facility_not_found")
        conflicts: list[AvailabilityConflict] = []
        for booking in self.bookings.overlapping_bookings(facility_id, starts_at, ends_at):
            conflicts.append(
                AvailabilityConflict(
                    kind="BOOKING",
                    id=booking.id,
                    starts_at=booking.starts_at,
                    ends_at=booking.ends_at,
                    status=booking.status,
                    description=booking.purpose,
                )
            )
        for block in self.bookings.overlapping_blocks(facility_id, starts_at, ends_at):
            conflicts.append(
                AvailabilityConflict(
                    kind="BLOCK",
                    id=block.id,
                    starts_at=block.starts_at,
                    ends_at=block.ends_at,
                    status=block.status,
                    description=block.reason,
                )
            )
        for reservation in self.bookings.overlapping_external(facility_id, starts_at, ends_at):
            conflicts.append(
                AvailabilityConflict(
                    kind="EXTERNAL_RESERVATION",
                    id=reservation.id,
                    starts_at=reservation.starts_at,
                    ends_at=reservation.ends_at,
                    status=reservation.status,
                    description=f"{reservation.source_service}:{reservation.source_reference_id}",
                )
            )
        available = facility.is_active and facility.is_bookable and not conflicts
        return AvailabilityOut(
            facility_id=facility_id,
            starts_at=starts_at,
            ends_at=ends_at,
            available=available,
            conflicts=conflicts,
        )

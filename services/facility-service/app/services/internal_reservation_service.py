from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.domain.models import ExternalReservation, OutboxEvent
from app.repositories.booking_repository import BookingRepository
from app.repositories.facility_repository import FacilityRepository
from app.repositories.outbox_repository import OutboxRepository
from app.schemas.internal import ExternalReservationCreate


class InternalReservationService:
    def __init__(self, db: Session):
        self.db = db
        self.bookings = BookingRepository(db)
        self.facilities = FacilityRepository(db)
        self.outbox = OutboxRepository(db)

    def create(self, payload: ExternalReservationCreate) -> ExternalReservation:
        facility = self.facilities.get_facility(payload.facility_id)
        if not facility:
            raise NotFoundError("Facility not found", code="facility_not_found")
        existing = self.bookings.get_external_by_source(
            payload.source_service, payload.source_reference_id
        )
        if existing:

            def normalized(value):
                return value if value.tzinfo else value.replace(tzinfo=UTC)

            if (
                existing.facility_id == payload.facility_id
                and normalized(existing.starts_at) == normalized(payload.starts_at)
                and normalized(existing.ends_at) == normalized(payload.ends_at)
                and existing.status == "ACTIVE"
            ):
                return existing
            raise ConflictError(
                "Source reservation already exists", code="source_reservation_exists"
            )
        try:
            self.bookings.lock_facility(facility.id)
            conflicts = self.bookings.overlapping_bookings(
                facility.id, payload.starts_at, payload.ends_at
            )
            conflicts += self.bookings.overlapping_blocks(
                facility.id, payload.starts_at, payload.ends_at
            )
            conflicts += self.bookings.overlapping_external(
                facility.id, payload.starts_at, payload.ends_at
            )
            if conflicts:
                raise ConflictError("Facility is unavailable", code="slot_conflict")
            reservation = ExternalReservation(
                facility_id=facility.id,
                source_service=payload.source_service,
                source_reference_id=payload.source_reference_id,
                starts_at=payload.starts_at,
                ends_at=payload.ends_at,
                metadata_json=payload.metadata,
            )
            self.bookings.add_external(reservation)
            self.outbox.add_event(
                OutboxEvent(
                    event_type="facility.external_reservation_created",
                    aggregate_type="external_reservation",
                    aggregate_id=reservation.id,
                    payload={
                        "reservation_id": str(reservation.id),
                        "facility_id": str(facility.id),
                        "source_service": reservation.source_service,
                        "source_reference_id": reservation.source_reference_id,
                    },
                    targets={},
                )
            )
            self.db.commit()
            return reservation
        except Exception:
            self.db.rollback()
            raise

    def cancel(self, source_service: str, source_reference_id: str) -> ExternalReservation:
        reservation = self.bookings.get_external_by_source(source_service, source_reference_id)
        if not reservation:
            raise NotFoundError(
                "External reservation not found", code="external_reservation_not_found"
            )
        if reservation.status == "CANCELLED":
            return reservation
        reservation.status = "CANCELLED"
        reservation.cancelled_at = datetime.now(UTC)
        try:
            self.db.add(reservation)
            self.db.commit()
            return reservation
        except Exception:
            self.db.rollback()
            raise

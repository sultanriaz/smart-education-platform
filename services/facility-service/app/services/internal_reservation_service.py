from __future__ import annotations

from datetime import UTC, datetime
import uuid

from sqlalchemy import select

from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.domain.models import ExternalReservation, OutboxEvent
from app.repositories.booking_repository import BookingRepository
from app.repositories.facility_repository import FacilityRepository
from app.repositories.outbox_repository import OutboxRepository
from app.schemas.internal import ExternalReservationCreate, ScheduleReservationsReplace


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


    def replace_schedule(self, schedule_id: uuid.UUID, payload: ScheduleReservationsReplace) -> dict:
        """Atomically reconcile all occurrences of one timetable schedule.

        PostgreSQL advisory locks serialize this operation with all normal booking
        and block writers. A conflict leaves existing reservations unchanged.
        """
        prefix = f"{schedule_id}:"
        source = "scheduling-service"
        desired = {f"{prefix}{o.occurrence_date.isoformat()}": o for o in payload.occurrences}
        try:
            query = select(ExternalReservation).where(
                ExternalReservation.source_service == source,
                ExternalReservation.source_reference_id.like(f"{prefix}%"),
            )
            current = list(self.db.scalars(query).all())
            facility_ids = {o.facility_id for o in payload.occurrences}
            facility_ids.update(o.facility_id for o in current if o.status == "ACTIVE")
            for facility_id in sorted(facility_ids, key=str):
                self.bookings.lock_facility(facility_id)
            # Re-read under the locks, including canceled records that can be revived.
            self.db.expire_all()
            current = list(self.db.scalars(query).all())
            existing = {o.source_reference_id: o for o in current}
            for o in payload.occurrences:
                facility = self.facilities.get_facility(o.facility_id)
                if not facility:
                    raise NotFoundError("Facility not found", code="facility_not_found")
                if not facility.is_active or not facility.is_bookable:
                    raise ConflictError("Classroom is not bookable", code="facility_not_bookable")
            # A schedule's own old reservations are excluded: an update may move them.
            own_ids = {o.id for o in current}
            for key, item in desired.items():
                conflicts = self.bookings.overlapping_bookings(
                    item.facility_id, item.starts_at, item.ends_at
                ) + self.bookings.overlapping_blocks(
                    item.facility_id, item.starts_at, item.ends_at
                )
                conflicts += [o for o in self.bookings.overlapping_external(
                    item.facility_id, item.starts_at, item.ends_at
                ) if o.id not in own_ids]
                if conflicts:
                    raise ConflictError("Classroom conflicts with an existing booking or reservation", code="slot_conflict")
            items = list(payload.occurrences)
            for i, first in enumerate(items):
                for second in items[i + 1:]:
                    if (first.facility_id == second.facility_id and
                            first.starts_at < second.ends_at and first.ends_at > second.starts_at):
                        raise ConflictError("Overlapping occurrences in the same classroom", code="slot_conflict")
            cancelled = 0
            now = datetime.now(UTC)
            for key, prior in existing.items():
                if key not in desired and prior.status == "ACTIVE":
                    prior.status = "CANCELLED"
                    prior.cancelled_at = now
                    cancelled += 1
            for key, item in desired.items():
                prior = existing.get(key)
                if prior is None:
                    self.bookings.add_external(ExternalReservation(
                        facility_id=item.facility_id, source_service=source,
                        source_reference_id=key, starts_at=item.starts_at,
                        ends_at=item.ends_at, metadata_json={"schedule_id": str(schedule_id),
                                                               "occurrence_date": item.occurrence_date.isoformat()},
                    ))
                else:
                    prior.facility_id = item.facility_id
                    prior.starts_at = item.starts_at
                    prior.ends_at = item.ends_at
                    prior.status = "ACTIVE"
                    prior.cancelled_at = None
            self.db.commit()
            return {"schedule_id": schedule_id, "active_count": len(desired),
                    "cancelled_count": cancelled}
        except Exception:
            self.db.rollback()
            raise

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import ConflictError, ForbiddenError, NotFoundError, ValidationError
from app.domain.models import Booking, BookingHistory, FacilityBlock, OutboxEvent
from app.repositories.booking_repository import BookingRepository
from app.repositories.facility_repository import FacilityRepository
from app.repositories.outbox_repository import OutboxRepository
from app.schemas.block import FacilityBlockCreate
from app.schemas.booking import BookingCancel, BookingCreate, BookingDecision
from app.security.auth import Principal


def utcnow() -> datetime:
    return datetime.now(UTC)


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=UTC)


class BookingService:
    def __init__(self, db: Session):
        self.db = db
        self.bookings = BookingRepository(db)
        self.facilities = FacilityRepository(db)
        self.outbox = OutboxRepository(db)

    def _validate_window(self, starts_at: datetime, ends_at: datetime) -> None:
        starts_at = _aware(starts_at)
        ends_at = _aware(ends_at)
        if ends_at <= starts_at:
            raise ValidationError("ends_at must be after starts_at", code="invalid_interval")
        duration = ends_at - starts_at
        if duration > timedelta(hours=settings.MAX_BOOKING_DURATION_HOURS):
            raise ValidationError("Booking exceeds maximum duration", code="booking_too_long")
        if starts_at < utcnow() + timedelta(minutes=settings.MIN_BOOKING_NOTICE_MINUTES):
            raise ValidationError("Booking start is too soon or in the past", code="booking_notice")

    def _conflicts(self, facility_id: uuid.UUID, starts_at: datetime, ends_at: datetime):
        return (
            self.bookings.overlapping_bookings(facility_id, starts_at, ends_at)
            + self.bookings.overlapping_blocks(facility_id, starts_at, ends_at)
            + self.bookings.overlapping_external(facility_id, starts_at, ends_at)
        )

    def create_booking(self, payload: BookingCreate, actor: Principal) -> Booking:
        self._validate_window(payload.starts_at, payload.ends_at)
        facility = self.facilities.get_facility(payload.facility_id)
        if not facility:
            raise NotFoundError("Facility not found", code="facility_not_found")
        if not facility.is_active or not facility.is_bookable:
            raise ConflictError(
                "Facility is not available for booking", code="facility_not_bookable"
            )
        if payload.attendees > facility.capacity:
            raise ValidationError(
                "Attendee count exceeds facility capacity", code="capacity_exceeded"
            )

        try:
            self.bookings.lock_facility(facility.id)
            if self._conflicts(facility.id, payload.starts_at, payload.ends_at):
                raise ConflictError(
                    "Requested time conflicts with an existing reservation", code="slot_conflict"
                )
            booking = Booking(
                facility_id=facility.id,
                requester_user_id=actor.user_id,
                purpose=payload.purpose.strip(),
                starts_at=payload.starts_at,
                ends_at=payload.ends_at,
                attendees=payload.attendees,
                status="PENDING",
            )
            self.bookings.add_booking(booking)
            self._history(booking, "CREATED", actor.user_id, None, "PENDING", None)
            self._event(
                "facility.booking_requested",
                booking,
                targets={"user_ids": [str(actor.user_id)], "roles": ["admin"]},
            )
            self.db.commit()
            return booking
        except Exception:
            self.db.rollback()
            raise

    def get_booking_for_actor(self, booking_id: uuid.UUID, actor: Principal) -> Booking:
        booking = self.bookings.get_booking(booking_id)
        if not booking:
            raise NotFoundError("Booking not found", code="booking_not_found")
        if not actor.has_role("admin") and booking.requester_user_id != actor.user_id:
            raise ForbiddenError("You cannot access this booking", code="booking_forbidden")
        return booking

    def approve(self, booking_id: uuid.UUID, payload: BookingDecision, actor: Principal) -> Booking:
        booking = self.bookings.get_booking(booking_id)
        if not booking:
            raise NotFoundError("Booking not found", code="booking_not_found")
        if booking.status != "PENDING":
            raise ConflictError(
                "Only pending bookings can be approved", code="invalid_booking_state"
            )
        try:
            self.bookings.lock_facility(booking.facility_id)
            conflicts = self.bookings.overlapping_bookings(
                booking.facility_id,
                booking.starts_at,
                booking.ends_at,
                exclude_booking_id=booking.id,
            )
            conflicts += self.bookings.overlapping_blocks(
                booking.facility_id, booking.starts_at, booking.ends_at
            )
            conflicts += self.bookings.overlapping_external(
                booking.facility_id, booking.starts_at, booking.ends_at
            )
            if conflicts:
                raise ConflictError(
                    "Booking conflicts with another reservation", code="slot_conflict"
                )
            old = booking.status
            booking.status = "APPROVED"
            booking.reviewed_by_user_id = actor.user_id
            booking.reviewed_at = utcnow()
            booking.review_note = payload.note
            self.db.add(booking)
            self._history(booking, "APPROVED", actor.user_id, old, booking.status, payload.note)
            self._event(
                "facility.booking_approved",
                booking,
                targets={"user_ids": [str(booking.requester_user_id)]},
            )
            self.db.commit()
            return booking
        except Exception:
            self.db.rollback()
            raise

    def reject(self, booking_id: uuid.UUID, payload: BookingDecision, actor: Principal) -> Booking:
        booking = self.bookings.get_booking(booking_id)
        if not booking:
            raise NotFoundError("Booking not found", code="booking_not_found")
        if booking.status != "PENDING":
            raise ConflictError(
                "Only pending bookings can be rejected", code="invalid_booking_state"
            )
        old = booking.status
        booking.status = "REJECTED"
        booking.reviewed_by_user_id = actor.user_id
        booking.reviewed_at = utcnow()
        booking.review_note = payload.note
        try:
            self.db.add(booking)
            self._history(booking, "REJECTED", actor.user_id, old, booking.status, payload.note)
            self._event(
                "facility.booking_rejected",
                booking,
                targets={"user_ids": [str(booking.requester_user_id)]},
            )
            self.db.commit()
            return booking
        except Exception:
            self.db.rollback()
            raise

    def cancel(self, booking_id: uuid.UUID, payload: BookingCancel, actor: Principal) -> Booking:
        booking = self.bookings.get_booking(booking_id)
        if not booking:
            raise NotFoundError("Booking not found", code="booking_not_found")
        if not actor.has_role("admin") and booking.requester_user_id != actor.user_id:
            raise ForbiddenError("You cannot cancel this booking", code="booking_forbidden")
        if booking.status not in {"PENDING", "APPROVED"}:
            raise ConflictError(
                "Booking cannot be cancelled in its current state", code="invalid_booking_state"
            )
        if not actor.has_role("admin"):
            cutoff = _aware(booking.starts_at) - timedelta(
                minutes=settings.CANCELLATION_CUTOFF_MINUTES
            )
            if utcnow() >= cutoff:
                raise ConflictError("Cancellation cutoff has passed", code="cancellation_cutoff")
        old = booking.status
        booking.status = "CANCELLED"
        booking.cancelled_by_user_id = actor.user_id
        booking.cancelled_at = utcnow()
        booking.cancellation_reason = payload.reason
        try:
            self.db.add(booking)
            self._history(booking, "CANCELLED", actor.user_id, old, booking.status, payload.reason)
            self._event(
                "facility.booking_cancelled",
                booking,
                targets={"user_ids": [str(booking.requester_user_id)]},
            )
            self.db.commit()
            return booking
        except Exception:
            self.db.rollback()
            raise

    def create_block(self, payload: FacilityBlockCreate, actor: Principal) -> FacilityBlock:
        self._validate_window(payload.starts_at, payload.ends_at)
        facility = self.facilities.get_facility(payload.facility_id)
        if not facility:
            raise NotFoundError("Facility not found", code="facility_not_found")
        try:
            self.bookings.lock_facility(facility.id)
            if self.bookings.overlapping_bookings(facility.id, payload.starts_at, payload.ends_at):
                raise ConflictError("Block conflicts with a booking", code="slot_conflict")
            if self.bookings.overlapping_external(facility.id, payload.starts_at, payload.ends_at):
                raise ConflictError(
                    "Block conflicts with an external reservation", code="slot_conflict"
                )
            block = FacilityBlock(
                facility_id=facility.id,
                starts_at=payload.starts_at,
                ends_at=payload.ends_at,
                reason=payload.reason,
                created_by_user_id=actor.user_id,
            )
            self.bookings.add_block(block)
            self.outbox.add_event(
                OutboxEvent(
                    event_type="facility.block_created",
                    aggregate_type="facility_block",
                    aggregate_id=block.id,
                    payload={"block_id": str(block.id), "facility_id": str(facility.id)},
                    targets={},
                )
            )
            self.db.commit()
            return block
        except Exception:
            self.db.rollback()
            raise

    def cancel_block(self, block_id: uuid.UUID, actor: Principal) -> FacilityBlock:
        block = self.bookings.get_block(block_id)
        if not block:
            raise NotFoundError("Facility block not found", code="block_not_found")
        if block.status != "ACTIVE":
            raise ConflictError("Block is already cancelled", code="invalid_block_state")
        block.status = "CANCELLED"
        block.cancelled_by_user_id = actor.user_id
        block.cancelled_at = utcnow()
        try:
            self.db.add(block)
            self.db.commit()
            return block
        except Exception:
            self.db.rollback()
            raise

    def _history(
        self,
        booking: Booking,
        action: str,
        actor_id: uuid.UUID,
        previous_status: str | None,
        new_status: str | None,
        note: str | None,
    ) -> None:
        self.bookings.add_history(
            BookingHistory(
                booking_id=booking.id,
                action=action,
                previous_status=previous_status,
                new_status=new_status,
                actor_user_id=actor_id,
                note=note,
                snapshot={
                    "facility_id": str(booking.facility_id),
                    "starts_at": booking.starts_at.isoformat(),
                    "ends_at": booking.ends_at.isoformat(),
                    "status": booking.status,
                },
            )
        )

    def _event(self, event_type: str, booking: Booking, *, targets: dict) -> None:
        self.outbox.add_event(
            OutboxEvent(
                event_type=event_type,
                aggregate_type="booking",
                aggregate_id=booking.id,
                payload={
                    "booking_id": str(booking.id),
                    "facility_id": str(booking.facility_id),
                    "requester_user_id": str(booking.requester_user_id),
                    "status": booking.status,
                    "starts_at": booking.starts_at.isoformat(),
                    "ends_at": booking.ends_at.isoformat(),
                    "title": "Facility booking update",
                    "message": f"Your facility booking is now {booking.status.lower()}.",
                },
                targets=targets,
            )
        )

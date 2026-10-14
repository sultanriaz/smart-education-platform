from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.domain.models import Booking, BookingHistory, ExternalReservation, FacilityBlock


class BookingRepository:
    def __init__(self, db: Session):
        self.db = db

    def lock_facility(self, facility_id: uuid.UUID) -> None:
        if self.db.bind is not None and self.db.bind.dialect.name == "postgresql":
            self.db.execute(
                text("SELECT pg_advisory_xact_lock(hashtext(:lock_key))"),
                {"lock_key": f"facility:{facility_id}"},
            )

    def add_booking(self, booking: Booking) -> None:
        self.db.add(booking)
        self.db.flush()

    def get_booking(self, booking_id: uuid.UUID, *, for_update: bool = False) -> Booking | None:
        stmt = select(Booking).where(Booking.id == booking_id)
        if for_update:
            stmt = stmt.with_for_update(of=Booking)
        return self.db.scalar(stmt)

    def list_bookings(
        self,
        *,
        offset: int,
        limit: int,
        requester_user_id: uuid.UUID | None = None,
        facility_id: uuid.UUID | None = None,
        status: str | None = None,
    ) -> list[Booking]:
        stmt = select(Booking).order_by(Booking.starts_at.desc()).offset(offset).limit(limit)
        if requester_user_id is not None:
            stmt = stmt.where(Booking.requester_user_id == requester_user_id)
        if facility_id is not None:
            stmt = stmt.where(Booking.facility_id == facility_id)
        if status is not None:
            stmt = stmt.where(Booking.status == status)
        return list(self.db.scalars(stmt).all())

    def overlapping_bookings(
        self,
        facility_id: uuid.UUID,
        starts_at: datetime,
        ends_at: datetime,
        *,
        exclude_booking_id: uuid.UUID | None = None,
    ) -> list[Booking]:
        blocking = ["APPROVED"]
        if settings.PENDING_BOOKINGS_RESERVE_SLOT:
            blocking.append("PENDING")
        stmt = select(Booking).where(
            Booking.facility_id == facility_id,
            Booking.status.in_(blocking),
            Booking.starts_at < ends_at,
            Booking.ends_at > starts_at,
        )
        if exclude_booking_id:
            stmt = stmt.where(Booking.id != exclude_booking_id)
        return list(self.db.scalars(stmt).all())

    def overlapping_blocks(
        self, facility_id: uuid.UUID, starts_at: datetime, ends_at: datetime
    ) -> list[FacilityBlock]:
        return list(
            self.db.scalars(
                select(FacilityBlock).where(
                    FacilityBlock.facility_id == facility_id,
                    FacilityBlock.status == "ACTIVE",
                    FacilityBlock.starts_at < ends_at,
                    FacilityBlock.ends_at > starts_at,
                )
            ).all()
        )

    def overlapping_external(
        self, facility_id: uuid.UUID, starts_at: datetime, ends_at: datetime
    ) -> list[ExternalReservation]:
        return list(
            self.db.scalars(
                select(ExternalReservation).where(
                    ExternalReservation.facility_id == facility_id,
                    ExternalReservation.status == "ACTIVE",
                    ExternalReservation.starts_at < ends_at,
                    ExternalReservation.ends_at > starts_at,
                )
            ).all()
        )

    def add_history(self, history: BookingHistory) -> None:
        self.db.add(history)
        self.db.flush()

    def list_history(self, booking_id: uuid.UUID) -> list[BookingHistory]:
        return list(
            self.db.scalars(
                select(BookingHistory)
                .where(BookingHistory.booking_id == booking_id)
                .order_by(BookingHistory.created_at)
            ).all()
        )

    def add_block(self, block: FacilityBlock) -> None:
        self.db.add(block)
        self.db.flush()

    def get_block(self, block_id: uuid.UUID) -> FacilityBlock | None:
        return self.db.get(FacilityBlock, block_id)

    def list_blocks(self, facility_id: uuid.UUID | None = None) -> list[FacilityBlock]:
        stmt = select(FacilityBlock).order_by(FacilityBlock.starts_at.desc())
        if facility_id:
            stmt = stmt.where(FacilityBlock.facility_id == facility_id)
        return list(self.db.scalars(stmt).all())

    def add_external(self, reservation: ExternalReservation) -> None:
        self.db.add(reservation)
        self.db.flush()

    def get_external_by_source(
        self, source_service: str, source_reference_id: str
    ) -> ExternalReservation | None:
        return self.db.scalar(
            select(ExternalReservation).where(
                ExternalReservation.source_service == source_service,
                ExternalReservation.source_reference_id == source_reference_id,
            )
        )

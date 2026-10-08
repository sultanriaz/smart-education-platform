from __future__ import annotations

from datetime import timedelta

import pytest

from app.core.errors import ConflictError
from app.schemas.booking import BookingCreate
from app.services.booking_service import BookingService
from tests.helpers import make_facility


def test_service_rollback_preserves_single_booking(db, student, admin, future_window):
    facility = make_facility(db, admin)
    start, end = future_window
    service = BookingService(db)
    service.create_booking(
        BookingCreate(
            facility_id=facility.id,
            purpose="First",
            starts_at=start,
            ends_at=end,
            attendees=3,
        ),
        student,
    )
    with pytest.raises(ConflictError):
        service.create_booking(
            BookingCreate(
                facility_id=facility.id,
                purpose="Second",
                starts_at=start + timedelta(minutes=10),
                ends_at=end,
                attendees=3,
            ),
            student,
        )
    from app.domain.models import Booking

    assert db.query(Booking).count() == 1

from datetime import UTC, datetime, time, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.core.errors import ConflictError
from app.schemas.facility import FacilityCreate, FacilityUpdate
from app.schemas.booking import BookingCreate
from app.services.booking_service import inside_operating_hours
from app.services.booking_service import BookingService
from app.services.facility_service import FacilityService


def test_hours_schema_rejects_invalid_timezone_and_partial_hours():
    common = dict(code="R1", name="Reading room", kind="ROOM", capacity=12)
    with pytest.raises(ValidationError):
        FacilityCreate(**common, opens_at_local="08:00")
    with pytest.raises(ValidationError):
        FacilityCreate(**common, opens_at_local="18:00", closes_at_local="08:00")
    with pytest.raises(ValidationError):
        FacilityCreate(**common, operating_timezone="Unknown/Planet")


def test_hours_closed_window_and_timezone_boundaries():
    f = SimpleNamespace(opens_at_local=time(9), closes_at_local=time(17), operating_timezone="Asia/Karachi")
    # UTC 04:00–12:00 is local 09:00–17:00 at Sahiwal.
    assert inside_operating_hours(f, datetime(2026, 10, 18, 4, tzinfo=UTC),
                                   datetime(2026, 10, 18, 12, tzinfo=UTC))
    assert not inside_operating_hours(f, datetime(2026, 10, 18, 3, tzinfo=UTC),
                                       datetime(2026, 10, 18, 6, tzinfo=UTC))
    assert not inside_operating_hours(f, datetime(2026, 10, 18, 11, tzinfo=UTC),
                                       datetime(2026, 10, 18, 21, tzinfo=UTC))


def test_booking_note_roundtrip_and_closed_window(db, admin):
    facility = FacilityService(db).create_facility(FacilityCreate(
        code="W10-ROOM", name="Wave ten room", kind="ROOM", capacity=20,
        opens_at_local=time(9), closes_at_local=time(17), operating_timezone="UTC"
    ), admin)
    start = datetime.now(UTC).replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=4)
    booked = BookingService(db).create_booking(BookingCreate(
        facility_id=facility.id, purpose="Seminar", requester_note="Projector needed",
        starts_at=start, ends_at=start+timedelta(hours=1), attendees=10
    ), admin)
    assert booked.requester_note == "Projector needed"
    with pytest.raises(ConflictError):
        BookingService(db).create_booking(BookingCreate(
            facility_id=facility.id, purpose="After hours", starts_at=start.replace(hour=18),
            ends_at=start.replace(hour=19), attendees=2
        ), admin)

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from tests.helpers import make_facility

TOKEN = {"X-Internal-Token": "CHANGE_ME_INTERNAL_SERVICE_TOKEN"}


def _body(facility_id, start, date="2026-10-19"):
    return {"occurrence_date": date, "facility_id": str(facility_id),
            "starts_at": start.isoformat(), "ends_at": (start + timedelta(hours=1)).isoformat()}


def _put(client, schedule, occurrences):
    return client.put(f"/api/v1/internal/reservations/schedules/{schedule}",
                      headers=TOKEN, json={"occurrences": occurrences})


def test_bulk_schedule_reservation_idempotent_and_blocks_booking(client, admin, student, db, as_principal):
    facility = make_facility(db, admin)
    start = datetime.now(UTC) + timedelta(days=3)
    schedule = uuid.uuid4()
    occurrence = _body(facility.id, start)
    assert (initial := _put(client, schedule, [occurrence])).status_code == 200, initial.text
    again = _put(client, schedule, [occurrence])
    assert again.status_code == 200 and again.json()["active_count"] == 1
    as_principal(student)
    blocked = client.post("/api/v1/bookings", json={
        "facility_id": str(facility.id), "purpose": "Study group",
        "starts_at": start.isoformat(), "ends_at": (start + timedelta(hours=1)).isoformat(),
        "attendees": 4,
    })
    assert blocked.status_code == 409, blocked.text
    assert _put(client, schedule, []).status_code == 200
    allowed = client.post("/api/v1/bookings", json={
        "facility_id": str(facility.id), "purpose": "Study group",
        "starts_at": start.isoformat(), "ends_at": (start + timedelta(hours=1)).isoformat(),
        "attendees": 4,
    })
    assert allowed.status_code == 201, allowed.text
    # A booked slot must not be re-acquired by a timetable.
    assert _put(client, schedule, [occurrence]).status_code == 409


def test_bulk_conflict_is_atomic_and_replacement_releases_original(client, admin, db):
    first_facility = make_facility(db, admin)
    other = make_facility(db, admin, code="ROOM-B13-OTHER")
    start = datetime.now(UTC) + timedelta(days=4)
    schedule_a, schedule_b = uuid.uuid4(), uuid.uuid4()
    original = _body(first_facility.id, start)
    assert _put(client, schedule_a, [original]).status_code == 200
    new = _body(other.id, start)
    other_schedule = _body(other.id, start + timedelta(minutes=30))
    assert _put(client, schedule_b, [other_schedule]).status_code == 200
    assert _put(client, schedule_a, [new]).status_code == 409
    from app.domain.models import ExternalReservation
    from sqlalchemy import select
    reservation = db.scalar(select(ExternalReservation).where(
        ExternalReservation.source_reference_id == f"{schedule_a}:2026-10-19"))
    assert reservation.status == "ACTIVE" and reservation.facility_id == first_facility.id
    assert _put(client, schedule_b, []).status_code == 200
    moved = _put(client, schedule_a, [new])
    assert moved.status_code == 200, moved.text
    db.refresh(reservation)
    assert reservation.facility_id == other.id


def test_bulk_requires_token(client, admin, db):
    facility = make_facility(db, admin)
    schedule = uuid.uuid4()
    resp = client.put(f"/api/v1/internal/reservations/schedules/{schedule}",
                      json={"occurrences": []})
    assert resp.status_code == 401

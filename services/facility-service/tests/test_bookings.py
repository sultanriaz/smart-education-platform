from __future__ import annotations

from datetime import timedelta

from app.domain.models import BookingHistory, OutboxEvent
from tests.helpers import make_facility


def payload(facility, start, end, attendees=10):
    return {
        "facility_id": str(facility.id),
        "purpose": "Project meeting",
        "starts_at": start.isoformat(),
        "ends_at": end.isoformat(),
        "attendees": attendees,
    }


def test_student_creates_pending_booking(client, as_principal, student, admin, db, future_window):
    facility = make_facility(db, admin)
    as_principal(student)
    start, end = future_window
    response = client.post("/api/v1/bookings", json=payload(facility, start, end))
    assert response.status_code == 201, response.text
    assert response.json()["status"] == "PENDING"
    assert db.query(BookingHistory).count() == 1
    assert db.query(OutboxEvent).filter_by(event_type="facility.booking_requested").count() == 1


def test_capacity_enforced(client, as_principal, student, admin, db, future_window):
    facility = make_facility(db, admin, capacity=5)
    as_principal(student)
    start, end = future_window
    response = client.post("/api/v1/bookings", json=payload(facility, start, end, attendees=6))
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "capacity_exceeded"


def test_overlapping_pending_booking_rejected(
    client, as_principal, student, other_student, admin, db, future_window
):
    facility = make_facility(db, admin)
    start, end = future_window
    as_principal(student)
    assert client.post("/api/v1/bookings", json=payload(facility, start, end)).status_code == 201
    as_principal(other_student)
    response = client.post(
        "/api/v1/bookings", json=payload(facility, start + timedelta(minutes=30), end)
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "slot_conflict"


def test_adjacent_booking_allowed(
    client, as_principal, student, other_student, admin, db, future_window
):
    facility = make_facility(db, admin)
    start, end = future_window
    as_principal(student)
    assert client.post("/api/v1/bookings", json=payload(facility, start, end)).status_code == 201
    as_principal(other_student)
    response = client.post(
        "/api/v1/bookings", json=payload(facility, end, end + timedelta(hours=1))
    )
    assert response.status_code == 201


def test_admin_approves_booking(client, as_principal, student, admin, db, future_window):
    facility = make_facility(db, admin)
    start, end = future_window
    as_principal(student)
    booking = client.post("/api/v1/bookings", json=payload(facility, start, end)).json()
    as_principal(admin)
    response = client.post(f"/api/v1/bookings/{booking['id']}/approve", json={"note": "Approved"})
    assert response.status_code == 200
    assert response.json()["status"] == "APPROVED"
    assert db.query(BookingHistory).count() == 2


def test_student_cannot_approve(client, as_principal, student, admin, db, future_window):
    facility = make_facility(db, admin)
    start, end = future_window
    as_principal(student)
    booking = client.post("/api/v1/bookings", json=payload(facility, start, end)).json()
    response = client.post(f"/api/v1/bookings/{booking['id']}/approve", json={})
    assert response.status_code == 403


def test_admin_rejects_booking_frees_slot(
    client, as_principal, student, other_student, admin, db, future_window
):
    facility = make_facility(db, admin)
    start, end = future_window
    as_principal(student)
    booking = client.post("/api/v1/bookings", json=payload(facility, start, end)).json()
    as_principal(admin)
    assert (
        client.post(
            f"/api/v1/bookings/{booking['id']}/reject", json={"note": "Unavailable"}
        ).status_code
        == 200
    )
    as_principal(other_student)
    assert client.post("/api/v1/bookings", json=payload(facility, start, end)).status_code == 201


def test_requester_cancels_own_booking(client, as_principal, student, admin, db, future_window):
    facility = make_facility(db, admin)
    start, end = future_window
    as_principal(student)
    booking = client.post("/api/v1/bookings", json=payload(facility, start, end)).json()
    response = client.post(
        f"/api/v1/bookings/{booking['id']}/cancel", json={"reason": "Plans changed"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"


def test_other_student_cannot_view_booking(
    client, as_principal, student, other_student, admin, db, future_window
):
    facility = make_facility(db, admin)
    start, end = future_window
    as_principal(student)
    booking = client.post("/api/v1/bookings", json=payload(facility, start, end)).json()
    as_principal(other_student)
    response = client.get(f"/api/v1/bookings/{booking['id']}")
    assert response.status_code == 403


def test_student_list_only_own_bookings(
    client, as_principal, student, other_student, admin, db, future_window
):
    facility = make_facility(db, admin)
    start, end = future_window
    as_principal(student)
    client.post("/api/v1/bookings", json=payload(facility, start, end))
    as_principal(other_student)
    client.post("/api/v1/bookings", json=payload(facility, end, end + timedelta(hours=1)))
    as_principal(student)
    response = client.get("/api/v1/bookings")
    assert response.status_code == 200
    assert len(response.json()) == 1

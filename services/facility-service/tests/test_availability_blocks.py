from __future__ import annotations

from tests.helpers import make_facility


def test_empty_window_available(client, as_principal, student, admin, db, future_window):
    facility = make_facility(db, admin)
    as_principal(student)
    start, end = future_window
    response = client.get(
        f"/api/v1/facilities/{facility.id}/availability",
        params={"starts_at": start.isoformat(), "ends_at": end.isoformat()},
    )
    assert response.status_code == 200
    assert response.json()["available"] is True


def test_booking_makes_window_unavailable(client, as_principal, student, admin, db, future_window):
    facility = make_facility(db, admin)
    start, end = future_window
    as_principal(student)
    client.post(
        "/api/v1/bookings",
        json={
            "facility_id": str(facility.id),
            "purpose": "Meeting",
            "starts_at": start.isoformat(),
            "ends_at": end.isoformat(),
            "attendees": 4,
        },
    )
    response = client.get(
        f"/api/v1/facilities/{facility.id}/availability",
        params={"starts_at": start.isoformat(), "ends_at": end.isoformat()},
    )
    assert response.json()["available"] is False
    assert response.json()["conflicts"][0]["kind"] == "BOOKING"


def test_admin_block_prevents_booking(client, as_principal, admin, student, db, future_window):
    facility = make_facility(db, admin)
    start, end = future_window
    as_principal(admin)
    block = client.post(
        "/api/v1/blocks",
        json={
            "facility_id": str(facility.id),
            "starts_at": start.isoformat(),
            "ends_at": end.isoformat(),
            "reason": "Maintenance",
        },
    )
    assert block.status_code == 201, block.text
    as_principal(student)
    response = client.post(
        "/api/v1/bookings",
        json={
            "facility_id": str(facility.id),
            "purpose": "Study group",
            "starts_at": start.isoformat(),
            "ends_at": end.isoformat(),
            "attendees": 4,
        },
    )
    assert response.status_code == 409


def test_cancelled_block_frees_slot(client, as_principal, admin, student, db, future_window):
    facility = make_facility(db, admin)
    start, end = future_window
    as_principal(admin)
    block = client.post(
        "/api/v1/blocks",
        json={
            "facility_id": str(facility.id),
            "starts_at": start.isoformat(),
            "ends_at": end.isoformat(),
            "reason": "Maintenance",
        },
    ).json()
    assert client.post(f"/api/v1/blocks/{block['id']}/cancel").status_code == 200
    as_principal(student)
    response = client.post(
        "/api/v1/bookings",
        json={
            "facility_id": str(facility.id),
            "purpose": "Study group",
            "starts_at": start.isoformat(),
            "ends_at": end.isoformat(),
            "attendees": 4,
        },
    )
    assert response.status_code == 201

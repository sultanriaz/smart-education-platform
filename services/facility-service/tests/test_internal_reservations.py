from __future__ import annotations

from tests.helpers import make_facility

TOKEN = "CHANGE_ME_INTERNAL_SERVICE_TOKEN"


def test_internal_requires_token(client, admin, db, future_window):
    facility = make_facility(db, admin)
    start, end = future_window
    response = client.post(
        "/api/v1/internal/reservations",
        json={
            "facility_id": str(facility.id),
            "source_service": "scheduling-service",
            "source_reference_id": "schedule-1",
            "starts_at": start.isoformat(),
            "ends_at": end.isoformat(),
        },
    )
    assert response.status_code in {401, 422}


def test_internal_reservation_created_and_idempotent(client, admin, db, future_window):
    facility = make_facility(db, admin)
    start, end = future_window
    body = {
        "facility_id": str(facility.id),
        "source_service": "scheduling-service",
        "source_reference_id": "schedule-1",
        "starts_at": start.isoformat(),
        "ends_at": end.isoformat(),
        "metadata": {"section_id": "abc"},
    }
    headers = {"X-Internal-Token": TOKEN}
    first = client.post("/api/v1/internal/reservations", json=body, headers=headers)
    assert first.status_code == 201, first.text
    second = client.post("/api/v1/internal/reservations", json=body, headers=headers)
    assert second.status_code == 201
    assert second.json()["id"] == first.json()["id"]


def test_external_reservation_blocks_user_booking(
    client, as_principal, student, admin, db, future_window
):
    facility = make_facility(db, admin)
    start, end = future_window
    client.post(
        "/api/v1/internal/reservations",
        headers={"X-Internal-Token": TOKEN},
        json={
            "facility_id": str(facility.id),
            "source_service": "scheduling-service",
            "source_reference_id": "occurrence-77",
            "starts_at": start.isoformat(),
            "ends_at": end.isoformat(),
        },
    )
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


def test_cancelling_external_reservation_frees_slot(
    client, as_principal, student, admin, db, future_window
):
    facility = make_facility(db, admin)
    start, end = future_window
    headers = {"X-Internal-Token": TOKEN}
    client.post(
        "/api/v1/internal/reservations",
        headers=headers,
        json={
            "facility_id": str(facility.id),
            "source_service": "scheduling-service",
            "source_reference_id": "occurrence-78",
            "starts_at": start.isoformat(),
            "ends_at": end.isoformat(),
        },
    )
    assert (
        client.delete(
            "/api/v1/internal/reservations/scheduling-service/occurrence-78", headers=headers
        ).status_code
        == 200
    )
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

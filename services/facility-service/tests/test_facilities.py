from __future__ import annotations

from app.domain.models import OutboxEvent


def test_admin_creates_facility(client, as_principal, admin):
    as_principal(admin)
    response = client.post(
        "/api/v1/facilities",
        json={"code": "lab-1", "name": "AI Lab", "kind": "lab", "capacity": 35},
    )
    assert response.status_code == 201, response.text
    assert response.json()["code"] == "LAB-1"
    assert response.json()["kind"] == "LAB"


def test_student_cannot_create_facility(client, as_principal, student):
    as_principal(student)
    response = client.post(
        "/api/v1/facilities",
        json={"code": "R1", "name": "Room One", "kind": "ROOM", "capacity": 20},
    )
    assert response.status_code == 403


def test_duplicate_facility_code_rejected(client, as_principal, admin):
    as_principal(admin)
    payload = {"code": "R-1", "name": "Room One", "kind": "ROOM", "capacity": 20}
    assert client.post("/api/v1/facilities", json=payload).status_code == 201
    response = client.post("/api/v1/facilities", json=payload)
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "facility_code_exists"


def test_invalid_facility_kind_rejected(client, as_principal, admin):
    as_principal(admin)
    response = client.post(
        "/api/v1/facilities",
        json={"code": "R2", "name": "Room Two", "kind": "SPACE_SHIP", "capacity": 20},
    )
    assert response.status_code == 422


def test_equipment_assignment(client, as_principal, admin):
    as_principal(admin)
    facility = client.post(
        "/api/v1/facilities",
        json={"code": "LAB2", "name": "Networks Lab", "kind": "LAB", "capacity": 30},
    ).json()
    equipment = client.post(
        "/api/v1/equipment",
        json={"code": "PROJ", "name": "Projector"},
    ).json()
    response = client.put(
        f"/api/v1/facilities/{facility['id']}/equipment",
        json={"equipment_id": equipment["id"], "quantity": 2},
    )
    assert response.status_code == 200
    detail = client.get(f"/api/v1/facilities/{facility['id']}")
    assert detail.json()["equipment"][0]["quantity"] == 2


def test_create_facility_emits_outbox(client, as_principal, admin, db):
    as_principal(admin)
    client.post(
        "/api/v1/facilities",
        json={"code": "H1", "name": "Hall One", "kind": "HALL", "capacity": 100},
    )
    assert db.query(OutboxEvent).filter_by(event_type="facility.created").count() == 1

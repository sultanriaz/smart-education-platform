"""B01 scoped grants: independent review, facility, block permissions."""
from __future__ import annotations

from app.security.auth import Principal
from tests.conftest import ADMIN_ID


def test_custom_facility_manager_can_create_but_not_review(client, as_principal):
    as_principal(Principal(ADMIN_ID, frozenset({"room-manager"}),
                           permissions=frozenset({"facility.facilities.manage"})))
    result = client.post("/api/v1/facilities", json={
        "code": "B01-ROOM", "name": "Permission Test Room", "kind": "ROOM", "capacity": 24,
    })
    assert result.status_code == 201, result.text
    assert client.get("/api/v1/facilities").status_code == 200
    assert client.get("/api/v1/blocks").status_code == 403
    assert client.post("/api/v1/bookings/" + str(ADMIN_ID) + "/approve", json={}).status_code == 403


def test_custom_reviewer_can_list_but_not_manage_facilities(client, as_principal, admin, db):
    from tests.helpers import make_facility
    make_facility(db, admin)
    as_principal(Principal(ADMIN_ID, frozenset({"booking-reviewer"}),
                           permissions=frozenset({"facility.bookings.review"})))
    assert client.get("/api/v1/bookings").status_code == 200
    assert client.get("/api/v1/blocks").status_code == 403
    assert client.post("/api/v1/facilities", json={}).status_code == 403


def test_custom_role_without_grants_denied_on_privileged_routes(client, as_principal):
    as_principal(Principal(ADMIN_ID, frozenset({"observer"})))
    assert client.post("/api/v1/facilities", json={}).status_code == 403
    assert client.get("/api/v1/blocks").status_code == 403

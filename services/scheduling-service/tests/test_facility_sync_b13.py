from __future__ import annotations

from tests.conftest import ROOM_2_ID


def _url(schedule):
    return f"/api/v1/schedules/{schedule['id']}"


def test_publishing_blocks_each_date_and_cancel_releases(client, fake_facility, schedule_payload):
    result = client.post("/api/v1/schedules", json=schedule_payload)
    assert result.status_code == 201, result.text
    schedule = result.json()
    reservations = fake_facility.reservations[schedule["id"]]
    assert len(reservations) == 13
    assert reservations[0]["occurrence_date"] == "2026-10-05"
    assert reservations[0]["facility_id"] == schedule_payload["room_id"]
    assert reservations[0]["starts_at"].endswith("+00:00")
    response = client.post(_url(schedule) + "/cancel", json={"reason": "closing"})
    assert response.status_code == 200, response.text
    assert fake_facility.reservations[schedule["id"]] == []


def test_draft_does_not_reserve_until_publish(client, fake_facility, schedule_payload):
    schedule_payload["publish"] = False
    result = client.post("/api/v1/schedules", json=schedule_payload)
    assert result.status_code == 201, result.text
    schedule = result.json()
    assert schedule["id"] not in fake_facility.reservations
    response = client.post(_url(schedule) + "/publish")
    assert response.status_code == 200, response.text
    assert len(fake_facility.reservations[schedule["id"]]) == 13


def test_facility_failure_fails_closed_without_schedule_commit(client, db, fake_facility, schedule_payload):
    from app.domain.models import ScheduleEntry
    from sqlalchemy import select
    fake_facility.fail = True
    result = client.post("/api/v1/schedules", json=schedule_payload)
    assert result.status_code == 503, result.text
    db.rollback()
    assert db.scalar(select(ScheduleEntry)) is None


def test_override_cancels_one_date_and_restores_or_moves(client, fake_facility, schedule_payload):
    schedule = client.post("/api/v1/schedules", json=schedule_payload).json()
    base = _url(schedule) + "/overrides"
    result = client.post(base, json={"occurrence_date": "2026-10-12", "kind": "CANCELLED"})
    assert result.status_code == 201, result.text
    rows = fake_facility.reservations[schedule["id"]]
    assert len(rows) == 12
    assert "2026-10-12" not in {o["occurrence_date"] for o in rows}
    result = client.post(base, json={
        "occurrence_date": "2026-10-12", "kind": "RESCHEDULED",
        "starts_at": "11:00:00", "ends_at": "12:00:00", "room_id": str(ROOM_2_ID),
    })
    assert result.status_code == 201, result.text
    new = [o for o in fake_facility.reservations[schedule["id"]]
           if o["occurrence_date"] == "2026-10-12"]
    assert len(new) == 1 and new[0]["facility_id"] == str(ROOM_2_ID)


def test_update_replaces_reservations_not_appends(client, fake_facility, schedule_payload):
    schedule = client.post("/api/v1/schedules", json=schedule_payload).json()
    response = client.patch(_url(schedule), json={"starts_at": "11:00:00", "ends_at": "12:00:00"})
    assert response.status_code == 200, response.text
    rows = fake_facility.reservations[schedule["id"]]
    assert len(rows) == 13
    assert rows[0]["starts_at"].endswith("06:00:00+00:00")


def test_reservation_conflict_rejects_publish_and_keeps_draft(client, fake_facility, schedule_payload):
    schedule_payload["publish"] = False
    schedule = client.post("/api/v1/schedules", json=schedule_payload).json()
    fake_facility.reservations["other-schedule"] = [{
        "facility_id": schedule_payload["room_id"],
        "starts_at": "2026-10-05T04:30:00+00:00", "ends_at": "2026-10-05T05:15:00+00:00",
    }]
    result = client.post(_url(schedule) + "/publish")
    assert result.status_code == 409, result.text
    db_state = client.get(_url(schedule))
    assert db_state.status_code == 200 and db_state.json()["status"] == "DRAFT"

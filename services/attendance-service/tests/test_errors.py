from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.domain.models import AttendanceSession
from app.repositories.attendance import AttendanceRepository


def test_unexpected_errors_keep_envelope_and_do_not_leak_details(client, academic, db, monkeypatch):
    def fail(self, row):
        raise RuntimeError("sensitive internal database detail")

    monkeypatch.setattr(AttendanceRepository, "add", fail)
    with TestClient(client.app, raise_server_exceptions=False) as errors_http:
        errors_http.headers.update(client.headers)
        response = errors_http.post(
            "/api/v1/sessions",
            json={
                "section_id": str(academic.section.id),
                "session_date": "2026-10-07",
            },
        )
    assert response.status_code == 500
    assert response.json()["code"] == "internal_error"
    assert response.json()["request_id"] == response.headers["X-Request-ID"]
    assert "sensitive" not in response.text
    assert db.scalar(select(func.count()).select_from(AttendanceSession)) == 0

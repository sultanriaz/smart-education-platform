from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.api import health
from app.core.config import Settings


def test_health_is_public_without_academic_or_database(client):
    client.headers.pop("Authorization")
    assert client.get("/health").json() == {"status": "ok", "service": "attendance-service"}


def test_readiness_requires_database_and_current_migration(client, db, monkeypatch):
    monkeypatch.setattr(health, "engine", db.get_bind())
    assert client.get("/ready").status_code == 503
    db.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) PRIMARY KEY)"))
    db.execute(text("INSERT INTO alembic_version VALUES ('outdated')"))
    db.commit()
    assert client.get("/ready").status_code == 503
    db.execute(text("UPDATE alembic_version SET version_num = '0001_attendance_core'"))
    db.commit()
    client.headers.pop("Authorization")
    assert client.get("/ready").json()["status"] == "ready"


def test_readiness_database_outage(client, monkeypatch):
    engine = MagicMock()
    engine.connect.side_effect = OperationalError("SELECT", {}, Exception("offline"))
    monkeypatch.setattr(health, "engine", engine)
    assert client.get("/ready").status_code == 503


@pytest.mark.parametrize(
    "settings",
    [
        {"DATABASE_URL": "sqlite://"},
        {"LOW_ATTENDANCE_THRESHOLD_PERCENT": 101},
        {"ACADEMIC_SERVICE_BASE_URL": "file:///tmp/data"},
        {"ACADEMIC_SERVICE_TIMEOUT_SECONDS": 0},
        {"JWT_ISSUER": ""},
        {"JWT_ACCESS_AUDIENCE": ""},
        {"JWT_JWKS_URL": "http://user:pass@server"},
        {"ENVIRONMENT": "production"},
    ],
)
def test_invalid_configuration_is_rejected(settings):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **settings)

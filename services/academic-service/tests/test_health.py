from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.api import health


def test_health_is_public_and_does_not_need_database(client):
    client.headers.pop("Authorization")
    assert client.get("/health").json() == {"status": "ok", "service": "academic-service"}


def test_ready_checks_database_and_migration(client, db, monkeypatch):
    monkeypatch.setattr(health, "engine", db.get_bind())
    assert client.get("/ready").status_code == 503
    db.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) PRIMARY KEY)"))
    db.execute(text("INSERT INTO alembic_version VALUES ('outdated')"))
    db.commit()
    assert client.get("/ready").status_code == 503
    db.execute(text("UPDATE alembic_version SET version_num = '0001_academic_core'"))
    db.commit()
    client.headers.pop("Authorization")
    assert client.get("/ready").json()["status"] == "ready"


def test_ready_database_outage(client, monkeypatch):
    engine = MagicMock()
    engine.connect.side_effect = OperationalError("SELECT 1", {}, Exception("offline"))
    monkeypatch.setattr(health, "engine", engine)
    assert client.get("/ready").status_code == 503


@pytest.mark.parametrize(
    "overrides",
    [
        {"DATABASE_URL": "sqlite://"},
        {"JWT_ISSUER": ""},
        {"JWT_ACCESS_AUDIENCE": ""},
        {"JWT_JWKS_URL": "file:///untrusted.json"},
        {"JWT_LEEWAY_SECONDS": 60},
        {"ENVIRONMENT": "production", "JWT_ISSUER": "http://identity.example.test"},
    ],
)
def test_invalid_configuration(overrides):
    from pydantic import ValidationError

    from app.core.config import Settings

    with pytest.raises(ValidationError):
        Settings(_env_file=None, **overrides)

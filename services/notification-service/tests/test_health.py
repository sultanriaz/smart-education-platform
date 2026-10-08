from __future__ import annotations


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ready_requires_current_owned_schema(client, db):
    from pathlib import Path

    from smartedu_infra.migrations import migration_head
    from sqlalchemy import text

    # create_all alone does not mean that production migrations ran.
    assert client.get("/ready").status_code == 503
    db.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) PRIMARY KEY)"))
    db.execute(text("INSERT INTO alembic_version VALUES ('outdated')"))
    db.commit()
    assert client.get("/ready").status_code == 503
    head = migration_head(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    db.execute(text("UPDATE alembic_version SET version_num = :head"), {"head": head})
    db.commit()
    assert client.get("/ready").status_code == 200

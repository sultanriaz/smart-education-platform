from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import engine

router = APIRouter(tags=["health"])


@lru_cache
def expected_revision() -> str | None:
    return ScriptDirectory.from_config(
        Config(
            str(Path(__file__).resolve().parents[2] / "alembic.ini"),
        )
    ).get_current_head()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "attendance-service"}


@router.get("/ready")
def ready() -> dict[str, str]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            if (
                connection.scalar(text("SELECT version_num FROM alembic_version"))
                != expected_revision()
            ):
                raise HTTPException(503, "Attendance migrations are not current.")
    except SQLAlchemyError as exc:
        raise HTTPException(503, "Attendance database is unavailable or not migrated.") from exc
    return {"status": "ready", "service": "attendance-service"}

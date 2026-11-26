from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.engine import Engine


@dataclass(frozen=True, slots=True)
class DependencyHealth:
    name: str
    ok: bool
    detail: str | None = None


def check_database(engine: Engine) -> DependencyHealth:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return DependencyHealth(name="database", ok=True)
    except Exception as exc:
        return DependencyHealth(
            name="database",
            ok=False,
            detail=exc.__class__.__name__,
        )

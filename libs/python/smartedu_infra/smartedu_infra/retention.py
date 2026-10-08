from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import text
from sqlalchemy.engine import Engine


@dataclass(frozen=True, slots=True)
class RetentionRule:
    table_name: str
    timestamp_column: str
    retention_days: int
    extra_where_sql: str = "TRUE"

    def cutoff(self, now: datetime | None = None) -> datetime:
        current = now or datetime.now(UTC)
        if current.tzinfo is None:
            raise ValueError("Retention clock must be timezone-aware")
        return current - timedelta(days=self.retention_days)


def _safe_identifier(value: str) -> str:
    if not value.replace("_", "").isalnum():
        raise ValueError(f"Unsafe SQL identifier: {value}")
    return value


def delete_expired(
    engine: Engine,
    rules: Iterable[RetentionRule],
    *,
    batch_size: int = 5000,
    now: datetime | None = None,
) -> dict[str, int]:
    if batch_size < 1:
        raise ValueError("batch_size must be positive")

    results: dict[str, int] = {}
    for rule in rules:
        table = _safe_identifier(rule.table_name)
        column = _safe_identifier(rule.timestamp_column)
        cutoff = rule.cutoff(now)

        # PostgreSQL ctid batching avoids one massive delete/lock window.
        statement = text(
            f"""
            WITH doomed AS (
                SELECT ctid
                FROM {table}
                WHERE {column} < :cutoff
                  AND ({rule.extra_where_sql})
                LIMIT :batch_size
            )
            DELETE FROM {table}
            WHERE ctid IN (SELECT ctid FROM doomed)
            """
        )

        total = 0
        while True:
            with engine.begin() as connection:
                result = connection.execute(
                    statement,
                    {"cutoff": cutoff, "batch_size": batch_size},
                )
                deleted = int(result.rowcount or 0)
            total += deleted
            if deleted < batch_size:
                break

        results[table] = total
    return results

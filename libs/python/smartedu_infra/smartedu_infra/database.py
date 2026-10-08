from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine

from .settings import DatabaseSettings


@dataclass(frozen=True, slots=True)
class PoolPlan:
    pool_size: int
    max_overflow: int
    pool_timeout_seconds: int
    pool_recycle_seconds: int
    statement_timeout_ms: int
    application_name: str


def pool_plan(settings: DatabaseSettings) -> PoolPlan:
    return PoolPlan(
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout_seconds=settings.db_pool_timeout_seconds,
        pool_recycle_seconds=settings.db_pool_recycle_seconds,
        statement_timeout_ms=settings.db_statement_timeout_ms,
        application_name=settings.db_application_name,
    )


def build_engine(
    settings: DatabaseSettings,
    *,
    echo: bool = False,
    extra_connect_args: dict[str, Any] | None = None,
) -> Engine:
    connect_args = dict(extra_connect_args or {})
    url = settings.database_url

    if url.startswith("postgresql"):
        options = (
            f"-c statement_timeout={settings.db_statement_timeout_ms} "
            f"-c application_name={settings.db_application_name}"
        )
        connect_args.setdefault("options", options)
        connect_args.setdefault("connect_timeout", 3)

    kwargs: dict[str, Any] = {
        "pool_pre_ping": True,
        "pool_recycle": settings.db_pool_recycle_seconds,
        "echo": echo,
        "future": True,
        "connect_args": connect_args,
    }

    if not url.startswith("sqlite"):
        kwargs.update(
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            pool_timeout=settings.db_pool_timeout_seconds,
        )

    engine = create_engine(url, **kwargs)

    if url.startswith("postgresql"):

        @event.listens_for(engine, "connect")
        def _set_timezone(dbapi_connection, _connection_record):
            cursor = dbapi_connection.cursor()
            try:
                cursor.execute("SET TIME ZONE 'UTC'")
            finally:
                cursor.close()

    return engine

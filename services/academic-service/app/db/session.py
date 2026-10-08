from __future__ import annotations

from collections.abc import Iterator

from smartedu_infra import DatabaseSettings, build_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

engine = build_engine(
    DatabaseSettings(
        DATABASE_URL=get_settings().DATABASE_URL, DB_APPLICATION_NAME="academic-service"
    )
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session

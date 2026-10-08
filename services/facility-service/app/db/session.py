from __future__ import annotations

from smartedu_infra import DatabaseSettings, build_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = build_engine(
    DatabaseSettings(DATABASE_URL=settings.DATABASE_URL, DB_APPLICATION_NAME="facility-service")
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

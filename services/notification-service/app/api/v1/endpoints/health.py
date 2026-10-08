from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from smartedu_infra.migrations import assert_owned_revision
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db

router = APIRouter(tags=["Health"])


@router.get("/health")
def health():
    return {"status": "ok", "service": "notification-service"}


@router.get("/ready")
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        assert_owned_revision(db, str(Path(__file__).resolve().parents[4] / "alembic.ini"))
        dependencies = {"database": "ready"}
        if settings.TASK_MODE.lower() == "celery":
            import redis

            redis.Redis.from_url(settings.REDIS_URL, socket_timeout=2).ping()
            dependencies["redis"] = "ready"
        return {"status": "ready", "dependencies": dependencies}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Notification service is not ready") from exc

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from smartedu_infra.migrations import assert_owned_revision
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter(tags=["Health"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/ready")
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        assert_owned_revision(db, str(Path(__file__).resolve().parents[4] / "alembic.ini"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database unavailable.") from exc
    return {"status": "ready"}

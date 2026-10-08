from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.reporting_service import ReportingService


def get_reporting_service(db: Session = Depends(get_db)) -> ReportingService:
    return ReportingService(db)

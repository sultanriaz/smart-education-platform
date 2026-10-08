from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.event_ingestion_service import EventIngestionService
from app.services.platform_service import PlatformService


def get_platform_service(db: Session = Depends(get_db)):
    return PlatformService(db)


def get_event_service(db: Session = Depends(get_db)):
    return EventIngestionService(db)

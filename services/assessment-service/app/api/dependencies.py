from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.clients.academic import AcademicClient
from app.db.session import get_db
from app.services.assessment_service import AssessmentService


def get_service(db: Session = Depends(get_db)) -> AssessmentService:
    return AssessmentService(db, AcademicClient())

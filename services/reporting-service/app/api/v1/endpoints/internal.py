from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import get_reporting_service
from app.schemas.events import EventIngestResult, InternalEventIn
from app.security.auth import require_internal_token
from app.services.reporting_service import ReportingService

router = APIRouter(prefix="/internal", tags=["Internal"])


@router.post("/events", response_model=EventIngestResult)
def ingest_event(
    payload: InternalEventIn,
    _auth=Depends(require_internal_token),
    service: ReportingService = Depends(get_reporting_service),
):
    status = service.ingest_event(payload)
    return EventIngestResult(status=status, event_id=payload.event_id)

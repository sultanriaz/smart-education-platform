from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import get_event_service
from app.schemas.events import InternalEventIn, InternalEventResult
from app.security.auth import require_internal_token
from app.services.event_ingestion_service import EventIngestionService

router = APIRouter(prefix="/internal", tags=["Internal"])


@router.post("/events", response_model=InternalEventResult)
def ingest_event(
    payload: InternalEventIn,
    _auth=Depends(require_internal_token),
    service: EventIngestionService = Depends(get_event_service),
):
    status = service.ingest(payload)
    return InternalEventResult(status=status, event_id=payload.event_id)

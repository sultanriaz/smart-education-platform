from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_dispatcher
from app.db.session import get_db
from app.queue.dispatcher import TaskDispatcher
from app.schemas.notification import InternalEventAck, InternalEventIn
from app.security.internal import require_internal_token
from app.services.event_service import EventService

router = APIRouter(prefix="/internal", tags=["Internal Events"])


@router.post(
    "/events",
    response_model=InternalEventAck,
    status_code=202,
    dependencies=[Depends(require_internal_token)],
)
def ingest_event(
    payload: InternalEventIn,
    db: Session = Depends(get_db),
    dispatcher: TaskDispatcher = Depends(get_dispatcher),
):
    event, duplicate = EventService(db).ingest(payload)
    if not duplicate and event.status == "RECEIVED":
        dispatcher.process_inbox_event(event.id)
    return InternalEventAck(
        accepted=True, duplicate=duplicate, inbox_event_id=event.id, status=event.status
    )

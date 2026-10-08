from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import DependencyContractError
from app.domain.models import InboxEvent, OutboxEvent
from app.repositories.event_repository import EventRepository
from app.repositories.outbox_repository import OutboxRepository
from app.schemas.notification import InternalEventIn
from app.services.campaign_service import CampaignService
from app.services.target_resolver import TargetResolver


class EventService:
    def __init__(self, db: Session, resolver: TargetResolver | None = None):
        self.db = db
        self.repo = EventRepository(db)
        self.outbox = OutboxRepository(db)
        self.resolver = resolver or TargetResolver()

    def ingest(self, payload: InternalEventIn) -> tuple[InboxEvent, bool]:
        existing = self.repo.get_by_event_id(payload.event_id)
        if existing is not None:
            return existing, True
        value = InboxEvent(
            event_id=payload.event_id,
            source_service=payload.source_service,
            event_type=payload.event_type,
            occurred_at=payload.occurred_at,
            payload=payload.payload,
            targets=payload.targets,
            status="RECEIVED",
        )
        self.repo.add_event(value)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            existing = self.repo.get_by_event_id(payload.event_id)
            if existing is not None:
                return existing, True
            raise
        self.db.refresh(value)
        return value, False

    def process(self, inbox_event_id: uuid.UUID) -> list[uuid.UUID]:
        event = self.repo.get_event(inbox_event_id, for_update=True)
        if event is None:
            return []
        if event.status == "PROCESSED":
            return []
        try:
            recipients = self.resolver.resolve_event_targets(
                event.targets or {}, event.payload or {}
            )
            if not recipients:
                raise DependencyContractError("Event has no resolvable recipients")
            pending = CampaignService(self.db, self.resolver).create_from_event(
                recipients=recipients,
                source_service=event.source_service,
                source_event_id=event.event_id,
                event_type=event.event_type,
                payload=event.payload or {},
            )
            event.status = "PROCESSED"
            event.error = None
            event.processed_at = datetime.now(UTC)
            self.outbox.add_event(
                OutboxEvent(
                    event_type="notification.source_event_processed",
                    aggregate_type="inbox_event",
                    aggregate_id=event.id,
                    payload={"source_event_id": event.event_id},
                )
            )
            self.db.commit()
            return pending
        except Exception as exc:
            self.db.rollback()
            event = self.repo.get_event(inbox_event_id, for_update=True)
            if event is not None:
                event.status = "FAILED"
                event.retry_count += 1
                event.error = str(exc)[:2000]
                self.db.commit()
            raise

"""Platform-owned audit/search ingestion and outbox publishing."""

import asyncio
import logging

from smartedu_infra.runtime import run_owned_worker

from app.db.session import SessionLocal
from app.domain.entities.models import OutboxEvent
from app.schemas.events import InternalEventIn
from app.services.event_ingestion_service import EventIngestionService
from app.workers.job_runner import process_jobs


def handle(envelope):
    with SessionLocal() as db:
        EventIngestionService(db).ingest(
            InternalEventIn(
                event_id=str(envelope.event_id),
                source_service=envelope.source,
                event_type=envelope.event_type,
                occurred_at=envelope.occurred_at,
                payload=envelope.data,
            )
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(
        run_owned_worker(
            service_name="platform-service",
            session_factory=SessionLocal,
            outbox_model=OutboxEvent,
            handler=handle,
            maintenance=lambda: process_jobs(SessionLocal),
        )
    )

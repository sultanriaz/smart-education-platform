"""Consume durable domain events into Reporting-owned projections."""

import asyncio
import logging

from smartedu_infra.runtime import run_owned_worker

from app.db.session import SessionLocal
from app.schemas.events import InternalEventIn
from app.services.reporting_service import ReportingService


def handle(envelope):
    with SessionLocal() as db:
        ReportingService(db).ingest_event(
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
            service_name="reporting-service", session_factory=SessionLocal, handler=handle
        )
    )

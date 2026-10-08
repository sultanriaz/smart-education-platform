"""Publish only assessment-owned events; deploy independently of the API."""

import asyncio
import logging

from smartedu_infra.runtime import run_owned_worker

from app.db.session import SessionLocal
from app.domain.entities.models import OutboxEvent
from app.workers.attempt_expiry import expire_attempts

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(
        run_owned_worker(
            service_name="assessment-service",
            session_factory=SessionLocal,
            outbox_model=OutboxEvent,
            maintenance=lambda: expire_attempts(SessionLocal),
        )
    )

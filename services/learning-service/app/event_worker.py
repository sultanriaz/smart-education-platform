"""Publish only learning-owned events; deploy independently of the API."""

import asyncio
import logging

from smartedu_infra.runtime import run_owned_worker

from app.db.session import SessionLocal
from app.domain.entities.models import OutboxEvent
from app.services.file_cleanup import run_file_cleanup

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(
        run_owned_worker(
            service_name="learning-service", session_factory=SessionLocal, outbox_model=OutboxEvent,
            maintenance=run_file_cleanup
        )
    )

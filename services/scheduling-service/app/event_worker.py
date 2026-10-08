"""Publish only scheduling-owned events; deploy independently of the API."""

import asyncio
import logging

from smartedu_infra.runtime import run_owned_worker

from app.db.session import SessionLocal
from app.domain.models import OutboxEvent

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(
        run_owned_worker(
            service_name="scheduling-service",
            session_factory=SessionLocal,
            outbox_model=OutboxEvent,
        )
    )

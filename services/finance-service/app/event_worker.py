"""Finance service event worker: outbox publisher and domain event subscriber."""
from __future__ import annotations

import asyncio
import logging

from smartedu_infra.runtime import run_owned_worker

from app.db.session import SessionLocal
from app.domain.models import FinanceOutboxEvent

logger = logging.getLogger(__name__)


def handle_event(envelope):
    logger.info("finance_event_received type=%s id=%s", envelope.event_type, envelope.event_id)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(
        run_owned_worker(
            service_name="finance-service",
            session_factory=SessionLocal,
            outbox_model=FinanceOutboxEvent,
            handler=handle_event,
        )
    )


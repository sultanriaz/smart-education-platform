"""Owned Academic outbox and durable Identity lifecycle subscriber."""

import asyncio
import logging
from uuid import UUID

from smartedu_infra.runtime import run_owned_worker
from sqlalchemy import select

from app.db.session import SessionLocal
from app.domain.models import IdentityEligibilityInbox, OutboxEvent
from app.services.academic import AcademicService
from app.services.identity_accounts import IdentityAccountClient

logger = logging.getLogger(__name__)


def handle_identity_eligibility(envelope):
    if envelope.source != "identity-service" or envelope.event_type != "identity.account_eligibility_changed":
        raise ValueError("Unexpected event source or event type")
    user_id = UUID(str(envelope.data["user_id"]))
    if str(user_id) != str(envelope.subject):
        raise ValueError("Identity event subject does not match payload")
    with SessionLocal() as db:
        if db.get(IdentityEligibilityInbox, envelope.event_id) is not None:
            return
        # Marker and Academic changes commit in the same transaction.
        db.add(IdentityEligibilityInbox(event_id=envelope.event_id, user_id=user_id))
        result = AcademicService(
            db, identity_accounts=IdentityAccountClient.from_environment()
        ).reconcile_identity(user_id)
        logger.info("identity_eligibility_reconciled event=%s counters=%s", envelope.event_id, result)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_owned_worker(
        service_name="academic-service", session_factory=SessionLocal,
        outbox_model=OutboxEvent, handler=handle_identity_eligibility,
    ))

"""Real RabbitMQ ingestion, encrypted security email, and delivery retries."""

import asyncio
import logging
import os
from datetime import UTC, datetime

from smartedu_infra.runtime import SECURITY_EVENTS, run_owned_worker
from sqlalchemy import or_, select

from app.db.session import SessionLocal
from app.domain.models import DeliveryAttempt, InboxEvent, OutboxEvent
from app.providers.email import get_email_provider
from app.schemas.notification import InternalEventIn
from app.services.delivery_service import DeliveryService
from app.services.event_service import EventService
from app.sprint18_security_events import security_email_from_event


def handle(envelope):
    with SessionLocal() as db:
        service = EventService(db)
        inbox, _duplicate = service.ingest(
            InternalEventIn(
                event_id=str(envelope.event_id),
                source_service=envelope.source,
                event_type=envelope.event_type,
                occurred_at=envelope.occurred_at,
                payload=envelope.data,
                targets=envelope.metadata.get("targets", {}),
            )
        )
        if envelope.event_type in SECURITY_EVENTS:
            # The database retains only ciphertext. Decrypt in memory immediately
            # before SMTP; never create an in-app notification containing a token.
            inbox = db.scalar(select(InboxEvent).where(InboxEvent.id == inbox.id).with_for_update())
            if inbox.status == "PROCESSED":
                return
            email = security_email_from_event(
                envelope,
                frontend_public_url=os.environ["FRONTEND_PUBLIC_URL"],
                encryption_key=os.environ["SECURITY_NOTIFICATION_ENCRYPTION_KEY"],
            )
            get_email_provider().send(
                to_email=email.recipient, subject=email.subject, body=email.body
            )
            inbox.status, inbox.error, inbox.processed_at = "PROCESSED", None, datetime.now(UTC)
            db.commit()
        else:
            service.process(inbox.id)


def maintenance():
    # Covers API-created attempts and persisted retries after worker restarts.
    # Each attempt is locked and committed by DeliveryService independently.
    with SessionLocal() as db:
        ids = list(
            db.scalars(
                select(DeliveryAttempt.id)
                .where(
                    DeliveryAttempt.status == "PENDING",
                    or_(
                        DeliveryAttempt.next_attempt_at.is_(None),
                        DeliveryAttempt.next_attempt_at <= datetime.now(UTC),
                    ),
                )
                .order_by(DeliveryAttempt.created_at)
                .limit(10)
            )
        )
    for attempt_id in ids:
        with SessionLocal() as db:
            DeliveryService(db).deliver(attempt_id)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(
        run_owned_worker(
            service_name="notification-service",
            session_factory=SessionLocal,
            outbox_model=OutboxEvent,
            handler=handle,
            maintenance=maintenance,
        )
    )

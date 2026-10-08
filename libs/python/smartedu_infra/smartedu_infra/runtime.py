"""Service-owned durable event runtime; callers supply their own session/model.

Publication is at least once. A confirmed publish followed by a process crash
can repeat an event; consumers must commit their inbox and business effect
atomically. No domain ORM is imported by this shared module.
"""

from __future__ import annotations

import asyncio
import logging
import random
import signal
from datetime import UTC, datetime, timedelta

from smartedu_contracts import EventEnvelope
from sqlalchemy import DateTime, Integer, String, or_, select
from sqlalchemy.orm import Mapped, mapped_column

from .messaging import RabbitEventBus
from .settings import MessagingSettings

logger = logging.getLogger(__name__)
MAX_RELAY_ATTEMPTS = 10

SECURITY_EVENTS = ("identity.password_reset.requested", "identity.email_verification.requested")
SUBSCRIPTIONS = {
    "notification-service": SECURITY_EVENTS
    + (
        "attendance.low_attendance_detected",
        "schedule.created",
        "schedule.updated",
        "schedule.cancelled",
        "schedule.occurrence_changed",
        "facility.booking_requested",
        "facility.booking_approved",
        "facility.booking_rejected",
        "facility.booking_cancelled",
        "assessment.quiz_assigned",
        "assessment.attempt_graded",
        "learning.resource_published",
    ),
    "reporting-service": (
        "academic.#",
        "attendance.#",
        "assessment.#",
        "facility.#",
        "notification.#",
        "schedule.#",
    ),
    "platform-service": (
        "academic.#",
        "attendance.#",
        "assessment.#",
        "facility.#",
        "learning.#",
        "notification.#",
        "schedule.#",
        "platform.#",
        "audit.#",
    ),
}


class RelayState:
    """Persist failures separately from the immutable domain event payload."""

    relay_attempts: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    relay_retry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    relay_error: Mapped[str | None] = mapped_column(String(240), nullable=True)


def envelope_from_row(row, service_name: str) -> EventEnvelope:
    occurred = getattr(row, "occurred_at", None) or row.created_at
    if occurred.tzinfo is None:
        occurred = occurred.replace(tzinfo=UTC)
    payload = dict(row.payload or {})
    return EventEnvelope(
        event_id=row.id,
        event_type=row.event_type,
        source=service_name,
        occurred_at=occurred,
        correlation_id=str(payload.get("correlation_id") or row.id),
        subject=str(row.aggregate_id),
        data=payload,
        metadata={"targets": getattr(row, "targets", None) or {}},
    )


async def relay_once(bus, session_factory, model, service_name: str) -> bool:
    """Lock one owned row through the bounded broker confirmation.

    SKIP LOCKED permits multiple worker replicas. A failure is retained with
    backoff; ten failures quarantine the row for explicit operator review.
    """
    now = datetime.now(UTC)
    attendance = hasattr(model, "available_at")
    attempts = model.attempts if attendance else model.relay_attempts
    retry_at = model.available_at if attendance else model.relay_retry_at
    with session_factory() as db:
        query = (
            select(model)
            .where(
                model.published_at.is_(None),
                attempts < MAX_RELAY_ATTEMPTS,
                or_(retry_at.is_(None), retry_at <= now),
            )
            .order_by(model.id)
            .limit(1)
            .with_for_update(skip_locked=True)
        )
        if attendance:
            query = query.where(or_(model.locked_until.is_(None), model.locked_until <= now))
        row = db.scalar(query)
        if row is None:
            return False
        count = (getattr(row, "attempts" if attendance else "relay_attempts") or 0) + 1
        setattr(row, "attempts" if attendance else "relay_attempts", count)
        try:
            await bus.publish(envelope_from_row(row, service_name))
        except Exception as exc:
            # Only the exception class is stored/logged; broker exceptions can
            # contain credentials or sensitive event content in their strings.
            retry = now + timedelta(seconds=min(300, 2**count) + random.random())
            setattr(row, "available_at" if attendance else "relay_retry_at", retry)
            setattr(row, "last_error" if attendance else "relay_error", type(exc).__name__)
            logger.warning(
                "outbox_publish_failed service=%s event_id=%s attempt=%s error=%s",
                service_name,
                row.id,
                count,
                type(exc).__name__,
            )
        else:
            row.published_at = datetime.now(UTC)
            setattr(row, "last_error" if attendance else "relay_error", None)
        db.commit()
        return True


async def run_owned_worker(
    *, service_name, session_factory, outbox_model=None, handler=None, maintenance=None
):
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop.set)
        except NotImplementedError:
            signal.signal(sig, lambda *_: loop.call_soon_threadsafe(stop.set))
    bus = RabbitEventBus(service_name=service_name, settings=MessagingSettings())
    await asyncio.wait_for(bus.connect(), timeout=15)
    # Create all queues before any publisher runs so events survive a stopped
    # consumer, including the first start of a fresh local environment.
    for consumer, keys in SUBSCRIPTIONS.items():
        topology = RabbitEventBus(service_name=consumer, settings=MessagingSettings())
        try:
            await topology.declare_consumer_queue(keys)
        finally:
            await topology.close()
    if handler:

        async def consume(envelope):
            await asyncio.to_thread(handler, envelope)

        await bus.consume(SUBSCRIPTIONS[service_name], consume)
    logger.info("event_worker_ready service=%s", service_name)
    try:
        while not stop.is_set():
            try:
                worked = (
                    await relay_once(bus, session_factory, outbox_model, service_name)
                    if outbox_model
                    else False
                )
                if maintenance:
                    await asyncio.to_thread(maintenance)
            except Exception as exc:
                logger.error(
                    "event_worker_iteration_failed service=%s error=%s",
                    service_name,
                    type(exc).__name__,
                )
                worked = False
            try:
                await asyncio.wait_for(stop.wait(), timeout=0.05 if worked else 0.5)
            except TimeoutError:
                pass
    finally:
        await bus.close()

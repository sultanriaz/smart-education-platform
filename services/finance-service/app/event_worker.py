"""Finance service durable event worker: outbox relay, idempotent consumer, and overdue scheduler."""
from __future__ import annotations

import asyncio
import logging
import time
import uuid
from datetime import UTC, datetime
from sqlalchemy import select
from smartedu_infra.runtime import run_owned_worker

from app.db.session import SessionLocal
from app.domain.models import (
    FeeStructure,
    FinanceAuditEvent,
    FinanceInboxEvent,
    FinanceOutboxEvent,
    Invoice,
    StudentFinancialAccount,
)
from app.services.invoice_service import InvoiceService

logger = logging.getLogger(__name__)
_LAST_MAINTENANCE_SCAN = 0.0


def handle_event(envelope):
    """Durable, idempotent consumer for domain events received by Finance Service."""
    event_id = uuid.UUID(str(envelope.event_id)) if not isinstance(envelope.event_id, uuid.UUID) else envelope.event_id
    event_type = str(envelope.event_type)
    source = str(envelope.source)
    data = envelope.data or {}

    with SessionLocal() as db:
        # Idempotency check: if this event has already been committed to the inbox, skip processing
        already_processed = db.scalar(
            select(FinanceInboxEvent).where(FinanceInboxEvent.event_id == event_id)
        )
        if already_processed:
            logger.info("finance_event_duplicate_skipped event_id=%s type=%s", event_id, event_type)
            return

        logger.info("finance_event_processing event_id=%s type=%s from=%s", event_id, event_type, source)

        if event_type in ("academic.enrollment.created.v1", "academic.student.enrolled.v1", "academic.enrollment.created"):
            # Academic enrollment event -> provision Student Financial Account
            student_id_raw = data.get("student_user_id") or data.get("student_id")
            if student_id_raw:
                try:
                    student_user_id = uuid.UUID(str(student_id_raw))
                    inv_svc = InvoiceService(db)
                    account = inv_svc.get_or_create_account(student_user_id)
                    logger.info("finance_student_account_ready student_id=%s account=%s", student_user_id, account.account_number)

                    # If program_id and semester are provided, prepare fee structure
                    program_id_raw = data.get("program_id")
                    acad_year_id_raw = data.get("academic_year_id")
                    semester = data.get("semester_number") or 1
                    if program_id_raw and acad_year_id_raw:
                        prog_id = uuid.UUID(str(program_id_raw))
                        year_id = uuid.UUID(str(acad_year_id_raw))
                        struct = inv_svc.fee_svc.find_fee_structure(prog_id, year_id, int(semester))
                        if struct:
                            # Idempotently check if invoice already created
                            existing_inv = db.scalar(
                                select(Invoice).where(
                                    Invoice.student_user_id == student_user_id,
                                    Invoice.program_id == prog_id,
                                    Invoice.academic_year_id == year_id,
                                    Invoice.semester_number == int(semester),
                                    Invoice.status != "CANCELLED",
                                )
                            )
                            if not existing_inv:
                                inv = inv_svc.create_invoice(
                                    student_user_id=student_user_id,
                                    program_id=prog_id,
                                    academic_year_id=year_id,
                                    semester_number=int(semester),
                                )
                                logger.info("finance_enrollment_invoice_generated invoice=%s student=%s", inv.invoice_number, student_user_id)
                except Exception as exc:
                    logger.error("finance_enrollment_handling_failed error=%s", type(exc).__name__, exc_info=True)

        elif event_type.startswith("finance.payment."):
            # Payment domain event logging/internal verification
            logger.info("finance_payment_event_acknowledged aggregate_id=%s", envelope.subject)

        # Mark event as processed in inbox
        inbox_record = FinanceInboxEvent(
            event_id=event_id,
            source_service=source,
            event_type=event_type,
            processed_at=datetime.now(UTC),
        )
        db.add(inbox_record)
        db.commit()
        logger.info("finance_event_processed_successfully event_id=%s", event_id)


def maintenance():
    """Durable, periodic maintenance hook for overdue invoices and penalty scheduling."""
    global _LAST_MAINTENANCE_SCAN
    now = time.monotonic()
    # Run scan every 30 seconds
    if now - _LAST_MAINTENANCE_SCAN < 30.0:
        return
    _LAST_MAINTENANCE_SCAN = now

    try:
        with SessionLocal() as db:
            inv_svc = InvoiceService(db)
            result = inv_svc.process_overdue_invoices()
            if result.get("processed_count", 0) > 0:
                logger.info(
                    "finance_maintenance_penalties_applied count=%s total=%s",
                    result["processed_count"],
                    result["total_penalty_assessed"],
                )
    except Exception as exc:
        logger.error("finance_maintenance_failed error=%s", type(exc).__name__, exc_info=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(
        run_owned_worker(
            service_name="finance-service",
            session_factory=SessionLocal,
            outbox_model=FinanceOutboxEvent,
            handler=handle_event,
            maintenance=maintenance,
        )
    )

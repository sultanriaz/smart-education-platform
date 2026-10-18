"""Payroll service durable event worker: outbox relay and idempotent event subscriber."""
from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import UTC, datetime

from smartedu_infra.runtime import run_owned_worker
from sqlalchemy import select

from app.db.session import SessionLocal
from app.domain.models import (
    EmployeePayrollProfile,
    PayrollInboxEvent,
    PayrollOutboxEvent,
)
from app.services.payroll_service import PayrollService

logger = logging.getLogger(__name__)


def handle_event(envelope):
    """Durable, idempotent consumer for domain events received by Payroll Service."""
    event_id = uuid.UUID(str(envelope.event_id)) if not isinstance(envelope.event_id, uuid.UUID) else envelope.event_id
    event_type = str(envelope.event_type)
    source = str(envelope.source)
    data = envelope.data or {}

    with SessionLocal() as db:
        # Idempotency check: if already processed, skip
        already_processed = db.scalar(
            select(PayrollInboxEvent).where(PayrollInboxEvent.event_id == event_id)
        )
        if already_processed:
            logger.info("payroll_event_duplicate_skipped event_id=%s type=%s", event_id, event_type)
            return

        logger.info("payroll_event_processing event_id=%s type=%s from=%s", event_id, event_type, source)

        if event_type in ("identity.user.created.v1", "identity.user.created"):
            # Check if this user needs an employee profile provisioned
            user_id_raw = data.get("user_id") or data.get("id")
            roles = data.get("roles") or []
            role = data.get("role") or ""
            is_employee = any(
                r in ("teacher", "faculty", "staff", "admin", "payroll_officer", "accountant")
                for r in (roles if isinstance(roles, list) else [role])
            )

            if user_id_raw and is_employee:
                try:
                    uid = uuid.UUID(str(user_id_raw))
                    existing = db.scalar(
                        select(EmployeePayrollProfile).where(EmployeePayrollProfile.user_id == uid)
                    )
                    if not existing:
                        email = data.get("email") or f"user_{uid.hex[:8]}@smartedu.local"
                        full_name = data.get("full_name") or data.get("name") or "Employee " + uid.hex[:6]
                        emp_num = f"EMP-{uid.hex[:6].upper()}"
                        svc = PayrollService(db)
                        svc.create_employee_profile(
                            user_id=uid,
                            employee_number=emp_num,
                            full_name=full_name,
                            email=email,
                            designation="Staff" if "teacher" not in roles else "Faculty",
                            employment_type="FULL_TIME",
                            bank_name="Simulated Payroll Partner Bank",
                            bank_account_number=f"PK-{uuid.uuid4().hex[:12].upper()}",
                        )
                        logger.info("payroll_profile_provisioned user_id=%s emp=%s", uid, emp_num)
                except Exception as exc:
                    logger.error("payroll_user_created_handling_failed error=%s", type(exc).__name__, exc_info=True)

        elif event_type in ("payroll.disbursement.retry.v1",):
            record_id_raw = data.get("record_id")
            if record_id_raw:
                try:
                    rec_id = uuid.UUID(str(record_id_raw))
                    svc = PayrollService(db)
                    rec = svc.retry_disbursement_record(
                        record_id=rec_id,
                        corrected_bank_name=data.get("corrected_bank_name"),
                        corrected_account_number=data.get("corrected_account_number"),
                    )
                    logger.info("payroll_disbursement_retry_executed record_id=%s new_ref=%s", rec.id, rec.simulated_reference)
                except Exception as exc:
                    logger.error("payroll_disbursement_retry_failed error=%s", type(exc).__name__, exc_info=True)

        # Mark processed in inbox
        inbox_record = PayrollInboxEvent(
            event_id=event_id,
            source_service=source,
            event_type=event_type,
            processed_at=datetime.now(UTC),
        )
        db.add(inbox_record)
        db.commit()
        logger.info("payroll_event_processed_successfully event_id=%s", event_id)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(
        run_owned_worker(
            service_name="payroll-service",
            session_factory=SessionLocal,
            outbox_model=PayrollOutboxEvent,
            handler=handle_event,
        )
    )

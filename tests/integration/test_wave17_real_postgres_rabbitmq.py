"""Real PostgreSQL and RabbitMQ integration tests for Wave 17 Finance and Payroll.

Verifies:
1. Automatic enrollment-to-invoice processing in real finance_db
2. Real inbox deduplication preventing duplicate records
3. Worker restart recovery and state continuity
4. Durable overdue invoice processing with balanced double-entry accounting
5. Real RabbitMQ messaging connectivity and exchange topology
"""
from __future__ import annotations

import os
import sys
import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import aio_pika
import pytest
from dotenv import dotenv_values
from sqlalchemy import select
from sqlalchemy.orm import Session

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME = REPO_ROOT / ".integration/runtime"

# Ensure environment variables from finance-service.env are loaded before importing app config
env_file = RUNTIME / "finance-service.env"
if env_file.exists():
    for k, v in dotenv_values(env_file).items():
        if v is not None:
            os.environ[k] = v

# Add libs and finance-service to sys.path
sys.path.insert(0, str(REPO_ROOT / "libs/python/smartedu_contracts"))
sys.path.insert(0, str(REPO_ROOT / "libs/python/smartedu_infra"))
sys.path.insert(0, str(REPO_ROOT / "services/finance-service"))

from smartedu_contracts import EventEnvelope, new_event
from app.db.session import SessionLocal
from app.domain.models import (
    FeeComponent,
    FeeStructure,
    FinanceAuditEvent,
    FinanceInboxEvent,
    FinanceOutboxEvent,
    Invoice,
    JournalEntry,
    JournalLine,
    StudentFinancialAccount,
)
from app.event_worker import handle_event as finance_handle_event
from app.services.invoice_service import InvoiceService


@pytest.fixture(scope="module")
def finance_db_session():
    """Real PostgreSQL session connected to finance_db using live credentials."""
    with SessionLocal() as session:
        yield session


@pytest.mark.asyncio
async def test_real_rabbitmq_broker_connectivity():
    """Verify live connectivity and exchange readiness with RabbitMQ container."""
    cfg = dotenv_values(RUNTIME / "finance-service.env")
    amqp_url = cfg.get("RABBITMQ_URL")
    if not amqp_url:
        pytest.skip("RABBITMQ_URL not configured")

    connection = await aio_pika.connect_robust(amqp_url)
    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            "smartedu.events", aio_pika.ExchangeType.TOPIC, durable=True
        )
        assert exchange is not None
        assert not connection.is_closed


def test_real_postgres_enrollment_to_invoice_and_deduplication(finance_db_session: Session):
    """Test enrollment event processing, account creation, and inbox deduplication on real PostgreSQL."""
    student_id = uuid.uuid4()
    program_id = uuid.uuid4()
    year_id = uuid.uuid4()
    event_id = uuid.uuid4()

    # Pre-create a FeeStructure with FeeComponent for this program and year in finance_db
    struct = FeeStructure(
        id=uuid.uuid4(),
        name=f"CS Curriculum Semester 1 - {student_id.hex[:4]}",
        program_id=program_id,
        academic_year_id=year_id,
        semester_number=1,
        is_active=True,
    )
    comp = FeeComponent(
        fee_structure_id=struct.id,
        name="Tuition Fee",
        component_type="TUITION",
        amount=Decimal("60000.00"),
    )
    struct.components.append(comp)
    finance_db_session.add(struct)
    finance_db_session.commit()

    envelope = new_event(
        event_type="academic.enrollment.created.v1",
        source="academic-service",
        data={
            "student_user_id": str(student_id),
            "program_id": str(program_id),
            "academic_year_id": str(year_id),
            "semester_number": 1,
        },
    )
    envelope.event_id = event_id

    # 1. Process event first time
    finance_handle_event(envelope)

    # Assert StudentFinancialAccount exists in real database
    account = finance_db_session.scalar(
        select(StudentFinancialAccount).where(StudentFinancialAccount.student_user_id == student_id)
    )
    assert account is not None
    assert account.account_number.startswith("SFA-")
    assert account.total_invoiced == Decimal("60000.00")
    assert account.outstanding_balance == Decimal("60000.00")

    # Assert Invoice exists in real database
    invoice = finance_db_session.scalar(
        select(Invoice).where(
            Invoice.student_user_id == student_id,
            Invoice.program_id == program_id,
            Invoice.status != "CANCELLED",
        )
    )
    assert invoice is not None
    assert invoice.total_amount == Decimal("60000.00")
    assert invoice.balance_amount == Decimal("60000.00")
    assert invoice.status == "ISSUED"

    # Assert Inbox event was recorded in real database
    inbox = finance_db_session.scalar(
        select(FinanceInboxEvent).where(FinanceInboxEvent.event_id == event_id)
    )
    assert inbox is not None
    assert inbox.source_service == "academic-service"

    # 2. Re-dispatch the EXACT same event (Deduplication Check)
    finance_handle_event(envelope)

    # Verify that no duplicate invoices or accounts were created
    all_invoices = finance_db_session.scalars(
        select(Invoice).where(Invoice.student_user_id == student_id)
    ).all()
    assert len(all_invoices) == 1, "Duplicate invoice was created on repeated event dispatch"

    all_accounts = finance_db_session.scalars(
        select(StudentFinancialAccount).where(StudentFinancialAccount.student_user_id == student_id)
    ).all()
    assert len(all_accounts) == 1, "Duplicate financial account was created on repeated event dispatch"


def test_real_postgres_worker_restart_recovery(finance_db_session: Session):
    """Simulate worker restart and prove continuity of event processing."""
    # Worker restarts: close session and establish new session
    finance_db_session.close()

    new_student_id = uuid.uuid4()
    new_event_id = uuid.uuid4()
    envelope = new_event(
        event_type="academic.enrollment.created.v1",
        source="academic-service",
        data={"student_user_id": str(new_student_id)},
    )
    envelope.event_id = new_event_id

    # Process through restarted worker
    finance_handle_event(envelope)

    # Re-verify through fresh database session
    with SessionLocal() as db:
        acct = db.scalar(
            select(StudentFinancialAccount).where(StudentFinancialAccount.student_user_id == new_student_id)
        )
        assert acct is not None
        assert acct.account_number.startswith("SFA-")


def test_real_postgres_durable_overdue_processing(finance_db_session: Session):
    """Verify overdue maintenance scheduler, late fee assessment, and balanced accounting in real PostgreSQL."""
    student_id = uuid.uuid4()
    inv_svc = InvoiceService(finance_db_session)
    acct = inv_svc.get_or_create_account(student_id)

    # Create an invoice due 20 days ago (past the 10-day grace period)
    due_date = date.today() - timedelta(days=20)
    program_id = uuid.uuid4()
    year_id = uuid.uuid4()
    inv = Invoice(
        id=uuid.uuid4(),
        invoice_number=f"INV-TEST-OD-{uuid.uuid4().hex[:6].upper()}",
        account_id=acct.id,
        student_user_id=student_id,
        program_id=program_id,
        academic_year_id=year_id,
        semester_number=1,
        subtotal=Decimal("40000.00"),
        issue_date=due_date - timedelta(days=30),
        due_date=due_date,
        total_amount=Decimal("40000.00"),
        paid_amount=Decimal("0.00"),
        balance_amount=Decimal("40000.00"),
        status="ISSUED",
        late_fee_applied=False,
    )
    finance_db_session.add(inv)
    acct.outstanding_balance += Decimal("40000.00")
    acct.total_invoiced += Decimal("40000.00")
    finance_db_session.commit()

    # Run overdue processing with standard defaults (10-day grace, flat PKR 500 fee)
    result = inv_svc.process_overdue_invoices()

    assert result["processed_count"] >= 1
    assert str(inv.id) in result["invoice_ids"]

    # Re-fetch invoice and assert updated money state
    finance_db_session.refresh(inv)
    finance_db_session.refresh(acct)

    assert inv.late_fee_applied is True
    assert inv.late_fee_amount == Decimal("500.00")
    assert inv.status == "OVERDUE"
    assert inv.total_amount == Decimal("40500.00")
    assert inv.balance_amount == Decimal("40500.00")

    # Assert outbox notification was persisted in real PostgreSQL
    outbox = finance_db_session.scalar(
        select(FinanceOutboxEvent).where(
            FinanceOutboxEvent.aggregate_id == inv.id,
            FinanceOutboxEvent.event_type == "finance.invoice.overdue.v1",
        )
    )
    assert outbox is not None
    assert outbox.payload["late_fee_amount"] == "500.00"

    # Assert balanced General Ledger entry was persisted in real PostgreSQL
    journal = finance_db_session.scalar(
        select(JournalEntry).where(JournalEntry.reference == f"LATE_FEE:{inv.invoice_number}")
    )
    assert journal is not None
    total_debits = sum(l.debit for l in journal.lines)
    total_credits = sum(l.credit for l in journal.lines)
    assert total_debits == total_credits == Decimal("500.00")
    assert len(journal.lines) == 2

    # Assert idempotent repeated run
    repeat_result = inv_svc.process_overdue_invoices()
    assert str(inv.id) not in repeat_result["invoice_ids"]
    assert inv.balance_amount == Decimal("40500.00")  # Not double charged

"""Tests for Maker-Checker segregation, failure simulation, duplicate payout prevention, and reconciliation."""
import uuid
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from app.core.errors import PayrollDomainError
from app.domain.models import (
    DisbursementBatch,
    DisbursementRecord,
    EmployeePayrollProfile,
    PayrollPeriod,
    PayrollRun,
    PayrollRunItem,
)
from app.services.payroll_service import PayrollService


def test_maker_checker_violation():
    mock_db = MagicMock()
    maker_id = uuid.uuid4()
    run_id = uuid.uuid4()

    run = PayrollRun(
        id=run_id,
        created_by_user_id=maker_id,
        status="CALCULATED",
        total_gross=Decimal("150000.00"),
        total_net=Decimal("130000.00"),
    )
    mock_db.scalar.return_value = run

    svc = PayrollService(mock_db)
    # The maker attempts to approve their own run
    with pytest.raises(PayrollDomainError) as exc_info:
        svc.approve_payroll_run(
            run_id=run_id,
            approved_by_user_id=maker_id,
            approved=True,
        )

    assert "Maker-checker violation" in str(exc_info.value)


def test_maker_checker_approval_success():
    mock_db = MagicMock()
    maker_id = uuid.uuid4()
    checker_id = uuid.uuid4()
    run_id = uuid.uuid4()

    run = PayrollRun(
        id=run_id,
        created_by_user_id=maker_id,
        period_id=uuid.uuid4(),
        status="CALCULATED",
        total_gross=Decimal("150000.00"),
        total_net=Decimal("130000.00"),
    )
    mock_db.scalar.return_value = run
    mock_db.scalars.return_value.all.return_value = []

    svc = PayrollService(mock_db)
    approved_run = svc.approve_payroll_run(
        run_id=run_id,
        approved_by_user_id=checker_id,
        approved=True,
        notes="All numbers verified against attendance",
    )

    assert approved_run.status == "APPROVED"
    assert approved_run.approved_by_user_id == checker_id
    assert approved_run.approved_at is not None


def test_cannot_disburse_unapproved_run():
    mock_db = MagicMock()
    run_id = uuid.uuid4()
    run = PayrollRun(
        id=run_id,
        status="CALCULATED",  # Not approved yet
        total_net=Decimal("100000.00"),
    )
    mock_db.scalar.return_value = run

    svc = PayrollService(mock_db)
    with pytest.raises(PayrollDomainError) as exc_info:
        svc.execute_disbursements(run_id=run_id)

    assert "Only APPROVED payroll runs can be disbursed" in str(exc_info.value)


def test_disbursement_failure_simulation():
    mock_db = MagicMock()
    run_id = uuid.uuid4()
    run = PayrollRun(
        id=run_id,
        status="APPROVED",
        total_net=Decimal("120000.00"),
    )
    mock_db.scalar.return_value = run

    profile1 = EmployeePayrollProfile(
        id=uuid.uuid4(),
        full_name="Dr. Tariq",
        bank_name="HBL",
        bank_account_number="11112222",
    )
    profile2 = EmployeePayrollProfile(
        id=uuid.uuid4(),
        full_name="Prof. Sarah",
        bank_name="Meezan Bank",
        bank_account_number="33334444",
    )

    item1 = PayrollRunItem(
        id=uuid.uuid4(),
        payroll_run_id=run.id,
        employee_profile_id=profile1.id,
        employee_profile=profile1,
        net_salary=Decimal("60000.00"),
    )
    item2 = PayrollRunItem(
        id=uuid.uuid4(),
        payroll_run_id=run.id,
        employee_profile_id=profile2.id,
        employee_profile=profile2,
        net_salary=Decimal("60000.00"),
    )
    mock_db.scalars.return_value.all.return_value = [item1, item2]

    svc = PayrollService(mock_db)
    # Simulate failures on profile1
    batch = svc.execute_disbursements(
        run_id=run_id,
        simulate_failures=True,
        fail_employee_ids=[profile1.id],
    )

    assert batch.failed_count == 1
    assert batch.status == "PARTIAL_FAILURE"
    assert run.status == "DISBURSEMENT_PARTIAL"


def test_duplicate_payout_prevention():
    mock_db = MagicMock()
    record_id = uuid.uuid4()

    settled_record = DisbursementRecord(
        id=record_id,
        status="SUCCESS",
        simulated_reference="SIM-PAYOUT-ALREADY-SETTLED",
        amount=Decimal("75000.00"),
    )
    mock_db.scalar.return_value = settled_record

    svc = PayrollService(mock_db)
    # Attempting to retry an already settled payout must fail-closed
    with pytest.raises(PayrollDomainError) as exc_info:
        svc.retry_disbursement_record(record_id=record_id)

    assert "Duplicate payout prevented" in str(exc_info.value)


def test_individual_failed_record_retry_success():
    mock_db = MagicMock()
    batch_id = uuid.uuid4()
    record_id = uuid.uuid4()
    run_id = uuid.uuid4()

    failed_record = DisbursementRecord(
        id=record_id,
        batch_id=batch_id,
        status="FAILED",
        simulated_reference="SIM-FAIL-1234",
        error_message="Invalid beneficiary details",
        retry_count=0,
        amount=Decimal("50000.00"),
    )
    batch = DisbursementBatch(
        id=batch_id,
        payroll_run_id=run_id,
        batch_number="DISB-202610-001",
        status="PARTIAL_FAILURE",
        failed_count=1,
    )
    run = PayrollRun(
        id=run_id,
        status="DISBURSEMENT_PARTIAL",
    )

    # Database returns record, then batch, then run
    mock_db.scalar.side_effect = [failed_record, batch, run]
    # All records check in batch returns [failed_record] which becomes SUCCESS
    mock_db.scalars.return_value.all.return_value = [failed_record]

    svc = PayrollService(mock_db)
    retried_record = svc.retry_disbursement_record(
        record_id=record_id,
        corrected_bank_name="Updated Partner Bank",
        corrected_account_number="PK99TEST987654",
    )

    assert retried_record.status == "SUCCESS"
    assert retried_record.retry_count == 1
    assert retried_record.error_message is None
    assert retried_record.simulated_reference.startswith("SIM-RETRY-")
    assert retried_record.bank_name == "Updated Partner Bank"
    assert batch.failed_count == 0
    assert batch.status == "COMPLETED"
    assert run.status == "PAID"


def test_batch_reconciliation():
    mock_db = MagicMock()
    batch_id = uuid.uuid4()

    batch = DisbursementBatch(
        id=batch_id,
        batch_number="DISB-TEST-REC",
        status="COMPLETED",
        reconciled_count=0,
        failed_count=0,
    )
    rec1 = DisbursementRecord(
        id=uuid.uuid4(),
        batch_id=batch_id,
        status="SUCCESS",
        amount=Decimal("40000.00"),
        reconciled=False,
    )
    rec2 = DisbursementRecord(
        id=uuid.uuid4(),
        batch_id=batch_id,
        status="SUCCESS",
        amount=Decimal("45000.00"),
        reconciled=False,
    )

    mock_db.scalar.return_value = batch
    mock_db.scalars.return_value.all.return_value = [rec1, rec2]

    svc = PayrollService(mock_db)
    result = svc.reconcile_disbursement_batch(batch_id=batch_id)

    assert result["total_records"] == 2
    assert result["reconciled_count"] == 2
    assert result["status"] == "COMPLETED"
    assert rec1.reconciled is True
    assert rec2.reconciled is True
    assert rec1.reconciled_at is not None
    assert rec2.reconciled_at is not None

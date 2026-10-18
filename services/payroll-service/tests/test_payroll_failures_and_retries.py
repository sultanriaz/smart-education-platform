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


def test_student_identity_rejected_from_payroll_provisioning():
    from unittest.mock import patch
    from app.event_worker import handle_event

    mock_db = MagicMock()
    mock_db.scalar.return_value = None  # Not in inbox, no existing profile

    envelope = MagicMock()
    envelope.event_id = uuid.uuid4()
    envelope.event_type = "identity.user.created.v1"
    envelope.source = "identity-service"
    envelope.data = {
        "user_id": str(uuid.uuid4()),
        "roles": ["student"],
        "role": "student",
        "full_name": "Ordinary Student",
        "email": "student@smartedu.local",
    }

    with patch("app.event_worker.SessionLocal") as mock_session, \
         patch("app.event_worker.PayrollService") as mock_svc_cls:
        mock_session.return_value.__enter__.return_value = mock_db
        mock_svc = MagicMock()
        mock_svc_cls.return_value = mock_svc

        handle_event(envelope)

        # Profile creation must NOT be called for student
        mock_svc.create_employee_profile.assert_not_called()


def test_authorized_employee_identity_provisions_profile():
    from unittest.mock import patch
    from app.event_worker import handle_event

    mock_db = MagicMock()
    mock_db.scalar.return_value = None  # Not duplicate, not existing

    emp_id = uuid.uuid4()
    envelope = MagicMock()
    envelope.event_id = uuid.uuid4()
    envelope.event_type = "identity.user.created.v1"
    envelope.source = "identity-service"
    envelope.data = {
        "user_id": str(emp_id),
        "roles": ["teacher"],
        "role": "teacher",
        "full_name": "Dr. Sarah Faculty",
        "email": "sarah@smartedu.local",
    }

    with patch("app.event_worker.SessionLocal") as mock_session, \
         patch("app.event_worker.PayrollService") as mock_svc_cls:
        mock_session.return_value.__enter__.return_value = mock_db
        mock_svc = MagicMock()
        mock_svc_cls.return_value = mock_svc

        handle_event(envelope)

        mock_svc.create_employee_profile.assert_called_once()
        call_kwargs = mock_svc.create_employee_profile.call_args.kwargs
        assert call_kwargs["user_id"] == emp_id
        assert call_kwargs["full_name"] == "Dr. Sarah Faculty"
        assert call_kwargs["designation"] == "Faculty"


def test_role_change_event_provisions_unprovisioned_promoted_user():
    from unittest.mock import patch
    from app.event_worker import handle_event

    mock_db = MagicMock()
    mock_db.scalar.return_value = None  # Not in inbox, not already created

    promoted_user_id = uuid.uuid4()
    envelope = MagicMock()
    envelope.event_id = uuid.uuid4()
    envelope.event_type = "identity.user.roles_changed.v1"
    envelope.source = "identity-service"
    envelope.data = {
        "user_id": str(promoted_user_id),
        "roles": ["staff", "accountant"],
        "full_name": "Promoted Staff Member",
        "email": "staff@smartedu.local",
    }

    with patch("app.event_worker.SessionLocal") as mock_session, \
         patch("app.event_worker.PayrollService") as mock_svc_cls:
        mock_session.return_value.__enter__.return_value = mock_db
        mock_svc = MagicMock()
        mock_svc_cls.return_value = mock_svc

        handle_event(envelope)

        mock_svc.create_employee_profile.assert_called_once()
        call_kwargs = mock_svc.create_employee_profile.call_args.kwargs
        assert call_kwargs["user_id"] == promoted_user_id
        assert call_kwargs["full_name"] == "Promoted Staff Member"


def test_duplicate_identity_event_deduplication():
    from unittest.mock import patch
    from app.event_worker import handle_event
    from app.domain.models import PayrollInboxEvent

    mock_db = MagicMock()
    existing_inbox = PayrollInboxEvent(
        id=uuid.uuid4(),
        event_id=uuid.uuid4(),
        event_type="identity.user.created.v1",
        source_service="identity-service",
    )
    # Database returns existing inbox event (deduplication hit)
    mock_db.scalar.return_value = existing_inbox

    envelope = MagicMock()
    envelope.event_id = existing_inbox.event_id
    envelope.event_type = "identity.user.created.v1"
    envelope.source = "identity-service"
    envelope.data = {"user_id": str(uuid.uuid4()), "roles": ["teacher"]}

    with patch("app.event_worker.SessionLocal") as mock_session, \
         patch("app.event_worker.PayrollService") as mock_svc_cls:
        mock_session.return_value.__enter__.return_value = mock_db
        mock_svc = MagicMock()
        mock_svc_cls.return_value = mock_svc

        handle_event(envelope)

        # Due to deduplication, no profile creation and no db.add calls occur
        mock_svc.create_employee_profile.assert_not_called()
        mock_db.add.assert_not_called()


def test_concurrent_disbursement_execution_prevention():
    mock_db = MagicMock()
    run_id = uuid.uuid4()
    # PayrollRun is already in PAID status
    run = PayrollRun(
        id=run_id,
        status="PAID",
        total_net=Decimal("120000.00"),
    )
    mock_db.scalar.return_value = run

    svc = PayrollService(mock_db)
    with pytest.raises(PayrollDomainError) as exc_info:
        svc.execute_disbursements(run_id=run_id)

    assert "Duplicate disbursement prevented" in str(exc_info.value)


def test_uncertain_outcome_requires_reconciliation_before_retry():
    mock_db = MagicMock()
    rec_id = uuid.uuid4()
    uncertain_rec = DisbursementRecord(
        id=rec_id,
        status="UNCERTAIN",
        simulated_reference="SIM-UNCERTAIN-01",
        amount=Decimal("45000.00"),
    )
    mock_db.scalar.return_value = uncertain_rec

    svc = PayrollService(mock_db)
    with pytest.raises(PayrollDomainError) as exc_info:
        svc.retry_disbursement_record(record_id=rec_id)

    assert "must be reconciled before retry" in str(exc_info.value)


def test_uncertain_outcome_reconciliation_without_duplicate_money_state():
    mock_db = MagicMock()
    batch_id = uuid.uuid4()

    batch = DisbursementBatch(
        id=batch_id,
        batch_number="DISB-UNCERTAIN-BATCH",
        status="COMPLETED",
        reconciled_count=0,
    )
    rec1 = DisbursementRecord(
        id=uuid.uuid4(),
        batch_id=batch_id,
        status="UNCERTAIN",
        simulated_reference="SIM-UNCERTAIN-02",
        amount=Decimal("55000.00"),
        reconciled=False,
    )

    mock_db.scalar.return_value = batch
    mock_db.scalars.return_value.all.return_value = [rec1]

    svc = PayrollService(mock_db)
    # First reconciliation: resolves UNCERTAIN -> SUCCESS, reconciles
    res1 = svc.reconcile_disbursement_batch(batch_id=batch_id)
    assert res1["reconciled_count"] == 1
    assert rec1.status == "SUCCESS"
    assert rec1.reconciled is True

    # Second reconciliation: idempotent, 0 additional money changes
    res2 = svc.reconcile_disbursement_batch(batch_id=batch_id)
    assert res2["reconciled_count"] == 1
    # Verify no duplicate disbursement records are ever added
    added_disbursements = [
        call.args[0] for call in mock_db.add.call_args_list if isinstance(call.args[0], DisbursementRecord)
    ]
    assert len(added_disbursements) == 0



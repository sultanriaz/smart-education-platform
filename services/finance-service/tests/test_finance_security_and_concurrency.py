"""Security, concurrency, idempotency, and double-entry integrity tests for Finance Service."""
import hashlib
import hmac
import time
import uuid
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from app.core.errors import FinanceDomainError
from app.domain.models import Invoice, Payment, PaymentIntent, StudentFinancialAccount
from app.services.accounting_service import AccountingService
from app.services.payment_adapters import EasypaisaAdapter, JazzCashAdapter
from app.services.payment_service import PaymentService


def test_callback_hmac_verification_success():
    secret = "test-webhook-secret-key-12345"
    adapter = JazzCashAdapter(secret_key=secret)

    now_ts = time.time()
    payload = {
        "pp_TxnRefNo": "JC-TEST-001",
        "pp_Amount": "5000.00",
        "pp_TxnCurrency": "PKR",
        "pp_TxnDateTime": str(int(now_ts)),
        "pp_BillReference": str(uuid.uuid4()),
        "pp_MerchantID": "SMARTEDU_JC_DEMO",
        "provider": "JAZZ_CASH",
    }
    # Correct signature
    sorted_keys = sorted(k for k in payload.keys() if k != "signature")
    canonical = "&".join(f"{k}={payload[k]}" for k in sorted_keys)
    sig = hmac.new(secret.encode("utf-8"), canonical.encode("utf-8"), hashlib.sha256).hexdigest()

    assert adapter.verify_callback(payload, sig, now_ts) is True


def test_callback_forgery_rejection():
    secret = "test-webhook-secret-key-12345"
    adapter = JazzCashAdapter(secret_key=secret)

    now_ts = time.time()
    payload = {
        "pp_TxnRefNo": "JC-TEST-001",
        "pp_Amount": "5000.00",
        "pp_TxnCurrency": "PKR",
    }
    # Forged signature
    forged_sig = "a" * 64
    assert adapter.verify_callback(payload, forged_sig, now_ts) is False

    # Tampered amount with valid-looking signature
    sorted_keys = sorted(k for k in payload.keys())
    canonical = "&".join(f"{k}={payload[k]}" for k in sorted_keys)
    sig = hmac.new(secret.encode("utf-8"), canonical.encode("utf-8"), hashlib.sha256).hexdigest()

    # Adversary alters amount to 50.00
    payload["pp_Amount"] = "50.00"
    assert adapter.verify_callback(payload, sig, now_ts) is False


def test_callback_replay_prevention_stale_timestamp():
    secret = "test-webhook-secret-key-12345"
    adapter = JazzCashAdapter(secret_key=secret)

    # Replay of a callback from 301 seconds ago
    stale_ts = time.time() - 301.0
    payload = {"pp_TxnRefNo": "JC-TEST-001", "pp_Amount": "1000.00"}
    sorted_keys = sorted(k for k in payload.keys())
    canonical = "&".join(f"{k}={payload[k]}" for k in sorted_keys)
    sig = hmac.new(secret.encode("utf-8"), canonical.encode("utf-8"), hashlib.sha256).hexdigest()

    assert adapter.verify_callback(payload, sig, stale_ts) is False


def test_easypaisa_callback_verification():
    secret = "test-ep-secret-999"
    adapter = EasypaisaAdapter(secret_key=secret)

    now_ts = time.time()
    payload = {
        "orderId": "EP-ORDER-99",
        "storeId": "SMARTEDU_EP_DEMO",
        "transactionAmount": "2500.00",
        "transactionCurrency": "PKR",
        "timestamp": str(int(now_ts)),
        "provider": "EASYPAISA",
    }
    sorted_keys = sorted(k for k in payload.keys() if k != "signature")
    canonical = "&".join(f"{k}={payload[k]}" for k in sorted_keys)
    sig = hmac.new(secret.encode("utf-8"), canonical.encode("utf-8"), hashlib.sha256).hexdigest()

    assert adapter.verify_callback(payload, sig, now_ts) is True

    # Tampered store ID
    payload_tampered = dict(payload)
    payload_tampered["storeId"] = "EVIL_STORE"
    assert adapter.verify_callback(payload_tampered, sig, now_ts) is False


def test_payment_idempotency_duplicate_provider_tx():
    mock_db = MagicMock()
    existing_payment = Payment(
        id=uuid.uuid4(),
        provider_transaction_id="TXN-DUP-001",
        amount=Decimal("1500.00"),
        status="CONFIRMED",
    )
    # Database scalar returns existing payment
    mock_db.scalar.return_value = existing_payment

    svc = PaymentService(mock_db)
    result = svc.confirm_payment(
        payment_intent_id=uuid.uuid4(),
        provider_transaction_id="TXN-DUP-001",
        method="JAZZ_CASH",
    )

    assert result == existing_payment
    assert result.provider_transaction_id == "TXN-DUP-001"
    # Ensure no new records were added to db
    assert mock_db.add.call_count == 0


def test_overpayment_prevention():
    mock_db = MagicMock()
    # First query (scalar for existing payment): None
    # Second query (scalar for intent): PaymentIntent with amount 5000
    # Third query (scalar for invoice): Invoice with balance 2000
    intent = PaymentIntent(
        id=uuid.uuid4(),
        invoice_id=uuid.uuid4(),
        student_user_id=uuid.uuid4(),
        amount=Decimal("5000.00"),
        status="PENDING",
    )
    invoice = Invoice(
        id=intent.invoice_id,
        balance_amount=Decimal("2000.00"),
        paid_amount=Decimal("0.00"),
        total_amount=Decimal("2000.00"),
        status="ISSUED",
    )

    mock_db.scalar.side_effect = [None, intent, invoice]

    svc = PaymentService(mock_db)
    with pytest.raises(FinanceDomainError) as exc_info:
        svc.confirm_payment(
            payment_intent_id=intent.id,
            provider_transaction_id="TXN-OVER-001",
            method="JAZZ_CASH",
        )

    assert "exceeds remaining balance" in str(exc_info.value)


def test_accounting_double_entry_balance_on_payment():
    mock_db = MagicMock()
    accounting = AccountingService(mock_db)

    # Ensure get_or_create_account creates mock Account objects
    def mock_account_lookup(code, name="Mock Account", type_="ASSET"):
        acc = MagicMock()
        acc.id = uuid.uuid4()
        acc.code = code
        acc.name = name
        acc.type = type_
        return acc

    accounting.get_account_by_code = mock_account_lookup

    payment = Payment(
        id=uuid.uuid4(),
        provider_transaction_id="TXN-PAY-12500",
        receipt_number="REC-TEST-001",
        amount=Decimal("12500.00"),
        method="JAZZ_CASH",
        paid_at=None,
    )
    invoice = Invoice(
        id=uuid.uuid4(),
        invoice_number="INV-2026-001",
    )

    entry = accounting.record_payment_receipt(payment, invoice)

    from app.domain.models import JournalLine
    added_lines = [call.args[0] for call in mock_db.add.call_args_list if isinstance(call.args[0], JournalLine)]

    total_debits = sum(l.debit for l in added_lines)
    total_credits = sum(l.credit for l in added_lines)

    assert total_debits == total_credits
    assert total_debits == Decimal("12500.00")
    debit_lines = [l for l in added_lines if l.debit > Decimal("0.00")]
    credit_lines = [l for l in added_lines if l.credit > Decimal("0.00")]
    assert len(debit_lines) == 1
    assert len(credit_lines) == 1
    assert debit_lines[0].debit == Decimal("12500.00")
    assert credit_lines[0].credit == Decimal("12500.00")


def test_overdue_policy_defaults():
    from app.core.config import settings
    assert settings.LATE_FEE_GRACE_DAYS == 10
    assert Decimal(str(settings.LATE_FEE_AMOUNT)) == Decimal("500.00")


def test_overdue_deadline_boundary_within_grace():
    from datetime import date
    from app.services.invoice_service import InvoiceService

    mock_db = MagicMock()
    due = date(2026, 5, 1)
    inv = Invoice(
        id=uuid.uuid4(),
        invoice_number="INV-BOUND-01",
        account_id=uuid.uuid4(),
        student_user_id=uuid.uuid4(),
        due_date=due,
        total_amount=Decimal("50000.00"),
        paid_amount=Decimal("0.00"),
        balance_amount=Decimal("50000.00"),
        status="ISSUED",
        late_fee_applied=False,
    )
    mock_db.scalar.return_value = inv

    svc = InvoiceService(mock_db)
    # Exactly on day 10 of grace (May 11): NOT overdue
    day_10 = date(2026, 5, 11)
    result = svc.apply_late_fee_if_overdue(inv.id, as_of_date=day_10)

    assert result.late_fee_applied is False
    assert result.status == "ISSUED"
    assert result.balance_amount == Decimal("50000.00")


def test_overdue_deadline_boundary_past_grace():
    from datetime import date
    from app.services.invoice_service import InvoiceService

    mock_db = MagicMock()
    due = date(2026, 5, 1)
    inv = Invoice(
        id=uuid.uuid4(),
        invoice_number="INV-BOUND-02",
        account_id=uuid.uuid4(),
        student_user_id=uuid.uuid4(),
        due_date=due,
        total_amount=Decimal("50000.00"),
        paid_amount=Decimal("0.00"),
        balance_amount=Decimal("50000.00"),
        status="ISSUED",
        late_fee_applied=False,
    )
    acct = StudentFinancialAccount(
        id=inv.account_id,
        student_user_id=inv.student_user_id,
        outstanding_balance=Decimal("50000.00"),
        total_invoiced=Decimal("50000.00"),
    )
    mock_db.scalar.side_effect = [inv, acct]

    svc = InvoiceService(mock_db)
    svc.accounting = MagicMock()

    # Day 11 (May 12): 1 day past 10-day grace -> Overdue penalty applied
    day_11 = date(2026, 5, 12)
    result = svc.apply_late_fee_if_overdue(inv.id, as_of_date=day_11)

    assert result.late_fee_applied is True
    assert result.late_fee_amount == Decimal("500.00")
    assert result.status == "OVERDUE"
    assert result.balance_amount == Decimal("50500.00")
    assert result.total_amount == Decimal("50500.00")
    assert acct.outstanding_balance == Decimal("50500.00")
    svc.accounting.record_late_fee.assert_called_once_with(inv, Decimal("500.00"))


def test_overdue_partial_payment_gets_penalized():
    from datetime import date
    from app.services.invoice_service import InvoiceService

    mock_db = MagicMock()
    due = date(2026, 5, 1)
    inv = Invoice(
        id=uuid.uuid4(),
        invoice_number="INV-PARTIAL-01",
        account_id=uuid.uuid4(),
        student_user_id=uuid.uuid4(),
        due_date=due,
        total_amount=Decimal("50000.00"),
        paid_amount=Decimal("20000.00"),
        balance_amount=Decimal("30000.00"),
        status="PARTIALLY_PAID",
        late_fee_applied=False,
    )
    acct = StudentFinancialAccount(
        id=inv.account_id,
        student_user_id=inv.student_user_id,
        outstanding_balance=Decimal("30000.00"),
        total_invoiced=Decimal("50000.00"),
    )
    mock_db.scalar.side_effect = [inv, acct]

    svc = InvoiceService(mock_db)
    svc.accounting = MagicMock()

    # Day 15: overdue
    result = svc.apply_late_fee_if_overdue(inv.id, as_of_date=date(2026, 5, 16))

    assert result.late_fee_applied is True
    assert result.late_fee_amount == Decimal("500.00")
    assert result.status == "OVERDUE"
    assert result.balance_amount == Decimal("30500.00")
    assert result.total_amount == Decimal("50500.00")


def test_overdue_fully_paid_invoice_exempt():
    from datetime import date
    from app.services.invoice_service import InvoiceService

    mock_db = MagicMock()
    due = date(2026, 5, 1)
    inv = Invoice(
        id=uuid.uuid4(),
        invoice_number="INV-PAID-01",
        account_id=uuid.uuid4(),
        student_user_id=uuid.uuid4(),
        due_date=due,
        total_amount=Decimal("50000.00"),
        paid_amount=Decimal("50000.00"),
        balance_amount=Decimal("0.00"),
        status="PAID",
        late_fee_applied=False,
    )
    mock_db.scalar.return_value = inv

    svc = InvoiceService(mock_db)
    result = svc.apply_late_fee_if_overdue(inv.id, as_of_date=date(2026, 5, 20))

    assert result.late_fee_applied is False
    assert result.status == "PAID"
    assert result.balance_amount == Decimal("0.00")


def test_overdue_repeated_scheduler_execution_idempotency():
    from datetime import date
    from app.services.invoice_service import InvoiceService

    mock_db = MagicMock()
    due = date(2026, 5, 1)
    inv = Invoice(
        id=uuid.uuid4(),
        invoice_number="INV-SCHED-01",
        account_id=uuid.uuid4(),
        student_user_id=uuid.uuid4(),
        due_date=due,
        total_amount=Decimal("30000.00"),
        paid_amount=Decimal("0.00"),
        balance_amount=Decimal("30000.00"),
        status="ISSUED",
        late_fee_applied=False,
        installments=[],
    )
    acct = StudentFinancialAccount(
        id=inv.account_id,
        student_user_id=inv.student_user_id,
        outstanding_balance=Decimal("30000.00"),
        total_invoiced=Decimal("30000.00"),
    )
    mock_db.scalar.return_value = acct

    # First run finds 1 unpenalized overdue invoice
    mock_db.scalars.return_value.all.return_value = [inv]

    svc = InvoiceService(mock_db)
    svc.accounting = MagicMock()

    day_20 = date(2026, 5, 21)
    run1 = svc.process_overdue_invoices(as_of_date=day_20)

    assert run1["processed_count"] == 1
    assert Decimal(run1["total_penalty_assessed"]) == Decimal("500.00")
    assert inv.late_fee_applied is True
    assert inv.balance_amount == Decimal("30500.00")

    # Second run finds no candidate invoices (or candidate is already late_fee_applied=True)
    mock_db.scalars.return_value.all.return_value = []
    run2 = svc.process_overdue_invoices(as_of_date=day_20)

    assert run2["processed_count"] == 0
    assert Decimal(run2["total_penalty_assessed"]) == Decimal("0.00")
    # Balance must NOT increase again
    assert inv.balance_amount == Decimal("30500.00")


def test_overdue_versioned_policy_override():
    from datetime import date
    from app.services.invoice_service import InvoiceService

    mock_db = MagicMock()
    due = date(2026, 5, 1)
    inv = Invoice(
        id=uuid.uuid4(),
        invoice_number="INV-POLICY-01",
        account_id=uuid.uuid4(),
        student_user_id=uuid.uuid4(),
        due_date=due,
        total_amount=Decimal("40000.00"),
        paid_amount=Decimal("0.00"),
        balance_amount=Decimal("40000.00"),
        status="ISSUED",
        late_fee_applied=False,
        installments=[],
    )
    acct = StudentFinancialAccount(
        id=inv.account_id,
        student_user_id=inv.student_user_id,
        outstanding_balance=Decimal("40000.00"),
        total_invoiced=Decimal("40000.00"),
    )
    mock_db.scalar.return_value = acct
    mock_db.scalars.return_value.all.return_value = [inv]

    svc = InvoiceService(mock_db)
    svc.accounting = MagicMock()

    # Custom versioned policy: 5 grace days and PKR 750 penalty
    # Day 7 (May 8) > May 1 + 5 days (May 6) -> Overdue under versioned policy
    run = svc.process_overdue_invoices(
        as_of_date=date(2026, 5, 8),
        grace_days=5,
        penalty_amount=Decimal("750.00"),
    )

    assert run["processed_count"] == 1
    assert Decimal(run["total_penalty_assessed"]) == Decimal("750.00")
    assert inv.late_fee_amount == Decimal("750.00")
    assert inv.balance_amount == Decimal("40750.00")


def test_overdue_balanced_accounting_entry():
    mock_db = MagicMock()
    accounting = AccountingService(mock_db)

    def mock_account_lookup(code, name="Mock Account", type_="ASSET"):
        acc = MagicMock()
        acc.id = uuid.uuid4()
        acc.code = code
        acc.name = name
        acc.type = type_
        return acc

    accounting.get_account_by_code = mock_account_lookup

    inv = Invoice(
        id=uuid.uuid4(),
        invoice_number="INV-LATE-001",
    )
    late_penalty = Decimal("500.00")
    entry = accounting.record_late_fee(inv, late_penalty)

    from app.domain.models import JournalLine
    added_lines = [call.args[0] for call in mock_db.add.call_args_list if isinstance(call.args[0], JournalLine)]

    total_debits = sum(l.debit for l in added_lines)
    total_credits = sum(l.credit for l in added_lines)

    assert total_debits == total_credits
    assert total_debits == Decimal("500.00")

    debit_lines = [l for l in added_lines if l.debit > Decimal("0.00")]
    credit_lines = [l for l in added_lines if l.credit > Decimal("0.00")]
    assert len(debit_lines) == 1
    assert len(credit_lines) == 1
    assert debit_lines[0].debit == Decimal("500.00")
    assert credit_lines[0].credit == Decimal("500.00")


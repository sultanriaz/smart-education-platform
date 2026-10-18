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

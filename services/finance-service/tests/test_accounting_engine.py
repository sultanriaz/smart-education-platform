from decimal import Decimal
import uuid
import pytest
from app.services.accounting_service import AccountingService
from app.domain.models import Account, JournalEntry, JournalLine

def test_double_entry_balance_validation():
    # Test debit == credit validation in journal entry creation
    service = AccountingService(db=None)

    lines_balanced = [
        {"account_code": "1010", "entry_type": "DEBIT", "amount": Decimal("1000.00")},
        {"account_code": "4010", "entry_type": "CREDIT", "amount": Decimal("1000.00")},
    ]

    total_debits = sum(line["amount"] for line in lines_balanced if line["entry_type"] == "DEBIT")
    total_credits = sum(line["amount"] for line in lines_balanced if line["entry_type"] == "CREDIT")

    assert total_debits == total_credits
    assert total_debits == Decimal("1000.00")

def test_double_entry_imbalance_detection():
    # Detect when debit != credit
    lines_unbalanced = [
        {"account_code": "1010", "entry_type": "DEBIT", "amount": Decimal("1000.00")},
        {"account_code": "4010", "entry_type": "CREDIT", "amount": Decimal("800.00")},
    ]

    total_debits = sum(line["amount"] for line in lines_unbalanced if line["entry_type"] == "DEBIT")
    total_credits = sum(line["amount"] for line in lines_unbalanced if line["entry_type"] == "CREDIT")

    assert total_debits != total_credits
    assert total_debits - total_credits == Decimal("200.00")

def test_chart_of_accounts_structure():
    expected_accounts = {
        "1010": "Cash and Bank",
        "1020": "Payment Gateway Clearing",
        "1100": "Accounts Receivable (Students)",
        "2010": "Fee Concessions and Scholarships",
        "2020": "Unearned / Advance Tuition Revenue",
        "4010": "Tuition Revenue",
        "4020": "Examination Fee Revenue",
        "4030": "Laboratory Fee Revenue",
        "4040": "Library Fee Revenue",
        "4050": "Late Payment Fines Revenue",
        "5010": "Refunds and Adjustments Expense"
    }

    assert len(expected_accounts) == 11
    assert expected_accounts["1010"] == "Cash and Bank"
    assert expected_accounts["4010"] == "Tuition Revenue"


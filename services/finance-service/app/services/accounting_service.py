from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import FinanceDomainError
from app.domain.models import Account, Invoice, JournalEntry, JournalLine, Payment, RefundRequest

DEFAULT_ACCOUNTS = [
    ("1010", "Cash and Provider Clearing", "ASSET"),
    ("1020", "Main University Bank Account", "ASSET"),
    ("1100", "Student Accounts Receivable", "ASSET"),
    ("2010", "Unearned Fee Advance", "LIABILITY"),
    ("2020", "Refund Liabilities Payable", "LIABILITY"),
    ("4010", "Tuition Fee Revenue", "REVENUE"),
    ("4020", "Examination Fee Revenue", "REVENUE"),
    ("4030", "Laboratory Fee Revenue", "REVENUE"),
    ("4040", "Library Fee Revenue", "REVENUE"),
    ("4050", "Late Payment Fee Revenue", "REVENUE"),
    ("5010", "Institutional Scholarship Concessions", "EXPENSE"),
]


class AccountingService:
    def __init__(self, db: Session):
        self.db = db

    def ensure_default_accounts(self) -> dict[str, Account]:
        account_map = {}
        for code, name, acct_type in DEFAULT_ACCOUNTS:
            acct = self.db.scalar(select(Account).where(Account.code == code))
            if acct is None:
                acct = Account(code=code, name=name, account_type=acct_type, is_active=True)
                self.db.add(acct)
                self.db.flush()
            account_map[code] = acct
        return account_map

    def get_account_by_code(self, code: str) -> Account:
        accounts = self.ensure_default_accounts()
        if code not in accounts:
            raise FinanceDomainError(f"Account code {code} not recognized")
        return accounts[code]

    def post_journal_entry(
        self,
        *,
        reference: str,
        description: str,
        lines: list[dict],
        entry_date: date | None = None,
    ) -> JournalEntry:
        """Post a strictly balanced double-entry journal.
        
        Invariant: Total Debits == Total Credits.
        """
        if not lines:
            raise FinanceDomainError("Journal entry must have at least two lines")

        now_date = entry_date or datetime.now(UTC).date()
        total_debit = Decimal("0.00")
        total_credit = Decimal("0.00")

        for line in lines:
            debit = Decimal(str(line.get("debit", 0))).quantize(Decimal("0.01"))
            credit = Decimal(str(line.get("credit", 0))).quantize(Decimal("0.01"))
            if debit < 0 or credit < 0:
                raise FinanceDomainError("Negative line amounts not permitted; use opposite debit/credit column")
            if debit > 0 and credit > 0:
                raise FinanceDomainError("Line cannot have both debit and credit amounts")
            total_debit += debit
            total_credit += credit

        if total_debit != total_credit:
            raise FinanceDomainError(
                f"Double-entry invariant violated: Total Debits ({total_debit}) != Total Credits ({total_credit})"
            )
        if total_debit == 0:
            raise FinanceDomainError("Journal entry cannot have zero total balance")

        entry_num = f"JE-{datetime.now(UTC).strftime('%Y%m')}-{uuid.uuid4().hex[:8].upper()}"
        entry = JournalEntry(
            entry_number=entry_num,
            entry_date=now_date,
            reference=reference,
            description=description,
            is_posted=True,
        )
        self.db.add(entry)
        self.db.flush()

        for line in lines:
            acct_id = line.get("account_id")
            if not acct_id and "account_code" in line:
                acct_id = self.get_account_by_code(line["account_code"]).id

            j_line = JournalLine(
                journal_entry_id=entry.id,
                account_id=acct_id,
                debit=Decimal(str(line.get("debit", 0))).quantize(Decimal("0.01")),
                credit=Decimal(str(line.get("credit", 0))).quantize(Decimal("0.01")),
                description=line.get("description"),
            )
            self.db.add(j_line)

        self.db.flush()
        return entry

    def record_invoice_issuance(self, invoice: Invoice) -> JournalEntry:
        """Accrual recognition of student invoice."""
        self.ensure_default_accounts()
        lines = []

        # Debit: Accounts Receivable for the payable balance
        lines.append({
            "account_code": "1100",
            "debit": invoice.total_amount,
            "credit": Decimal("0.00"),
            "description": f"Accounts Receivable: Invoice {invoice.invoice_number}",
        })

        # Debit: Scholarship expense if concession applied
        if invoice.scholarship_amount > Decimal("0.00"):
            lines.append({
                "account_code": "5010",
                "debit": invoice.scholarship_amount,
                "credit": Decimal("0.00"),
                "description": f"Scholarship concession: Invoice {invoice.invoice_number}",
            })

        # Credit: Revenue per component type
        code_map = {
            "TUITION": "4010",
            "EXAMINATION": "4020",
            "LABORATORY": "4030",
            "LIBRARY": "4040",
        }
        for item in invoice.items:
            rev_code = code_map.get(item.component_type.upper(), "4010")
            lines.append({
                "account_code": rev_code,
                "debit": Decimal("0.00"),
                "credit": item.amount,
                "description": f"{item.component_name} revenue: Invoice {invoice.invoice_number}",
            })

        return self.post_journal_entry(
            reference=f"INVOICE:{invoice.invoice_number}",
            description=f"Issuance of student semester fee invoice {invoice.invoice_number}",
            lines=lines,
            entry_date=invoice.issue_date,
        )

    def record_late_fee(self, invoice: Invoice, late_fee_amount: Decimal) -> JournalEntry:
        """Record late penalty charged on overdue invoice."""
        lines = [
            {
                "account_code": "1100",
                "debit": late_fee_amount,
                "credit": Decimal("0.00"),
                "description": f"Late penalty charged on {invoice.invoice_number}",
            },
            {
                "account_code": "4050",
                "debit": Decimal("0.00"),
                "credit": late_fee_amount,
                "description": f"Late fee revenue: {invoice.invoice_number}",
            },
        ]
        return self.post_journal_entry(
            reference=f"LATE_FEE:{invoice.invoice_number}",
            description=f"Overdue penalty assessed on invoice {invoice.invoice_number}",
            lines=lines,
        )

    def record_payment_receipt(self, payment: Payment, invoice: Invoice) -> JournalEntry:
        """Cash / provider receipt reducing student receivable."""
        lines = [
            {
                "account_code": "1010",
                "debit": payment.amount,
                "credit": Decimal("0.00"),
                "description": f"Receipt via {payment.method}: Receipt {payment.receipt_number}",
            },
            {
                "account_code": "1100",
                "debit": Decimal("0.00"),
                "credit": payment.amount,
                "description": f"Receivable settlement: Invoice {invoice.invoice_number}",
            },
        ]
        return self.post_journal_entry(
            reference=f"PAYMENT:{payment.provider_transaction_id}",
            description=f"Payment received for invoice {invoice.invoice_number} via {payment.method}",
            lines=lines,
        )

    def record_refund(self, refund: RefundRequest) -> JournalEntry:
        """Refund recording: reduces cash and acknowledges refund expense/reversal."""
        lines = [
            {
                "account_code": "1100",
                "debit": refund.amount,
                "credit": Decimal("0.00"),
                "description": f"Refund adjustment for student {refund.student_user_id}",
            },
            {
                "account_code": "1010",
                "debit": Decimal("0.00"),
                "credit": refund.amount,
                "description": f"Cash disbursement for refund {refund.id}",
            },
        ]
        return self.post_journal_entry(
            reference=f"REFUND:{refund.id}",
            description=f"Approved refund of {refund.amount} for payment {refund.payment_id}",
            lines=lines,
        )

    def get_trial_balance(self, as_of: date | None = None) -> dict:
        """Compute the trial balance and verify debit/credit parity."""
        accounts = self.ensure_default_accounts()
        target_date = as_of or datetime.now(UTC).date()

        query = (
            select(
                JournalLine.account_id,
                func.sum(JournalLine.debit).label("total_debit"),
                func.sum(JournalLine.credit).label("total_credit"),
            )
            .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
            .where(JournalEntry.entry_date <= target_date, JournalEntry.is_posted == True)
            .group_by(JournalLine.account_id)
        )

        rows = self.db.execute(query).fetchall()
        balance_map = {row.account_id: (row.total_debit or Decimal("0.00"), row.total_credit or Decimal("0.00")) for row in rows}

        items = []
        grand_debit = Decimal("0.00")
        grand_credit = Decimal("0.00")

        all_accounts = self.db.scalars(select(Account).order_by(Account.code)).all()
        for acct in all_accounts:
            deb, cred = balance_map.get(acct.id, (Decimal("0.00"), Decimal("0.00")))
            grand_debit += deb
            grand_credit += cred
            # Net balance by account type
            if acct.account_type in {"ASSET", "EXPENSE"}:
                net = deb - cred
            else:
                net = cred - deb
            items.append({
                "account_code": acct.code,
                "account_name": acct.name,
                "account_type": acct.account_type,
                "total_debit": deb,
                "total_credit": cred,
                "balance": net,
            })

        return {
            "as_of": target_date,
            "items": items,
            "total_debits": grand_debit,
            "total_credits": grand_credit,
            "is_balanced": grand_debit == grand_credit,
        }


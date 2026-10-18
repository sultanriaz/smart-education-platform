from __future__ import annotations

import csv
import io
import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import FinanceDomainError
from app.domain.models import Payment, ReconciliationBatch, ReconciliationItem


class ReconciliationService:
    def __init__(self, db: Session):
        self.db = db

    def _sanitize_cell(self, value: str) -> str:
        """Prevent CSV formula injection by stripping dangerous leading characters."""
        val = value.strip()
        while val and val[0] in {"=", "+", "-", "@", "\t", "\r"}:
            val = val[1:].strip()
        return val

    def process_settlement_csv(
        self,
        *,
        filename: str,
        provider: str,
        csv_content: str,
    ) -> ReconciliationBatch:
        if len(csv_content.encode("utf-8")) > 5 * 1024 * 1024:
            raise FinanceDomainError("Settlement file exceeds maximum allowed size (5MB)")

        reader = csv.reader(io.StringIO(csv_content.strip()))
        rows = list(reader)
        if not rows:
            raise FinanceDomainError("Settlement CSV is empty")

        header = [self._sanitize_cell(col).lower() for col in rows[0]]
        expected = {"transaction_ref", "amount", "date"}
        if not expected.issubset(set(header)):
            raise FinanceDomainError(f"Missing required columns in settlement file. Expected at least: {expected}")

        ref_idx = header.index("transaction_ref")
        amt_idx = header.index("amount")
        date_idx = header.index("date")

        batch = ReconciliationBatch(
            filename=filename,
            provider=provider.upper(),
            total_rows=0,
            matched_rows=0,
            exception_rows=0,
            status="PROCESSED",
        )
        self.db.add(batch)
        self.db.flush()

        data_rows = rows[1:]
        if len(data_rows) > 5000:
            raise FinanceDomainError("Settlement file exceeds 5,000 row batch limit")

        for row in data_rows:
            if not row or all(not c.strip() for c in row):
                continue
            batch.total_rows += 1

            ref = self._sanitize_cell(row[ref_idx])
            amt_str = self._sanitize_cell(row[amt_idx])
            date_str = self._sanitize_cell(row[date_idx])

            try:
                amt = Decimal(amt_str).quantize(Decimal("0.01"))
            except Exception:
                amt = Decimal("0.00")

            try:
                stmt_date = date.fromisoformat(date_str[:10])
            except Exception:
                stmt_date = datetime.now(UTC).date()

            # Search DB for payment matching ref
            payment = self.db.scalar(
                select(Payment).where(Payment.provider_transaction_id == ref)
            )

            if payment is None:
                match_status = "UNMATCHED_PROVIDER"
                batch.exception_rows += 1
            elif payment.amount != amt:
                match_status = "AMOUNT_MISMATCH"
                batch.exception_rows += 1
            else:
                match_status = "MATCHED"
                batch.matched_rows += 1

            item = ReconciliationItem(
                batch_id=batch.id,
                transaction_ref=ref,
                amount=amt,
                statement_date=stmt_date,
                match_status=match_status,
                resolved=match_status == "MATCHED",
            )
            self.db.add(item)

        self.db.commit()
        self.db.refresh(batch)
        return batch


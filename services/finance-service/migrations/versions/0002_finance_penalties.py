from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002_finance"
down_revision = "0001_finance"
branch_labels = None
depends_on = None


def upgrade():
    # 1. Add additive columns to invoices if they do not exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    invoice_cols = {c["name"] for c in inspector.get_columns("invoices")}
    
    if "late_fee_applied_at" not in invoice_cols:
        op.add_column(
            "invoices",
            sa.Column("late_fee_applied_at", sa.DateTime(timezone=True), nullable=True),
        )
    if "overdue_notified_at" not in invoice_cols:
        op.add_column(
            "invoices",
            sa.Column("overdue_notified_at", sa.DateTime(timezone=True), nullable=True),
        )

    # 2. Ensure finance_inbox_events exists
    tables = inspector.get_table_names()
    if "finance_inbox_events" not in tables:
        op.create_table(
            "finance_inbox_events",
            sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
            sa.Column("event_id", sa.Uuid(as_uuid=True), unique=True, index=True, nullable=False),
            sa.Column("source_service", sa.String(80), nullable=False),
            sa.Column("event_type", sa.String(160), nullable=False),
            sa.Column("processed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )


def downgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    invoice_cols = {c["name"] for c in inspector.get_columns("invoices")}
    if "overdue_notified_at" in invoice_cols:
        op.drop_column("invoices", "overdue_notified_at")
    if "late_fee_applied_at" in invoice_cols:
        op.drop_column("invoices", "late_fee_applied_at")
    tables = inspector.get_table_names()
    if "finance_inbox_events" in tables:
        op.drop_table("finance_inbox_events")


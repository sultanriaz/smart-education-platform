from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002_payroll"
down_revision = "0001_payroll"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # 1. Additive columns to disbursement_records
    rec_cols = {c["name"] for c in inspector.get_columns("disbursement_records")}
    if "retry_count" not in rec_cols:
        op.add_column(
            "disbursement_records",
            sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        )
    if "last_retried_at" not in rec_cols:
        op.add_column(
            "disbursement_records",
            sa.Column("last_retried_at", sa.DateTime(timezone=True), nullable=True),
        )
    if "reconciled" not in rec_cols:
        op.add_column(
            "disbursement_records",
            sa.Column("reconciled", sa.Boolean(), nullable=False, server_default="false"),
        )
    if "reconciled_at" not in rec_cols:
        op.add_column(
            "disbursement_records",
            sa.Column("reconciled_at", sa.DateTime(timezone=True), nullable=True),
        )

    # 2. Additive columns to disbursement_batches
    batch_cols = {c["name"] for c in inspector.get_columns("disbursement_batches")}
    if "failed_count" not in batch_cols:
        op.add_column(
            "disbursement_batches",
            sa.Column("failed_count", sa.Integer(), nullable=False, server_default="0"),
        )
    if "reconciled_count" not in batch_cols:
        op.add_column(
            "disbursement_batches",
            sa.Column("reconciled_count", sa.Integer(), nullable=False, server_default="0"),
        )

    # 3. Ensure payroll_inbox_events exists
    tables = inspector.get_table_names()
    if "payroll_inbox_events" not in tables:
        op.create_table(
            "payroll_inbox_events",
            sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
            sa.Column("event_id", sa.Uuid(as_uuid=True), unique=True, index=True, nullable=False),
            sa.Column("source_service", sa.String(80), nullable=False),
            sa.Column("event_type", sa.String(160), nullable=False),
            sa.Column("processed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )


def downgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    batch_cols = {c["name"] for c in inspector.get_columns("disbursement_batches")}
    if "reconciled_count" in batch_cols:
        op.drop_column("disbursement_batches", "reconciled_count")
    if "failed_count" in batch_cols:
        op.drop_column("disbursement_batches", "failed_count")

    rec_cols = {c["name"] for c in inspector.get_columns("disbursement_records")}
    if "reconciled_at" in rec_cols:
        op.drop_column("disbursement_records", "reconciled_at")
    if "reconciled" in rec_cols:
        op.drop_column("disbursement_records", "reconciled")
    if "last_retried_at" in rec_cols:
        op.drop_column("disbursement_records", "last_retried_at")
    if "retry_count" in rec_cols:
        op.drop_column("disbursement_records", "retry_count")

    tables = inspector.get_table_names()
    if "payroll_inbox_events" in tables:
        op.drop_table("payroll_inbox_events")


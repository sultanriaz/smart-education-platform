"""Durable relay retry state; only this service's schema is modified."""

import sqlalchemy as sa
from alembic import op

revision = "0003_academic_event_runtime"
down_revision = "0001_academic_core"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "outbox_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("event_type", sa.String(160), nullable=False),
        sa.Column("aggregate_id", sa.Uuid(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_outbox_events_event_type", "outbox_events", ["event_type"])
    op.create_index("ix_outbox_events_aggregate_id", "outbox_events", ["aggregate_id"])
    op.create_index("ix_outbox_events_published_at", "outbox_events", ["published_at"])
    existing = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("outbox_events")}
    for column in (
        sa.Column("relay_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("relay_retry_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("relay_error", sa.String(240), nullable=True),
    ):
        if column.name not in existing:
            op.add_column("outbox_events", column)


def downgrade():
    for column in ("relay_error", "relay_retry_at", "relay_attempts"):
        op.drop_column("outbox_events", column)
    op.drop_table("outbox_events")

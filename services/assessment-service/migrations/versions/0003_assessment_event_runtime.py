"""Durable relay retry state; only this service's schema is modified."""

import sqlalchemy as sa
from alembic import op

revision = "0003_assessment_event_runtime"
down_revision = "0001_assessment"
branch_labels = None
depends_on = None


def upgrade():
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

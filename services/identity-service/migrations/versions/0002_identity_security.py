"""Identity-owned one-time tokens and encrypted security outbox."""

import sqlalchemy as sa
from alembic import op

revision = "0002_identity_security"
down_revision = "e05f24e27336"
branch_labels = None
depends_on = None


def upgrade():
    for name in ("password_reset_tokens", "email_verification_tokens"):
        op.create_table(
            name,
            sa.Column("id", sa.Uuid(), primary_key=True),
            sa.Column("user_id", sa.Uuid(), nullable=False),
            sa.Column("token_digest", sa.String(64), nullable=False, unique=True),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("used_at", sa.DateTime(timezone=True)),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index(f"ix_{name}_user_expires", name, ["user_id", "expires_at"])
    op.create_table(
        "outbox_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("event_type", sa.String(160), nullable=False),
        sa.Column("aggregate_id", sa.Uuid(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_identity_outbox_pending", "outbox_events", ["published_at", "created_at"])


def downgrade():
    op.drop_table("outbox_events")
    op.drop_table("email_verification_tokens")
    op.drop_table("password_reset_tokens")

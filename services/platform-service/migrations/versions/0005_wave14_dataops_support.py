"""Wave 14 additive job and support state.
Revision ID: 0005_wave14_dataops_support
Revises: 0004_wave13_governance
"""
import sqlalchemy as sa
from alembic import op
revision = "0005_wave14_dataops_support"
down_revision = "0004_wave13_governance"
branch_labels = depends_on = None

def upgrade():
    for col in (sa.Column("content_digest", sa.String(64)), sa.Column("idempotency_key", sa.String(160)), sa.Column("dry_run", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("expires_at", sa.DateTime(timezone=True))): op.add_column("job_records", col)
    op.create_index("ix_jobs_type_idempotency", "job_records", ["job_type", "idempotency_key"], unique=True, postgresql_where=sa.text("idempotency_key IS NOT NULL"))
    for col in (sa.Column("due_at", sa.DateTime(timezone=True)), sa.Column("escalated_at", sa.DateTime(timezone=True)), sa.Column("last_message_at", sa.DateTime(timezone=True))): op.add_column("support_tickets", col)
    op.create_index("ix_tickets_status_due", "support_tickets", ["status", "due_at"])
    op.create_index("ix_tickets_creator_created", "support_tickets", ["created_by_user_id", "created_at"])
    op.create_index("ix_support_messages_ticket_created", "support_messages", ["ticket_id", "created_at"])

def downgrade():
    op.drop_index("ix_support_messages_ticket_created", "support_messages")
    op.drop_index("ix_tickets_creator_created", "support_tickets")
    op.drop_index("ix_tickets_status_due", "support_tickets")
    for col in ("last_message_at", "escalated_at", "due_at"): op.drop_column("support_tickets", col)
    op.drop_index("ix_jobs_type_idempotency", "job_records")
    for col in ("expires_at", "dry_run", "idempotency_key", "content_digest"): op.drop_column("job_records", col)

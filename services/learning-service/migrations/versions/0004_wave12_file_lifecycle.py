"""Durable file cleanup and auditable storage operations."""
import sqlalchemy as sa
from alembic import op
revision = "0004_learning_file_lifecycle"
down_revision = "0003_learning_event_runtime"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("file_deletion_tasks",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("storage_key", sa.String(500), nullable=False, unique=True),
        sa.Column("resource_id", sa.Uuid(), nullable=False),
        sa.Column("actor_user_id", sa.Uuid(), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True)),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.Column("error", sa.String(160)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    op.create_index("ix_file_deletions_resource", "file_deletion_tasks", ["resource_id"])
    op.create_table("file_operation_audits",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("resource_id", sa.Uuid(), nullable=False),
        sa.Column("version_id", sa.Uuid()),
        sa.Column("actor_user_id", sa.Uuid(), nullable=False),
        sa.Column("operation", sa.String(24), nullable=False),
        sa.Column("checksum_sha256", sa.String(64)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    op.create_index("ix_file_operation_audits_resource", "file_operation_audits", ["resource_id"])


def downgrade():
    op.drop_index("ix_file_operation_audits_resource", table_name="file_operation_audits")
    op.drop_table("file_operation_audits")
    op.drop_index("ix_file_deletions_resource", table_name="file_deletion_tasks")
    op.drop_table("file_deletion_tasks")

"""Durable Identity lifecycle inbox for idempotent Academic reconciliation."""

import sqlalchemy as sa
from alembic import op

revision = "0004_identity_lifecycle_inbox"
down_revision = "0003_academic_event_runtime"
branch_labels = None
depends_on = None


def upgrade():
    for table in ("student_academic_profiles", "teacher_academic_profiles"):
        op.add_column(table, sa.Column(
            "identity_suspended", sa.Boolean(), nullable=False, server_default=sa.false()
        ))
    op.create_table(
        "identity_eligibility_inbox",
        sa.Column("event_id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_identity_eligibility_inbox_user_id",
                    "identity_eligibility_inbox", ["user_id"])


def downgrade():
    for table in ("student_academic_profiles", "teacher_academic_profiles"):
        op.drop_column(table, "identity_suspended")
    op.drop_index("ix_identity_eligibility_inbox_user_id",
                  table_name="identity_eligibility_inbox")
    op.drop_table("identity_eligibility_inbox")

"""Allow a draft schedule lifecycle without changing published schedules.

Revision ID: 0004_sched_draft
Revises: 0003_scheduling_event_runtime
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_sched_draft"
down_revision = "0003_scheduling_event_runtime"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("schedule_entries", recreate="auto") as batch:
        batch.drop_constraint("ck_schedule_status", type_="check")
        batch.create_check_constraint("ck_schedule_status", "status IN ('DRAFT', 'ACTIVE', 'CANCELLED')")


def downgrade():
    bind = op.get_bind()
    existing = bind.execute(sa.text("SELECT COUNT(*) FROM schedule_entries WHERE status = 'DRAFT'")).scalar_one()
    if existing:
        raise RuntimeError("Cannot downgrade while DRAFT entries exist; publish or remove drafts with authorization first")
    with op.batch_alter_table("schedule_entries", recreate="auto") as batch:
        batch.drop_constraint("ck_schedule_status", type_="check")
        batch.create_check_constraint("ck_schedule_status", "status IN ('ACTIVE', 'CANCELLED')")

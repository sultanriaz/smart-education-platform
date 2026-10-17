"""Wave11: durable campaign drafts, scheduling and expiry state."""
import sqlalchemy as sa
from alembic import op

revision = "0004_wave11_campaign_lifecycle"
down_revision = "0003_notification_event_runtime"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("notification_campaigns", sa.Column("priority", sa.String(20), nullable=False, server_default="NORMAL"))
    op.add_column("notification_campaigns", sa.Column("data", sa.JSON(), nullable=False, server_default="{}"))
    op.add_column("notification_campaigns", sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=True))
    op.add_column("notification_campaigns", sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("notification_campaigns", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    op.create_index("ix_notification_campaigns_scheduled_for", "notification_campaigns", ["scheduled_for"])
    op.create_index("ix_notification_campaigns_expires_at", "notification_campaigns", ["expires_at"])


def downgrade():
    op.drop_index("ix_notification_campaigns_expires_at", table_name="notification_campaigns")
    op.drop_index("ix_notification_campaigns_scheduled_for", table_name="notification_campaigns")
    for col in ("updated_at", "expires_at", "scheduled_for", "data", "priority"):
        op.drop_column("notification_campaigns", col)

"""Wave 13 authentication activity history. Revision ID: 0005_wave13_auth_activity"""
import sqlalchemy as sa
from alembic import op
revision = "0005_wave13_auth_activity"
down_revision = "0004_auth_version"
branch_labels = depends_on = None

def upgrade():
    for col in (sa.Column("outcome", sa.String(32), nullable=False, server_default="SUCCEEDED"), sa.Column("request_id", sa.String(128)), sa.Column("correlation_id", sa.String(128)), sa.Column("trace_id", sa.String(64))): op.add_column("security_audit_events", col)
    op.create_index("ix_security_history_user_date", "security_audit_events", ["user_id", "created_at"])
    op.create_index("ix_security_history_action_outcome", "security_audit_events", ["action", "outcome"])
    op.create_index("ix_security_history_correlation", "security_audit_events", ["correlation_id"])

def downgrade():
    for index in ("ix_security_history_correlation", "ix_security_history_action_outcome", "ix_security_history_user_date"): op.drop_index(index, "security_audit_events")
    for col in ("trace_id", "correlation_id", "request_id", "outcome"): op.drop_column("security_audit_events", col)

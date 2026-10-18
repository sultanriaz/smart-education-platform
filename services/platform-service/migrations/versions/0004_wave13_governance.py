"""Wave 13 additive governance and index lifecycle.
Revision ID: 0004_wave13_governance
Revises: 0003_platform_event_runtime
"""
import sqlalchemy as sa
from alembic import op
revision = "0004_wave13_governance"
down_revision = "0003_platform_event_runtime"
branch_labels = depends_on = None

def upgrade():
    for col in (sa.Column("event_id", sa.Uuid(), nullable=True), sa.Column("outcome", sa.String(32), nullable=True), sa.Column("request_id", sa.String(128), nullable=True), sa.Column("trace_id", sa.String(64), nullable=True)):
        op.add_column("audit_entries", col)
    op.create_unique_constraint("uq_audit_entries_event_id", "audit_entries", ["event_id"])
    op.create_index("ix_audit_actor_occurred", "audit_entries", ["actor_user_id", "occurred_at"])
    op.create_index("ix_audit_correlation_occurred", "audit_entries", ["correlation_id", "occurred_at"])
    op.add_column("platform_settings", sa.Column("version", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("feature_flags", sa.Column("version", sa.Integer(), nullable=False, server_default="0"))
    op.create_table("setting_revisions", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("setting_key", sa.String(160), nullable=False), sa.Column("version", sa.Integer(), nullable=False), sa.Column("value", sa.JSON(), nullable=False), sa.Column("is_public", sa.Boolean(), nullable=False), sa.Column("description", sa.Text()), sa.Column("changed_by_user_id", sa.Uuid(), nullable=False), sa.Column("reason", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.UniqueConstraint("setting_key", "version", name="uq_setting_revision"))
    op.create_index("ix_setting_revisions_setting_key", "setting_revisions", ["setting_key"])
    op.create_table("feature_flag_revisions", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("flag_key", sa.String(160), nullable=False), sa.Column("version", sa.Integer(), nullable=False), sa.Column("enabled", sa.Boolean(), nullable=False), sa.Column("config", sa.JSON(), nullable=False), sa.Column("description", sa.Text()), sa.Column("changed_by_user_id", sa.Uuid(), nullable=False), sa.Column("reason", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.UniqueConstraint("flag_key", "version", name="uq_feature_flag_revision"))
    op.create_index("ix_feature_flag_revisions_flag_key", "feature_flag_revisions", ["flag_key"])
    for col in (sa.Column("acl_version", sa.Integer(), nullable=False, server_default="1"), sa.Column("content_hash", sa.String(64)), sa.Column("deindexed_at", sa.DateTime(timezone=True))):
        op.add_column("search_documents", col)
    op.create_table("search_index_revisions", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("search_document_id", sa.Uuid(), nullable=False), sa.Column("acl_version", sa.Integer(), nullable=False), sa.Column("audience", sa.JSON(), nullable=False), sa.Column("content_hash", sa.String(64), nullable=False), sa.Column("indexed_at", sa.DateTime(timezone=True), nullable=False), sa.Column("deindexed_at", sa.DateTime(timezone=True)))
    op.create_index("ix_search_index_revisions_search_document_id", "search_index_revisions", ["search_document_id"])

def downgrade():
    op.drop_index("ix_search_index_revisions_search_document_id", "search_index_revisions")
    op.drop_table("search_index_revisions")
    for col in ("deindexed_at", "content_hash", "acl_version"): op.drop_column("search_documents", col)
    op.drop_index("ix_feature_flag_revisions_flag_key", "feature_flag_revisions")
    op.drop_table("feature_flag_revisions")
    op.drop_index("ix_setting_revisions_setting_key", "setting_revisions")
    op.drop_table("setting_revisions")
    op.drop_column("feature_flags", "version")
    op.drop_column("platform_settings", "version")
    op.drop_index("ix_audit_correlation_occurred", "audit_entries")
    op.drop_index("ix_audit_actor_occurred", "audit_entries")
    op.drop_constraint("uq_audit_entries_event_id", "audit_entries", type_="unique")
    for col in ("trace_id", "request_id", "outcome", "event_id"): op.drop_column("audit_entries", col)

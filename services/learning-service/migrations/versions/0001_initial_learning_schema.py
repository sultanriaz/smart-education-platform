"""initial learning schema

Revision ID: 0001_learning
Revises:
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ENUM

revision = "0001_learning"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Types are explicitly created once below. Table creation must not issue
    # a second CREATE TYPE (PostgreSQL rolls the whole migration back).
    resource_type = ENUM("FILE", "LINK", "VIDEO", "NOTE", name="resource_type", create_type=False)
    resource_status = ENUM(
        "DRAFT", "PUBLISHED", "ARCHIVED", name="resource_status", create_type=False
    )
    target_type = ENUM("SECTION", "COURSE", name="target_type", create_type=False)
    access_action = ENUM("VIEW", "DOWNLOAD", name="access_action", create_type=False)
    bind = op.get_bind()
    for enum in (resource_type, resource_status, target_type, access_action):
        enum.create(bind, checkfirst=True)

    op.create_table(
        "resource_categories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("slug", sa.String(120), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )

    op.create_table(
        "learning_resources",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(240), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("resource_type", resource_type, nullable=False),
        sa.Column("status", resource_status, nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=True),
        sa.Column("creator_user_id", sa.Uuid(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["resource_categories.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_learning_resources_title", "learning_resources", ["title"])
    op.create_index("ix_learning_resources_status", "learning_resources", ["status"])
    op.create_index(
        "ix_learning_resources_creator_user_id", "learning_resources", ["creator_user_id"]
    )
    op.create_index("ix_learning_resources_created_at", "learning_resources", ["created_at"])

    op.create_table(
        "resource_targets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("resource_id", sa.Uuid(), nullable=False),
        sa.Column("target_type", target_type, nullable=False),
        sa.Column("target_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["resource_id"], ["learning_resources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("resource_id", "target_type", "target_id", name="uq_resource_target"),
    )
    op.create_index("ix_resource_targets_resource_id", "resource_targets", ["resource_id"])
    op.create_index("ix_resource_targets_lookup", "resource_targets", ["target_type", "target_id"])

    op.create_table(
        "resource_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("resource_id", sa.Uuid(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("text_content", sa.Text(), nullable=True),
        sa.Column("external_url", sa.Text(), nullable=True),
        sa.Column("storage_key", sa.String(500), nullable=True),
        sa.Column("original_filename", sa.String(255), nullable=True),
        sa.Column("mime_type", sa.String(255), nullable=True),
        sa.Column("size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("checksum_sha256", sa.String(64), nullable=True),
        sa.Column("change_note", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["resource_id"], ["learning_resources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("resource_id", "version_number", name="uq_resource_version_number"),
        sa.UniqueConstraint("storage_key"),
    )
    op.create_index("ix_resource_versions_resource_id", "resource_versions", ["resource_id"])

    op.create_table(
        "resource_access_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("resource_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("action", access_action, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["resource_id"], ["learning_resources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_resource_access_logs_resource_id", "resource_access_logs", ["resource_id"])
    op.create_index("ix_resource_access_logs_user_id", "resource_access_logs", ["user_id"])
    op.create_index("ix_resource_access_logs_created_at", "resource_access_logs", ["created_at"])
    op.create_index(
        "ix_resource_access_user_resource", "resource_access_logs", ["user_id", "resource_id"]
    )

    op.create_table(
        "outbox_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(160), nullable=False),
        sa.Column("aggregate_type", sa.String(80), nullable=False),
        sa.Column("aggregate_id", sa.Uuid(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_outbox_events_event_type", "outbox_events", ["event_type"])
    op.create_index("ix_outbox_events_aggregate_id", "outbox_events", ["aggregate_id"])
    op.create_index("ix_outbox_events_created_at", "outbox_events", ["created_at"])
    op.create_index("ix_outbox_events_published_at", "outbox_events", ["published_at"])


def downgrade() -> None:
    op.drop_table("outbox_events")
    op.drop_table("resource_access_logs")
    op.drop_table("resource_versions")
    op.drop_table("resource_targets")
    op.drop_table("learning_resources")
    op.drop_table("resource_categories")
    bind = op.get_bind()
    for name in ("access_action", "target_type", "resource_status", "resource_type"):
        sa.Enum(name=name).drop(bind, checkfirst=True)

"""initial notification schema

Revision ID: 0001_notification
Revises:
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_notification"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notification_templates",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(120), nullable=False),
        sa.Column("title_template", sa.String(255), nullable=False),
        sa.Column("body_template", sa.Text(), nullable=False),
        sa.Column("default_channels", sa.JSON(), nullable=False),
        sa.Column("category", sa.String(80), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(
        "ix_notification_templates_code", "notification_templates", ["code"], unique=True
    )
    op.create_index("ix_notification_templates_category", "notification_templates", ["category"])
    op.create_index("ix_notification_templates_enabled", "notification_templates", ["enabled"])
    op.create_index(
        "ix_notification_templates_created_by_user_id",
        "notification_templates",
        ["created_by_user_id"],
    )

    op.create_table(
        "notification_preferences",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("in_app_enabled", sa.Boolean(), nullable=False),
        sa.Column("email_enabled", sa.Boolean(), nullable=False),
        sa.Column("muted_categories", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(
        "ix_notification_preferences_user_id", "notification_preferences", ["user_id"], unique=True
    )

    op.create_table(
        "notification_campaigns",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("target_kind", sa.String(30), nullable=False),
        sa.Column("target_value", sa.JSON(), nullable=False),
        sa.Column("template_code", sa.String(120), nullable=True),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("category", sa.String(80), nullable=False),
        sa.Column("channels", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("recipient_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    for name, cols in [
        ("ix_notification_campaigns_created_by_user_id", ["created_by_user_id"]),
        ("ix_notification_campaigns_target_kind", ["target_kind"]),
        ("ix_notification_campaigns_category", ["category"]),
        ("ix_notification_campaigns_status", ["status"]),
        ("ix_notification_campaigns_created_at", ["created_at"]),
    ]:
        op.create_index(name, "notification_campaigns", cols)

    op.create_table(
        "notifications",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("recipient_user_id", sa.Uuid(), nullable=False),
        sa.Column("recipient_email", sa.String(320), nullable=True),
        sa.Column("campaign_id", sa.Uuid(), nullable=True),
        sa.Column("category", sa.String(80), nullable=False),
        sa.Column("priority", sa.String(20), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("source_service", sa.String(100), nullable=True),
        sa.Column("source_event_id", sa.String(160), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("in_app_visible", sa.Boolean(), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["campaign_id"], ["notification_campaigns.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    for name, cols in [
        ("ix_notifications_recipient_user_id", ["recipient_user_id"]),
        ("ix_notifications_campaign_id", ["campaign_id"]),
        ("ix_notifications_category", ["category"]),
        ("ix_notifications_priority", ["priority"]),
        ("ix_notifications_source_service", ["source_service"]),
        ("ix_notifications_source_event_id", ["source_event_id"]),
        ("ix_notifications_status", ["status"]),
        ("ix_notifications_in_app_visible", ["in_app_visible"]),
        ("ix_notifications_created_at", ["created_at"]),
        ("ix_notifications_recipient_created", ["recipient_user_id", "created_at"]),
        ("ix_notifications_recipient_status", ["recipient_user_id", "status"]),
    ]:
        op.create_index(name, "notifications", cols)

    op.create_table(
        "delivery_attempts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("notification_id", sa.Uuid(), nullable=False),
        sa.Column("channel", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
        sa.Column("provider_message_id", sa.String(255), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["notification_id"], ["notifications.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "notification_id", "channel", "attempt_number", name="uq_delivery_attempt"
        ),
    )
    op.create_index(
        "ix_delivery_attempts_notification_id", "delivery_attempts", ["notification_id"]
    )
    op.create_index("ix_delivery_attempts_channel", "delivery_attempts", ["channel"])
    op.create_index("ix_delivery_attempts_status", "delivery_attempts", ["status"])
    op.create_index("ix_delivery_status_retry", "delivery_attempts", ["status", "next_attempt_at"])

    op.create_table(
        "inbox_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("event_id", sa.String(160), nullable=False),
        sa.Column("source_service", sa.String(100), nullable=False),
        sa.Column("event_type", sa.String(160), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("targets", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id"),
    )
    for name, cols, unique in [
        ("ix_inbox_events_event_id", ["event_id"], True),
        ("ix_inbox_events_source_service", ["source_service"], False),
        ("ix_inbox_events_event_type", ["event_type"], False),
        ("ix_inbox_events_status", ["status"], False),
        ("ix_inbox_events_received_at", ["received_at"], False),
    ]:
        op.create_index(name, "inbox_events", cols, unique=unique)

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
    for name, cols in [
        ("ix_outbox_events_event_type", ["event_type"]),
        ("ix_outbox_events_aggregate_type", ["aggregate_type"]),
        ("ix_outbox_events_aggregate_id", ["aggregate_id"]),
        ("ix_outbox_events_created_at", ["created_at"]),
    ]:
        op.create_index(name, "outbox_events", cols)


def downgrade() -> None:
    op.drop_table("outbox_events")
    op.drop_table("inbox_events")
    op.drop_table("delivery_attempts")
    op.drop_table("notifications")
    op.drop_table("notification_campaigns")
    op.drop_table("notification_preferences")
    op.drop_table("notification_templates")

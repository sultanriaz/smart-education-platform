"""initial scheduling schema

Revision ID: 0001_scheduling
Revises:
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_scheduling"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "schedule_entries",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("section_id", sa.Uuid(), nullable=False),
        sa.Column("course_id", sa.Uuid(), nullable=True),
        sa.Column("semester_id", sa.Uuid(), nullable=True),
        sa.Column("teacher_user_id", sa.Uuid(), nullable=False),
        sa.Column("room_id", sa.Uuid(), nullable=True),
        sa.Column("weekday", sa.Integer(), nullable=False),
        sa.Column("starts_at", sa.Time(), nullable=False),
        sa.Column("ends_at", sa.Time(), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=False),
        sa.Column("timezone_name", sa.String(64), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("weekday >= 0 AND weekday <= 6", name="ck_schedule_weekday"),
        sa.CheckConstraint("starts_at < ends_at", name="ck_schedule_time_order"),
        sa.CheckConstraint("effective_from <= effective_to", name="ck_schedule_date_order"),
        sa.CheckConstraint("status IN ('ACTIVE', 'CANCELLED')", name="ck_schedule_status"),
    )
    op.create_index("ix_schedule_entries_section_id", "schedule_entries", ["section_id"])
    op.create_index("ix_schedule_entries_course_id", "schedule_entries", ["course_id"])
    op.create_index("ix_schedule_entries_semester_id", "schedule_entries", ["semester_id"])
    op.create_index("ix_schedule_entries_teacher_user_id", "schedule_entries", ["teacher_user_id"])
    op.create_index("ix_schedule_entries_room_id", "schedule_entries", ["room_id"])
    op.create_index("ix_schedule_entries_status", "schedule_entries", ["status"])
    op.create_index(
        "ix_schedule_section_window",
        "schedule_entries",
        ["section_id", "weekday", "effective_from", "effective_to"],
    )
    op.create_index(
        "ix_schedule_teacher_window",
        "schedule_entries",
        ["teacher_user_id", "weekday", "effective_from", "effective_to"],
    )
    op.create_index(
        "ix_schedule_room_window",
        "schedule_entries",
        ["room_id", "weekday", "effective_from", "effective_to"],
    )

    op.create_table(
        "schedule_overrides",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "schedule_id",
            sa.Uuid(),
            sa.ForeignKey("schedule_entries.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("occurrence_date", sa.Date(), nullable=False),
        sa.Column("kind", sa.String(20), nullable=False),
        sa.Column("starts_at", sa.Time(), nullable=True),
        sa.Column("ends_at", sa.Time(), nullable=True),
        sa.Column("room_id", sa.Uuid(), nullable=True),
        sa.Column("reason", sa.String(500), nullable=True),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "schedule_id", "occurrence_date", name="uq_schedule_override_occurrence"
        ),
        sa.CheckConstraint("kind IN ('CANCELLED', 'RESCHEDULED')", name="ck_override_kind"),
    )
    op.create_index("ix_schedule_overrides_schedule_id", "schedule_overrides", ["schedule_id"])
    op.create_index(
        "ix_schedule_overrides_occurrence_date", "schedule_overrides", ["occurrence_date"]
    )

    op.create_table(
        "schedule_audits",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("schedule_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(80), nullable=False),
        sa.Column("actor_user_id", sa.Uuid(), nullable=False),
        sa.Column("before_data", sa.JSON(), nullable=True),
        sa.Column("after_data", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_schedule_audits_schedule_id", "schedule_audits", ["schedule_id"])
    op.create_index("ix_schedule_audits_action", "schedule_audits", ["action"])
    op.create_index("ix_schedule_audits_actor_user_id", "schedule_audits", ["actor_user_id"])
    op.create_index("ix_schedule_audits_created_at", "schedule_audits", ["created_at"])

    op.create_table(
        "outbox_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("aggregate_type", sa.String(80), nullable=False),
        sa.Column("aggregate_id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(120), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_outbox_events_aggregate_id", "outbox_events", ["aggregate_id"])
    op.create_index("ix_outbox_events_event_type", "outbox_events", ["event_type"])
    op.create_index("ix_outbox_unpublished", "outbox_events", ["published_at", "occurred_at"])


def downgrade() -> None:
    op.drop_table("outbox_events")
    op.drop_table("schedule_audits")
    op.drop_table("schedule_overrides")
    op.drop_table("schedule_entries")

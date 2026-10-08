"""initial facility schema

Revision ID: 0001_facility
Revises:
Create Date: 2026-10-07
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_facility"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "facilities",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("kind", sa.String(length=30), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("building", sa.String(length=120), nullable=True),
        sa.Column("floor", sa.String(length=40), nullable=True),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_bookable", sa.Boolean(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("capacity > 0", name="ck_facility_capacity_positive"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_facilities_code", "facilities", ["code"], unique=True)
    op.create_index("ix_facilities_name", "facilities", ["name"])
    op.create_index("ix_facilities_kind", "facilities", ["kind"])
    op.create_index("ix_facilities_building", "facilities", ["building"])
    op.create_index("ix_facilities_is_active", "facilities", ["is_active"])
    op.create_index("ix_facilities_is_bookable", "facilities", ["is_bookable"])
    op.create_index("ix_facilities_created_by_user_id", "facilities", ["created_by_user_id"])
    op.create_index("ix_facilities_kind_active", "facilities", ["kind", "is_active"])

    op.create_table(
        "equipment",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_equipment_code", "equipment", ["code"], unique=True)
    op.create_index("ix_equipment_name", "equipment", ["name"])
    op.create_index("ix_equipment_is_active", "equipment", ["is_active"])

    op.create_table(
        "facility_equipment",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("facility_id", sa.Uuid(), nullable=False),
        sa.Column("equipment_id", sa.Uuid(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.CheckConstraint("quantity > 0", name="ck_facility_equipment_quantity_positive"),
        sa.ForeignKeyConstraint(["equipment_id"], ["equipment.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["facility_id"], ["facilities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("facility_id", "equipment_id", name="uq_facility_equipment"),
    )
    op.create_index("ix_facility_equipment_facility_id", "facility_equipment", ["facility_id"])
    op.create_index("ix_facility_equipment_equipment_id", "facility_equipment", ["equipment_id"])

    op.create_table(
        "bookings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("facility_id", sa.Uuid(), nullable=False),
        sa.Column("requester_user_id", sa.Uuid(), nullable=False),
        sa.Column("purpose", sa.String(length=500), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attendees", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reviewed_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_note", sa.Text(), nullable=True),
        sa.Column("cancelled_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancellation_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("ends_at > starts_at", name="ck_booking_valid_interval"),
        sa.CheckConstraint("attendees > 0", name="ck_booking_attendees_positive"),
        sa.ForeignKeyConstraint(["facility_id"], ["facilities.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    for name, cols in [
        ("ix_bookings_facility_id", ["facility_id"]),
        ("ix_bookings_requester_user_id", ["requester_user_id"]),
        ("ix_bookings_starts_at", ["starts_at"]),
        ("ix_bookings_ends_at", ["ends_at"]),
        ("ix_bookings_status", ["status"]),
        ("ix_bookings_created_at", ["created_at"]),
        ("ix_booking_facility_interval", ["facility_id", "starts_at", "ends_at"]),
        ("ix_booking_requester_created", ["requester_user_id", "created_at"]),
    ]:
        op.create_index(name, "bookings", cols)

    op.create_table(
        "booking_history",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("booking_id", sa.Uuid(), nullable=False),
        sa.Column("action", sa.String(length=60), nullable=False),
        sa.Column("previous_status", sa.String(length=24), nullable=True),
        sa.Column("new_status", sa.String(length=24), nullable=True),
        sa.Column("actor_user_id", sa.Uuid(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("snapshot", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_booking_history_booking_id", "booking_history", ["booking_id"])
    op.create_index("ix_booking_history_action", "booking_history", ["action"])
    op.create_index("ix_booking_history_actor_user_id", "booking_history", ["actor_user_id"])
    op.create_index("ix_booking_history_created_at", "booking_history", ["created_at"])
    op.create_index(
        "ix_booking_history_booking_created", "booking_history", ["booking_id", "created_at"]
    )

    op.create_table(
        "facility_blocks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("facility_id", sa.Uuid(), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("cancelled_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("ends_at > starts_at", name="ck_facility_block_valid_interval"),
        sa.ForeignKeyConstraint(["facility_id"], ["facilities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    for name, cols in [
        ("ix_facility_blocks_facility_id", ["facility_id"]),
        ("ix_facility_blocks_starts_at", ["starts_at"]),
        ("ix_facility_blocks_ends_at", ["ends_at"]),
        ("ix_facility_blocks_status", ["status"]),
        ("ix_facility_blocks_created_by_user_id", ["created_by_user_id"]),
        ("ix_facility_blocks_created_at", ["created_at"]),
        ("ix_facility_block_interval", ["facility_id", "starts_at", "ends_at"]),
    ]:
        op.create_index(name, "facility_blocks", cols)

    op.create_table(
        "external_reservations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("facility_id", sa.Uuid(), nullable=False),
        sa.Column("source_service", sa.String(length=100), nullable=False),
        sa.Column("source_reference_id", sa.String(length=160), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("ends_at > starts_at", name="ck_external_reservation_valid_interval"),
        sa.ForeignKeyConstraint(["facility_id"], ["facilities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source_service", "source_reference_id", name="uq_external_reservation_source"
        ),
    )
    for name, cols in [
        ("ix_external_reservations_facility_id", ["facility_id"]),
        ("ix_external_reservations_source_service", ["source_service"]),
        ("ix_external_reservations_source_reference_id", ["source_reference_id"]),
        ("ix_external_reservations_starts_at", ["starts_at"]),
        ("ix_external_reservations_ends_at", ["ends_at"]),
        ("ix_external_reservations_status", ["status"]),
        ("ix_external_reservations_created_at", ["created_at"]),
        ("ix_external_reservation_interval", ["facility_id", "starts_at", "ends_at"]),
    ]:
        op.create_index(name, "external_reservations", cols)

    op.create_table(
        "outbox_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(length=160), nullable=False),
        sa.Column("aggregate_type", sa.String(length=80), nullable=False),
        sa.Column("aggregate_id", sa.Uuid(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("targets", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    for name, cols in [
        ("ix_outbox_events_event_type", ["event_type"]),
        ("ix_outbox_events_aggregate_type", ["aggregate_type"]),
        ("ix_outbox_events_aggregate_id", ["aggregate_id"]),
        ("ix_outbox_events_created_at", ["created_at"]),
        ("ix_outbox_unpublished", ["published_at", "created_at"]),
    ]:
        op.create_index(name, "outbox_events", cols)


def downgrade() -> None:
    op.drop_table("outbox_events")
    op.drop_table("external_reservations")
    op.drop_table("facility_blocks")
    op.drop_table("booking_history")
    op.drop_table("bookings")
    op.drop_table("facility_equipment")
    op.drop_table("equipment")
    op.drop_table("facilities")

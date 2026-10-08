from __future__ import annotations

import uuid
from datetime import UTC, datetime

from smartedu_infra.runtime import RelayState
from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class NotificationTemplate(Base):
    __tablename__ = "notification_templates"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    title_template: Mapped[str] = mapped_column(String(255))
    body_template: Mapped[str] = mapped_column(Text)
    default_channels: Mapped[list[str]] = mapped_column(JSON, default=lambda: ["IN_APP"])
    category: Mapped[str] = mapped_column(String(80), default="general", index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), unique=True, index=True)
    in_app_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    email_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    muted_categories: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class NotificationCampaign(Base):
    __tablename__ = "notification_campaigns"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    target_kind: Mapped[str] = mapped_column(String(30), index=True)
    target_value: Mapped[dict] = mapped_column(JSON, default=dict)
    template_code: Mapped[str | None] = mapped_column(String(120), nullable=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(80), default="general", index=True)
    channels: Mapped[list[str]] = mapped_column(JSON, default=lambda: ["IN_APP"])
    status: Mapped[str] = mapped_column(String(30), default="COMPLETED", index=True)
    recipient_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_recipient_created", "recipient_user_id", "created_at"),
        Index("ix_notifications_recipient_status", "recipient_user_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipient_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    recipient_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("notification_campaigns.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    category: Mapped[str] = mapped_column(String(80), default="general", index=True)
    priority: Mapped[str] = mapped_column(String(20), default="NORMAL", index=True)
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    data: Mapped[dict] = mapped_column(JSON, default=dict)
    source_service: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    source_event_id: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="UNREAD", index=True)
    in_app_visible: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )

    deliveries: Mapped[list[DeliveryAttempt]] = relationship(
        back_populates="notification", cascade="all, delete-orphan"
    )


class DeliveryAttempt(Base):
    __tablename__ = "delivery_attempts"
    __table_args__ = (
        UniqueConstraint(
            "notification_id", "channel", "attempt_number", name="uq_delivery_attempt"
        ),
        Index("ix_delivery_status_retry", "status", "next_attempt_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notification_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("notifications.id", ondelete="CASCADE"), index=True
    )
    channel: Mapped[str] = mapped_column(String(20), index=True)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", index=True)
    attempt_number: Mapped[int] = mapped_column(Integer, default=1)
    provider_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    notification: Mapped[Notification] = relationship(back_populates="deliveries")


class InboxEvent(Base):
    __tablename__ = "inbox_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    source_service: Mapped[str] = mapped_column(String(100), index=True)
    event_type: Mapped[str] = mapped_column(String(160), index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    targets: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(20), default="RECEIVED", index=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class OutboxEvent(RelayState, Base):
    __tablename__ = "outbox_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type: Mapped[str] = mapped_column(String(160), index=True)
    aggregate_type: Mapped[str] = mapped_column(String(80), index=True)
    aggregate_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

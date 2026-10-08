from __future__ import annotations

import uuid
from datetime import UTC, datetime

from smartedu_infra.runtime import RelayState
from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
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


class InternalEvent(Base):
    __tablename__ = "internal_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), unique=True, index=True)
    source_service: Mapped[str] = mapped_column(String(80), index=True)
    event_type: Mapped[str] = mapped_column(String(160), index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )


class AuditEntry(Base):
    __tablename__ = "audit_entries"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_service: Mapped[str] = mapped_column(String(80), index=True)
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String(160), index=True)
    entity_type: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    entity_id: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    correlation_id: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class SearchDocument(Base):
    __tablename__ = "search_documents"
    __table_args__ = (
        UniqueConstraint(
            "source_service",
            "document_type",
            "document_id",
            name="uq_search_source_type_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_service: Mapped[str] = mapped_column(String(80), index=True)
    document_type: Mapped[str] = mapped_column(String(80), index=True)
    document_id: Mapped[str] = mapped_column(String(160), index=True)
    title: Mapped[str] = mapped_column(String(240), index=True)
    body: Mapped[str] = mapped_column(Text, default="")
    url_path: Mapped[str | None] = mapped_column(String(400), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    audience_roles: Mapped[list] = mapped_column(
        JSON, default=lambda: ["admin", "teacher", "student"]
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_number: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    assigned_to_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True, index=True
    )
    subject: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(80), default="GENERAL", index=True)
    priority: Mapped[str] = mapped_column(String(24), default="MEDIUM", index=True)
    status: Mapped[str] = mapped_column(String(24), default="OPEN", index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    messages: Mapped[list[SupportMessage]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan", lazy="selectin"
    )


class SupportMessage(Base):
    __tablename__ = "support_messages"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("support_tickets.id", ondelete="CASCADE"), index=True
    )
    author_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    body: Mapped[str] = mapped_column(Text)
    is_internal: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    ticket: Mapped[SupportTicket] = relationship(back_populates="messages")


class PlatformSetting(Base):
    __tablename__ = "platform_settings"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    value: Mapped[dict] = mapped_column(JSON, default=dict)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    description: Mapped[str | None] = mapped_column(String(300), nullable=True)
    updated_by_user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class FeatureFlag(Base):
    __tablename__ = "feature_flags"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    description: Mapped[str | None] = mapped_column(String(300), nullable=True)
    updated_by_user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class ServiceRegistry(Base):
    __tablename__ = "service_registry"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    base_url: Mapped[str] = mapped_column(String(400))
    health_path: Mapped[str] = mapped_column(String(120), default="/health")
    ready_path: Mapped[str] = mapped_column(String(120), default="/ready")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    critical: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    timeout_seconds: Mapped[float] = mapped_column(Float, default=3.0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class ServiceHealthCheck(Base):
    __tablename__ = "service_health_checks"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_name: Mapped[str] = mapped_column(String(100), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    health_ok: Mapped[bool] = mapped_column(Boolean)
    ready_ok: Mapped[bool] = mapped_column(Boolean)
    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    detail: Mapped[dict] = mapped_column(JSON, default=dict)
    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )


class JobRecord(Base):
    __tablename__ = "job_records"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_type: Mapped[str] = mapped_column(String(50), index=True)
    target_service: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    resource_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="QUEUED", index=True)
    parameters: Mapped[dict] = mapped_column(JSON, default=dict)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    result: Mapped[dict] = mapped_column(JSON, default=dict)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    requested_by_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class OutboxEvent(RelayState, Base):
    __tablename__ = "outbox_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type: Mapped[str] = mapped_column(String(160), index=True)
    aggregate_type: Mapped[str] = mapped_column(String(80))
    aggregate_id: Mapped[str] = mapped_column(String(160), index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

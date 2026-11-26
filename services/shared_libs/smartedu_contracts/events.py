from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .context import ensure_correlation_id, get_causation_id


def utc_now() -> datetime:
    return datetime.now(UTC)


class EventEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    event_type: str = Field(min_length=3, max_length=160)
    event_version: int = Field(default=1, ge=1)
    source: str = Field(min_length=2, max_length=80)
    occurred_at: datetime = Field(default_factory=utc_now)

    correlation_id: str = Field(min_length=1, max_length=128)
    causation_id: str | None = Field(default=None, max_length=128)

    actor_user_id: uuid.UUID | None = None
    subject: str | None = Field(default=None, max_length=240)
    data: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("occurred_at")
    @classmethod
    def _must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("occurred_at must be timezone-aware")
        return value.astimezone(UTC)


def new_event(
    *,
    event_type: str,
    source: str,
    data: dict[str, Any],
    event_version: int = 1,
    actor_user_id: uuid.UUID | None = None,
    subject: str | None = None,
    correlation_id: str | None = None,
    causation_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> EventEnvelope:
    return EventEnvelope(
        event_type=event_type,
        event_version=event_version,
        source=source,
        actor_user_id=actor_user_id,
        subject=subject,
        data=data,
        metadata=metadata or {},
        correlation_id=correlation_id or ensure_correlation_id(),
        causation_id=causation_id or get_causation_id(),
    )

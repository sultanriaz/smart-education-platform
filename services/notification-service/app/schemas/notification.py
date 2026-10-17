from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

Channel = Literal["IN_APP", "EMAIL"]
Priority = Literal["LOW", "NORMAL", "HIGH", "URGENT"]
TargetKind = Literal["DIRECT", "ROLE", "SECTION", "COURSE", "PROGRAM", "DEPARTMENT"]


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    recipient_user_id: uuid.UUID
    category: str
    priority: str
    title: str
    body: str
    data: dict
    status: str
    read_at: datetime | None
    created_at: datetime


class NotificationListOut(BaseModel):
    items: list[NotificationOut]
    total: int
    offset: int
    limit: int


class UnreadCountOut(BaseModel):
    unread_count: int


class PreferenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
    in_app_enabled: bool
    email_enabled: bool
    muted_categories: list[str]


class PreferenceUpdate(BaseModel):
    in_app_enabled: bool | None = None
    email_enabled: bool | None = None
    muted_categories: list[str] | None = None


class TemplateCreate(BaseModel):
    code: str = Field(min_length=2, max_length=120, pattern=r"^[a-zA-Z0-9_.-]+$")
    title_template: str = Field(min_length=1, max_length=255)
    body_template: str = Field(min_length=1, max_length=10000)
    default_channels: list[Channel] = ["IN_APP"]
    category: str = Field(default="general", min_length=1, max_length=80)
    enabled: bool = True


class TemplateUpdate(BaseModel):
    title_template: str | None = Field(default=None, min_length=1, max_length=255)
    body_template: str | None = Field(default=None, min_length=1, max_length=10000)
    default_channels: list[Channel] | None = None
    category: str | None = Field(default=None, min_length=1, max_length=80)
    enabled: bool | None = None


class TemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    title_template: str
    body_template: str
    default_channels: list[str]
    category: str
    enabled: bool
    created_by_user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class DirectRecipient(BaseModel):
    user_id: uuid.UUID
    email: EmailStr | None = None


class CampaignTarget(BaseModel):
    kind: TargetKind
    recipients: list[DirectRecipient] | None = None
    role: Literal["admin", "teacher", "student"] | None = None
    section_id: uuid.UUID | None = None
    course_id: uuid.UUID | None = None
    program_id: uuid.UUID | None = None
    department_id: uuid.UUID | None = None

    @model_validator(mode="after")
    def validate_target(self):
        if self.kind == "DIRECT" and not self.recipients:
            raise ValueError("DIRECT target requires recipients")
        if self.kind == "ROLE" and not self.role:
            raise ValueError("ROLE target requires role")
        for kind, value in (
            ("SECTION", self.section_id), ("COURSE", self.course_id),
            ("PROGRAM", self.program_id), ("DEPARTMENT", self.department_id),
        ):
            if self.kind == kind and not value:
                raise ValueError(f"{kind} target requires a matching ID")
        return self


class CampaignCreate(BaseModel):
    target: CampaignTarget
    template_code: str | None = None
    title: str | None = Field(default=None, max_length=255)
    body: str | None = Field(default=None, max_length=10000)
    template_data: dict = {}
    category: str = Field(default="general", min_length=1, max_length=80)
    priority: Priority = "NORMAL"
    channels: list[Channel] | None = None
    data: dict = Field(default_factory=dict)
    draft: bool = False
    publish_at: datetime | None = None
    expires_at: datetime | None = None

    @model_validator(mode="after")
    def validate_content(self):
        for name in ("publish_at", "expires_at"):
            value = getattr(self, name)
            if value is not None and (value.tzinfo is None or value.utcoffset() is None):
                raise ValueError(f"{name} must carry a timezone offset")
        if self.expires_at and self.publish_at and self.expires_at <= self.publish_at:
            raise ValueError("expires_at must be after publish_at")
        if not self.template_code and (not self.title or not self.body):
            raise ValueError("Provide template_code or both title and body")
        return self


class CampaignOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_by_user_id: uuid.UUID
    target_kind: str
    target_value: dict
    template_code: str | None
    title: str | None
    body: str | None
    category: str
    channels: list[str]
    status: str
    recipient_count: int
    priority: str
    data: dict
    scheduled_for: datetime | None
    expires_at: datetime | None
    created_at: datetime


class DeliveryAttemptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    notification_id: uuid.UUID
    channel: str
    status: str
    attempt_number: int
    provider_message_id: str | None
    last_error: str | None
    next_attempt_at: datetime | None
    created_at: datetime
    updated_at: datetime


class InternalEventIn(BaseModel):
    event_id: str = Field(min_length=1, max_length=160)
    source_service: str = Field(min_length=1, max_length=100)
    event_type: str = Field(min_length=1, max_length=160)
    occurred_at: datetime | None = None
    payload: dict = {}
    targets: dict = {}


class InternalEventAck(BaseModel):
    accepted: bool
    duplicate: bool = False
    inbox_event_id: uuid.UUID
    status: str

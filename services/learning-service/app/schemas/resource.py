from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from app.domain.entities.models import ResourceStatus, ResourceType, TargetType


class TargetInput(BaseModel):
    target_type: TargetType
    target_id: uuid.UUID


class ResourceCreate(BaseModel):
    title: str = Field(min_length=2, max_length=240)
    description: str | None = None
    resource_type: ResourceType
    category_id: uuid.UUID | None = None
    tags: list[str] = Field(default_factory=list, max_length=30)
    targets: list[TargetInput] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def unique_targets(self):
        keys = {(x.target_type, x.target_id) for x in self.targets}
        if len(keys) != len(self.targets):
            raise ValueError("Duplicate resource targets are not allowed")
        return self


class ResourceUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=240)
    description: str | None = None
    category_id: uuid.UUID | None = None
    tags: list[str] | None = Field(default=None, max_length=30)
    targets: list[TargetInput] | None = Field(default=None, min_length=1, max_length=100)


class VersionCreate(BaseModel):
    text_content: str | None = None
    external_url: HttpUrl | None = None
    change_note: str | None = Field(default=None, max_length=500)


class VersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    resource_id: uuid.UUID
    version_number: int
    created_by_user_id: uuid.UUID
    text_content: str | None
    external_url: str | None
    storage_key: str | None
    original_filename: str | None
    mime_type: str | None
    size_bytes: int | None
    checksum_sha256: str | None
    change_note: str | None
    created_at: datetime


class TargetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    target_type: TargetType
    target_id: uuid.UUID


class ResourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    description: str | None
    resource_type: ResourceType
    status: ResourceStatus
    category_id: uuid.UUID | None
    creator_user_id: uuid.UUID
    tags: list[str]
    targets: list[TargetOut]
    versions: list[VersionOut]
    published_at: datetime | None
    archived_at: datetime | None
    created_at: datetime
    updated_at: datetime


class RecommendationOut(BaseModel):
    resource: ResourceOut
    score: int
    reason: str

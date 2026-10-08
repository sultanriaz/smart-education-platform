from __future__ import annotations

import os
import uuid
from datetime import datetime
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SettingUpsert(BaseModel):
    value: dict
    is_public: bool = False
    description: str | None = None


class SettingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    value: dict
    is_public: bool
    description: str | None
    updated_at: datetime


class FeatureFlagUpsert(BaseModel):
    enabled: bool
    config: dict = {}
    description: str | None = None


class FeatureFlagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    enabled: bool
    config: dict
    description: str | None
    updated_at: datetime


class ServiceRegistryCreate(BaseModel):
    service_name: str = Field(min_length=2, max_length=100)
    base_url: str = Field(min_length=4, max_length=400)
    health_path: str = "/health"
    ready_path: str = "/ready"
    enabled: bool = True
    critical: bool = False
    timeout_seconds: float = Field(default=3.0, gt=0, le=30)

    @model_validator(mode="after")
    def trusted_target(self):
        url = urlsplit(self.base_url)
        names = (
            "identity",
            "academic",
            "attendance",
            "scheduling",
            "notification",
            "facility",
            "learning",
            "assessment",
            "reporting",
            "platform",
        )
        allowed = {"localhost", "127.0.0.1", "host.docker.internal"}
        allowed.update(f"{name}-service" for name in names)
        allowed.update(f"{name}-service.smartedu.svc.cluster.local" for name in names)
        allowed.update(
            host.strip()
            for host in os.getenv("SERVICE_REGISTRY_ALLOWED_HOSTS", "").split(",")
            if host.strip()
        )
        if (
            url.scheme not in {"http", "https"}
            or url.hostname not in allowed
            or url.username
            or url.password
            or url.query
            or url.fragment
            or url.path not in {"", "/"}
        ):
            raise ValueError("Registry target must be an explicitly trusted service origin")
        if any(
            not path.startswith("/") or path.startswith("//") or "?" in path or "#" in path
            for path in (self.health_path, self.ready_path)
        ):
            raise ValueError("Health paths must be relative to the service origin")
        return self


class ServiceRegistryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    service_name: str
    base_url: str
    health_path: str
    ready_path: str
    enabled: bool
    critical: bool
    timeout_seconds: float


class JobCreate(BaseModel):
    job_type: str = Field(pattern="^(IMPORT|EXPORT|HEALTH_SWEEP|REINDEX)$")
    target_service: str | None = None
    resource_type: str | None = None
    parameters: dict = {}
    payload: dict = {}


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_type: str
    target_service: str | None
    resource_type: str | None
    status: str
    parameters: dict
    result: dict
    error: str | None
    attempts: int
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None

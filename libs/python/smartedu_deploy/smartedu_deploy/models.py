from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

DNS_NAME = re.compile(r"^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")


class Resources(BaseModel):
    cpu_request: str
    memory_request: str
    cpu_limit: str
    memory_limit: str


class Workload(BaseModel):
    component: str
    kind: Literal["python-service", "frontend", "gateway"]
    port: int = Field(ge=1, le=65535)
    replicas: int = Field(ge=2)
    min_replicas: int = Field(ge=2)
    max_replicas: int = Field(ge=2)
    cpu_target_percent: int = Field(default=70, ge=10, le=95)
    memory_target_percent: int = Field(default=75, ge=10, le=95)
    resources: Resources

    @model_validator(mode="after")
    def valid_scaling(self):
        if self.min_replicas > self.replicas:
            raise ValueError("min_replicas cannot exceed replicas")
        if self.replicas > self.max_replicas:
            raise ValueError("replicas cannot exceed max_replicas")
        return self


class ExternalDependency(BaseModel):
    name: str
    kind: Literal[
        "postgresql",
        "redis-cache",
        "redis-durable",
        "rabbitmq",
        "object-storage",
        "email",
        "observability",
    ]
    highly_available: bool = True
    private_network_only: bool = True
    backup_required: bool = False


class ProductionTopology(BaseModel):
    version: int = 1
    namespace: str = "smartedu"
    public_host: str
    tls_secret_name: str
    ingress_class: str = "nginx"
    workloads: list[Workload]
    external_dependencies: list[ExternalDependency]

    @field_validator("public_host")
    @classmethod
    def validate_public_host(cls, value: str) -> str:
        if not DNS_NAME.fullmatch(value):
            raise ValueError("public_host must be a DNS hostname")
        return value

    @field_validator("workloads")
    @classmethod
    def unique_workloads(cls, value: list[Workload]) -> list[Workload]:
        names = [item.component for item in value]
        if len(names) != len(set(names)):
            raise ValueError("workload component names must be unique")
        return value


class ReleaseImage(BaseModel):
    component: str
    repository: str
    digest: str
    immutable_ref: str

    @field_validator("digest")
    @classmethod
    def valid_digest(cls, value: str) -> str:
        if not value.startswith("sha256:") or len(value) != 71:
            raise ValueError("invalid sha256 digest")
        int(value.removeprefix("sha256:"), 16)
        return value

    @model_validator(mode="after")
    def immutable_matches_digest(self):
        if not self.immutable_ref.endswith("@" + self.digest):
            raise ValueError("immutable_ref must end with @digest")
        return self


class ReleaseManifest(BaseModel):
    schema_version: int = 1
    release_tag: str
    commit_sha: str
    generated_at: str
    source_repository: str
    images: list[ReleaseImage]
    migration_policy: str = "forward-only"
    migration_components: list[str] = Field(default_factory=list)

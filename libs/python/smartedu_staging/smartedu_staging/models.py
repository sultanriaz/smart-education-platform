from __future__ import annotations

import re

from pydantic import BaseModel, Field, field_validator, model_validator

DNS_NAME = re.compile(r"^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")


class WorkloadOverride(BaseModel):
    component: str
    replicas: int = Field(ge=1)
    min_replicas: int = Field(ge=1)
    max_replicas: int = Field(ge=1)

    @model_validator(mode="after")
    def validate_scale(self):
        if self.min_replicas > self.replicas:
            raise ValueError("min_replicas cannot exceed replicas")
        if self.replicas > self.max_replicas:
            raise ValueError("replicas cannot exceed max_replicas")
        return self


class StagingTopology(BaseModel):
    version: int = 1
    namespace: str = "smartedu-staging"
    public_host: str
    tls_secret_name: str = "smartedu-staging-tls"
    ingress_class: str = "nginx"
    workload_overrides: list[WorkloadOverride]
    required_secrets: list[str]
    stateful_dependencies: list[str]

    @field_validator("public_host")
    @classmethod
    def validate_host(cls, value: str) -> str:
        if not DNS_NAME.fullmatch(value):
            raise ValueError("public_host must be a valid DNS hostname")
        return value

    @field_validator("workload_overrides")
    @classmethod
    def unique_components(cls, value: list[WorkloadOverride]):
        names = [item.component for item in value]
        if len(names) != len(set(names)):
            raise ValueError("workload_overrides must be unique")
        return value


class ReleaseImage(BaseModel):
    component: str
    immutable_ref: str
    digest: str

    @model_validator(mode="after")
    def validate_digest_ref(self):
        if not self.digest.startswith("sha256:") or len(self.digest) != 71:
            raise ValueError("digest must be sha256:<64 hex>")
        int(self.digest.removeprefix("sha256:"), 16)
        if not self.immutable_ref.endswith("@" + self.digest):
            raise ValueError("immutable_ref must be digest pinned")
        return self


class ReleaseManifest(BaseModel):
    release_tag: str
    commit_sha: str
    images: list[ReleaseImage]
    migration_components: list[str] = Field(default_factory=list)

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class Component(BaseModel):
    name: str
    kind: Literal["python-service", "frontend", "gateway"]
    path: str
    dockerfile: str
    image_suffix: str
    test_command: str | None = None
    migration_command: str | None = None
    deploy_service: str | None = None
    watched_paths: list[str] = Field(default_factory=list)

    @property
    def build_context(self) -> str:
        return "." if self.kind == "python-service" else self.path


class ComponentCatalog(BaseModel):
    version: int = 1
    global_watched_paths: list[str] = Field(default_factory=list)
    components: list[Component]

    @field_validator("components")
    @classmethod
    def unique_names(cls, value: list[Component]) -> list[Component]:
        names = [item.name for item in value]
        if len(names) != len(set(names)):
            raise ValueError("component names must be unique")
        return value


class ReleaseImage(BaseModel):
    component: str
    repository: str
    digest: str
    immutable_ref: str

    @field_validator("digest")
    @classmethod
    def digest_is_sha256(cls, value: str) -> str:
        if not value.startswith("sha256:") or len(value) != 71:
            raise ValueError("digest must be sha256:<64 hex>")
        int(value[7:], 16)
        return value


class ReleaseManifest(BaseModel):
    schema_version: int = 1
    release_tag: str
    commit_sha: str
    generated_at: str
    source_repository: str
    images: list[ReleaseImage]
    migration_policy: Literal["forward-only", "explicit-reversible"] = "forward-only"
    migration_components: list[str] = Field(default_factory=list)

    @field_validator("commit_sha")
    @classmethod
    def full_sha(cls, value: str) -> str:
        if len(value) != 40:
            raise ValueError("commit_sha must be a full 40-character Git SHA")
        int(value, 16)
        return value

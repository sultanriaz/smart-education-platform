from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

LaunchPhaseStatus = Literal["NOT_STARTED", "IN_PROGRESS", "PASS", "FAIL", "ABORTED"]
LaunchOutcome = Literal["SUCCEEDED", "ROLLED_BACK", "ABORTED", "FAILED"]
IncidentSeverity = Literal["SEV1", "SEV2", "SEV3", "SEV4"]


class ReleaseImage(BaseModel):
    component: str
    immutable_ref: str
    digest: str

    @model_validator(mode="after")
    def validate_ref(self):
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

    @field_validator("commit_sha")
    @classmethod
    def full_sha(cls, value: str) -> str:
        if len(value) != 40:
            raise ValueError("commit_sha must be a full 40-character Git SHA")
        int(value, 16)
        return value

    @field_validator("images")
    @classmethod
    def unique_images(cls, value: list[ReleaseImage]) -> list[ReleaseImage]:
        names = [item.component for item in value]
        if len(names) != len(set(names)):
            raise ValueError("release image components must be unique")
        return value


class PhaseRecord(BaseModel):
    name: str
    status: LaunchPhaseStatus
    started_at: datetime | None = None
    completed_at: datetime | None = None
    operator: str | None = None
    notes: str = ""
    evidence_paths: list[str] = Field(default_factory=list)


class LaunchIncident(BaseModel):
    id: str
    severity: IncidentSeverity
    summary: str
    opened_at: datetime
    status: Literal["OPEN", "MITIGATED", "CLOSED"] = "OPEN"
    owner: str | None = None
    notes: str = ""


class LaunchRecord(BaseModel):
    schema_version: int = 1
    launch_id: str
    release_tag: str
    commit_sha: str
    production_url: str
    kube_context: str
    started_at: datetime
    completed_at: datetime | None = None
    readiness_run_id: str
    backup_reference: str | None = None
    phases: list[PhaseRecord] = Field(default_factory=list)
    incidents: list[LaunchIncident] = Field(default_factory=list)
    outcome: LaunchOutcome | None = None
    final_notes: str = ""

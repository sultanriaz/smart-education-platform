from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

CheckpointStatus = Literal["NOT_RUN", "PASS", "WARN", "FAIL", "BLOCKED"]
IssueSeverity = Literal["SEV1", "SEV2", "SEV3", "SEV4"]
IssueStatus = Literal["OPEN", "MITIGATING", "MONITORING", "CLOSED", "DEFERRED"]
Disposition = Literal["STABLE", "STABLE_WITH_FOLLOWUPS", "UNSTABLE"]


class StabilizationCheckpoint(BaseModel):
    id: str
    category: str
    title: str
    mandatory: bool = True
    owner_role: str
    evidence_required: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)


class CheckpointResult(BaseModel):
    checkpoint_id: str
    status: CheckpointStatus
    observed_by: str
    observed_at: datetime
    notes: str = ""
    evidence_paths: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def failure_needs_notes(self):
        if self.status in {"WARN", "FAIL", "BLOCKED"} and not self.notes.strip():
            raise ValueError("WARN/FAIL/BLOCKED checkpoint results require explanatory notes")
        return self


class StabilizationIssue(BaseModel):
    id: str
    severity: IssueSeverity
    title: str
    status: IssueStatus = "OPEN"
    owner: str
    opened_at: datetime
    closed_at: datetime | None = None
    linked_incident_id: str | None = None
    linked_release_tag: str | None = None
    mitigation: str = ""
    notes: str = ""

    @model_validator(mode="after")
    def closure_rules(self):
        if self.status == "CLOSED" and self.closed_at is None:
            raise ValueError("CLOSED issue requires closed_at")
        return self


class FollowUp(BaseModel):
    id: str
    title: str
    owner: str
    target_date: datetime | None = None
    severity: Literal["HIGH", "MEDIUM", "LOW"]
    status: Literal["OPEN", "IN_PROGRESS", "CLOSED"] = "OPEN"
    notes: str = ""


class StabilizationApproval(BaseModel):
    role: Literal[
        "TechnicalLead",
        "OperationsOwner",
        "SecurityOwner",
        "ProductOwner",
        "ProjectSupervisor",
    ]
    approver: str
    approved_at: datetime
    decision: Literal["APPROVE", "APPROVE_WITH_FOLLOWUPS", "REJECT"]
    conditions: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def conditional_rules(self):
        if self.decision == "APPROVE_WITH_FOLLOWUPS" and not self.conditions:
            raise ValueError("APPROVE_WITH_FOLLOWUPS requires at least one condition")
        return self


class StabilizationRun(BaseModel):
    schema_version: int = 1
    run_id: str
    launch_id: str
    release_tag: str
    commit_sha: str
    production_url: str
    started_at: datetime
    completed_at: datetime | None = None
    checkpoints: list[CheckpointResult] = Field(default_factory=list)
    issues: list[StabilizationIssue] = Field(default_factory=list)
    followups: list[FollowUp] = Field(default_factory=list)
    approvals: list[StabilizationApproval] = Field(default_factory=list)
    disposition: Disposition | None = None
    final_notes: str = ""

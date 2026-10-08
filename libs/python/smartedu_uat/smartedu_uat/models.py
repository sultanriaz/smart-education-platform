from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

Priority = Literal["P0", "P1", "P2", "P3"]
ExecutionType = Literal["manual", "automated", "hybrid"]
ScenarioStatus = Literal["NOT_RUN", "PASS", "FAIL", "BLOCKED", "WAIVED"]
DefectSeverity = Literal["BLOCKER", "CRITICAL", "MAJOR", "MINOR", "COSMETIC"]
DefectStatus = Literal["OPEN", "IN_PROGRESS", "FIXED", "RETEST", "CLOSED", "DEFERRED"]
SignoffDecision = Literal["APPROVE", "APPROVE_WITH_CONDITIONS", "REJECT"]


class UATScenario(BaseModel):
    id: str
    role: Literal["Student", "Teacher", "Admin", "CrossRole"]
    title: str
    domain: str
    priority: Priority
    execution: ExecutionType
    preconditions: list[str] = Field(default_factory=list)
    steps: list[str]
    expected_results: list[str]
    requirement_refs: list[str]
    evidence: list[str] = Field(default_factory=list)
    automated_reference: str | None = None

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        if not value.startswith("UAT-"):
            raise ValueError("scenario IDs must start with UAT-")
        return value

    @model_validator(mode="after")
    def automated_reference_required_when_automated(self):
        if self.execution == "automated" and not self.automated_reference:
            raise ValueError("automated scenarios require automated_reference")
        return self


class ScenarioResult(BaseModel):
    scenario_id: str
    status: ScenarioStatus
    executed_by: str
    executed_at: datetime
    notes: str = ""
    evidence_paths: list[str] = Field(default_factory=list)
    defect_ids: list[str] = Field(default_factory=list)
    waiver_id: str | None = None

    @model_validator(mode="after")
    def waiver_required(self):
        if self.status == "WAIVED" and not self.waiver_id:
            raise ValueError("WAIVED result requires waiver_id")
        return self


class UATDefect(BaseModel):
    id: str
    scenario_id: str | None = None
    severity: DefectSeverity
    title: str
    status: DefectStatus = "OPEN"
    owner: str | None = None
    notes: str = ""
    workaround: str | None = None


class Signoff(BaseModel):
    role: Literal[
        "StudentRepresentative",
        "TeacherRepresentative",
        "AdminRepresentative",
        "ProductOwner",
        "ProjectSupervisor",
    ]
    signer: str
    decision: SignoffDecision
    signed_at: datetime
    conditions: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def conditions_required_when_conditional(self):
        if self.decision == "APPROVE_WITH_CONDITIONS" and not self.conditions:
            raise ValueError("APPROVE_WITH_CONDITIONS requires at least one condition")
        return self


class UATPolicy(BaseModel):
    minimum_pass_rate_percent: float = Field(default=95.0, ge=0, le=100)
    require_all_p0_pass: bool = True
    require_all_p1_pass: bool = True
    max_open_blocker: int = 0
    max_open_critical: int = 0
    max_open_major: int = 0
    required_signoff_roles: list[str]
    allow_blocked_with_approved_waiver: bool = False


class UATRun(BaseModel):
    schema_version: int = 1
    run_id: str
    release_tag: str
    commit_sha: str
    staging_url: str
    started_at: datetime
    completed_at: datetime | None = None
    results: list[ScenarioResult] = Field(default_factory=list)
    defects: list[UATDefect] = Field(default_factory=list)
    signoffs: list[Signoff] = Field(default_factory=list)

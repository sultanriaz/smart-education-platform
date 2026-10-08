from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

CheckStatus = Literal["NOT_RUN", "PASS", "FAIL", "BLOCKED", "WAIVED"]
RiskSeverity = Literal["BLOCKER", "CRITICAL", "HIGH", "MEDIUM", "LOW"]
RiskStatus = Literal["OPEN", "MITIGATING", "ACCEPTED", "CLOSED"]
ApprovalDecision = Literal["APPROVE", "APPROVE_WITH_CONDITIONS", "REJECT"]
ReadinessDecision = Literal["GO", "GO_WITH_CONDITIONS", "NO_GO"]


class ReadinessCheck(BaseModel):
    id: str
    category: str
    title: str
    mandatory: bool = True
    owner_role: str
    evidence_required: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)
    description: str = ""

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        if not value.startswith("PR-"):
            raise ValueError("readiness check IDs must start with PR-")
        return value


class CheckResult(BaseModel):
    check_id: str
    status: CheckStatus
    verified_by: str
    verified_at: datetime
    notes: str = ""
    evidence_paths: list[str] = Field(default_factory=list)
    waiver_id: str | None = None

    @model_validator(mode="after")
    def waiver_rules(self):
        if self.status == "WAIVED" and not self.waiver_id:
            raise ValueError("WAIVED check requires waiver_id")
        return self


class ReadinessRisk(BaseModel):
    id: str
    title: str
    severity: RiskSeverity
    status: RiskStatus = "OPEN"
    owner: str
    mitigation: str
    due_at: datetime | None = None
    acceptance_reason: str | None = None

    @model_validator(mode="after")
    def accepted_requires_reason(self):
        if self.status == "ACCEPTED" and not self.acceptance_reason:
            raise ValueError("ACCEPTED risk requires acceptance_reason")
        return self


class Approval(BaseModel):
    role: Literal[
        "TechnicalLead",
        "OperationsOwner",
        "SecurityOwner",
        "ProductOwner",
        "ProjectSupervisor",
    ]
    approver: str
    decision: ApprovalDecision
    approved_at: datetime
    conditions: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def conditional_requires_conditions(self):
        if self.decision == "APPROVE_WITH_CONDITIONS" and not self.conditions:
            raise ValueError("APPROVE_WITH_CONDITIONS requires at least one condition")
        return self


class ReadinessPolicy(BaseModel):
    require_all_mandatory_pass: bool = True
    allow_mandatory_waiver: bool = False
    max_open_blocker: int = 0
    max_open_critical: int = 0
    max_open_high: int = 0
    required_approval_roles: list[str]
    require_uat_pass: bool = True
    require_release_identity_match: bool = True


class ReadinessRun(BaseModel):
    schema_version: int = 1
    run_id: str
    release_tag: str
    commit_sha: str
    production_url: str
    started_at: datetime
    completed_at: datetime | None = None
    checks: list[CheckResult] = Field(default_factory=list)
    risks: list[ReadinessRisk] = Field(default_factory=list)
    approvals: list[Approval] = Field(default_factory=list)
    final_decision: ReadinessDecision | None = None
    decision_notes: str = ""

from __future__ import annotations

from dataclasses import dataclass

from .models import StabilizationCheckpoint, StabilizationRun


@dataclass(frozen=True, slots=True)
class StabilizationGate:
    passed: bool
    reasons: list[str]
    mandatory_passed: int
    mandatory_total: int


def evaluate_stabilization(
    *,
    checkpoints: list[StabilizationCheckpoint],
    run: StabilizationRun,
    policy: dict,
) -> StabilizationGate:
    reasons: list[str] = []
    results = {item.checkpoint_id: item for item in run.checkpoints}
    mandatory = [item for item in checkpoints if item.mandatory]
    mandatory_passed = 0

    for checkpoint in mandatory:
        result = results.get(checkpoint.id)
        if result is None:
            reasons.append(f"mandatory checkpoint not run: {checkpoint.id}")
            continue
        if result.status != "PASS":
            reasons.append(f"mandatory checkpoint not PASS: {checkpoint.id}={result.status}")
            continue
        mandatory_passed += 1

    max_open = policy.get("max_open_issues", {})
    for severity in ("SEV1", "SEV2", "SEV3"):
        allowed = int(max_open.get(severity, 0))
        count = sum(
            issue.severity == severity and issue.status in {"OPEN", "MITIGATING", "MONITORING"}
            for issue in run.issues
        )
        if count > allowed:
            reasons.append(f"open {severity} issues {count} exceed allowed {allowed}")

    if policy.get("require_all_high_followups_closed", True):
        high_open = [
            item.id for item in run.followups if item.severity == "HIGH" and item.status != "CLOSED"
        ]
        if high_open:
            reasons.append(f"HIGH follow-ups remain open: {high_open}")

    required_roles = set(policy.get("required_approval_roles", []))
    approved_roles = {
        item.role
        for item in run.approvals
        if item.decision in {"APPROVE", "APPROVE_WITH_FOLLOWUPS"}
    }
    missing = sorted(required_roles - approved_roles)
    if missing:
        reasons.append(f"missing required approvals: {missing}")

    rejected = sorted(item.role for item in run.approvals if item.decision == "REJECT")
    if rejected:
        reasons.append(f"rejected approvals: {rejected}")

    if run.completed_at is None:
        reasons.append("stabilization run is not completed")

    allowed_dispositions = set(
        policy.get(
            "allowed_dispositions",
            ["STABLE", "STABLE_WITH_FOLLOWUPS"],
        )
    )
    if run.disposition not in allowed_dispositions:
        reasons.append(f"disposition {run.disposition!r} not allowed by stabilization policy")

    return StabilizationGate(
        passed=not reasons,
        reasons=reasons,
        mandatory_passed=mandatory_passed,
        mandatory_total=len(mandatory),
    )

from __future__ import annotations

from dataclasses import dataclass

from .models import ReadinessCheck, ReadinessPolicy, ReadinessRun

OPEN_RISK_STATES = {"OPEN", "MITIGATING"}


@dataclass(frozen=True, slots=True)
class ReadinessGate:
    passed: bool
    reasons: list[str]
    mandatory_passed: int
    mandatory_total: int


def evaluate_readiness(
    *,
    checks: list[ReadinessCheck],
    run: ReadinessRun,
    policy: ReadinessPolicy,
) -> ReadinessGate:
    reasons: list[str] = []
    result_map = {item.check_id: item for item in run.checks}
    check_ids = {item.id for item in checks}

    unknown = sorted(set(result_map) - check_ids)
    if unknown:
        reasons.append(f"unknown check results: {unknown}")

    mandatory = [item for item in checks if item.mandatory]
    mandatory_passed = 0

    for check in mandatory:
        result = result_map.get(check.id)
        if not result:
            reasons.append(f"mandatory check not run: {check.id}")
            continue

        if result.status == "PASS":
            mandatory_passed += 1
            continue

        if result.status == "WAIVED":
            if policy.allow_mandatory_waiver and result.waiver_id:
                mandatory_passed += 1
            else:
                reasons.append(f"mandatory check waived but waivers disabled: {check.id}")
            continue

        reasons.append(f"mandatory check not PASS: {check.id}={result.status}")

    if run.completed_at is None:
        reasons.append("readiness run is not marked completed")

    limits = {
        "BLOCKER": policy.max_open_blocker,
        "CRITICAL": policy.max_open_critical,
        "HIGH": policy.max_open_high,
    }
    for severity, limit in limits.items():
        count = sum(
            risk.severity == severity and risk.status in OPEN_RISK_STATES for risk in run.risks
        )
        if count > limit:
            reasons.append(f"open {severity} risks {count} exceed allowed {limit}")

    approved_roles = {
        item.role
        for item in run.approvals
        if item.decision in {"APPROVE", "APPROVE_WITH_CONDITIONS"}
    }
    missing = sorted(set(policy.required_approval_roles) - approved_roles)
    if missing:
        reasons.append(f"missing required approvals: {missing}")

    rejected = sorted(item.role for item in run.approvals if item.decision == "REJECT")
    if rejected:
        reasons.append(f"rejected approvals: {rejected}")

    if run.final_decision is None:
        reasons.append("final readiness decision not recorded")
    elif run.final_decision == "NO_GO":
        reasons.append("final readiness decision is NO_GO")

    return ReadinessGate(
        passed=not reasons,
        reasons=reasons,
        mandatory_passed=mandatory_passed,
        mandatory_total=len(mandatory),
    )

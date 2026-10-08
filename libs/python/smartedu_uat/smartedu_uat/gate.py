from __future__ import annotations

from dataclasses import dataclass

from .models import UATPolicy, UATRun, UATScenario

OPEN_DEFECT_STATES = {"OPEN", "IN_PROGRESS", "RETEST"}


@dataclass(frozen=True, slots=True)
class GateResult:
    passed: bool
    reasons: list[str]
    pass_rate_percent: float


def evaluate_gate(
    *,
    scenarios: list[UATScenario],
    run: UATRun,
    policy: UATPolicy,
) -> GateResult:
    reasons: list[str] = []
    results = {item.scenario_id: item for item in run.results}
    scenario_ids = {item.id for item in scenarios}

    unknown = sorted(set(results) - scenario_ids)
    if unknown:
        reasons.append(f"unknown scenario results: {unknown}")

    counted = [
        results[item.id]
        for item in scenarios
        if item.id in results and results[item.id].status in {"PASS", "FAIL", "BLOCKED", "WAIVED"}
    ]
    passed = sum(item.status == "PASS" for item in counted)
    denominator = sum(item.status in {"PASS", "FAIL", "BLOCKED"} for item in counted)
    pass_rate = 100.0 if denominator == 0 else (passed / denominator) * 100.0

    if run.completed_at is None:
        reasons.append("UAT run is not marked completed")

    not_run = [
        item.id
        for item in scenarios
        if item.id not in results or results[item.id].status == "NOT_RUN"
    ]
    if not_run:
        reasons.append(f"{len(not_run)} scenarios not run")

    blocked = [result.scenario_id for result in run.results if result.status == "BLOCKED"]
    if blocked:
        if not policy.allow_blocked_with_approved_waiver:
            reasons.append(f"blocked scenarios are not allowed: {sorted(blocked)}")
        else:
            missing_waiver = sorted(
                result.scenario_id
                for result in run.results
                if result.status == "BLOCKED" and not result.waiver_id
            )
            if missing_waiver:
                reasons.append(f"blocked scenarios missing approved waiver IDs: {missing_waiver}")

    if pass_rate < policy.minimum_pass_rate_percent:
        reasons.append(
            f"pass rate {pass_rate:.2f}% below required {policy.minimum_pass_rate_percent:.2f}%"
        )

    for priority, required in (
        ("P0", policy.require_all_p0_pass),
        ("P1", policy.require_all_p1_pass),
    ):
        if not required:
            continue
        bad = [
            item.id
            for item in scenarios
            if item.priority == priority
            and (item.id not in results or results[item.id].status != "PASS")
        ]
        if bad:
            reasons.append(f"{priority} scenarios not PASS: {bad}")

    severity_limits = {
        "BLOCKER": policy.max_open_blocker,
        "CRITICAL": policy.max_open_critical,
        "MAJOR": policy.max_open_major,
    }
    for severity, limit in severity_limits.items():
        count = sum(
            defect.severity == severity and defect.status in OPEN_DEFECT_STATES
            for defect in run.defects
        )
        if count > limit:
            reasons.append(f"open {severity} defects {count} exceed allowed {limit}")

    signed_roles = {
        signoff.role
        for signoff in run.signoffs
        if signoff.decision in {"APPROVE", "APPROVE_WITH_CONDITIONS"}
    }
    missing_roles = sorted(set(policy.required_signoff_roles) - signed_roles)
    if missing_roles:
        reasons.append(f"missing required signoffs: {missing_roles}")

    rejected_roles = sorted(
        signoff.role for signoff in run.signoffs if signoff.decision == "REJECT"
    )
    if rejected_roles:
        reasons.append(f"rejected signoffs: {rejected_roles}")

    return GateResult(
        passed=not reasons,
        reasons=reasons,
        pass_rate_percent=pass_rate,
    )

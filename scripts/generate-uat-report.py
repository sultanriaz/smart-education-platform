from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from smartedu_uat import (
    evaluate_gate,
    load_policy,
    load_run,
    load_scenarios,
)


def esc(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run")
    parser.add_argument("--policy", default="config/uat/policy.yaml")
    parser.add_argument("--scenarios", default="config/uat/scenarios")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    run = load_run(args.run)
    scenarios = load_scenarios(args.scenarios)
    policy = load_policy(args.policy)
    gate = evaluate_gate(scenarios=scenarios, run=run, policy=policy)

    scenario_lookup = {item.id: item for item in scenarios}
    result_lookup = {item.scenario_id: item for item in run.results}
    statuses = Counter(
        result_lookup[item.id].status if item.id in result_lookup else "NOT_RUN"
        for item in scenarios
    )
    severities = Counter(
        defect.severity
        for defect in run.defects
        if defect.status in {"OPEN", "IN_PROGRESS", "RETEST"}
    )

    lines = [
        "# Smart Education Platform — UAT Report",
        "",
        f"- **Run ID:** `{run.run_id}`",
        f"- **Release:** `{run.release_tag}`",
        f"- **Commit:** `{run.commit_sha}`",
        f"- **Staging:** `{run.staging_url}`",
        f"- **Started:** `{run.started_at.isoformat()}`",
        f"- **Completed:** `{run.completed_at.isoformat() if run.completed_at else 'Not recorded'}`",
        f"- **Gate:** **{'PASS' if gate.passed else 'FAIL'}**",
        f"- **Pass rate:** **{gate.pass_rate_percent:.2f}%**",
        "",
        "## Scenario summary",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]
    for status in ["PASS", "FAIL", "BLOCKED", "WAIVED", "NOT_RUN"]:
        lines.append(f"| {status} | {statuses.get(status, 0)} |")

    lines += [
        "",
        "## Scenario results",
        "",
        "| ID | Role | Priority | Scenario | Result | Tester | Evidence/Defects |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for scenario in scenarios:
        result = result_lookup.get(scenario.id)
        if result:
            detail = ", ".join(
                [*result.evidence_paths, *[f"defect:{x}" for x in result.defect_ids]]
            )
            lines.append(
                f"| {scenario.id} | {scenario.role} | {scenario.priority} | "
                f"{esc(scenario.title)} | {result.status} | "
                f"{esc(result.executed_by)} | {esc(detail)} |"
            )
        else:
            lines.append(
                f"| {scenario.id} | {scenario.role} | {scenario.priority} | "
                f"{esc(scenario.title)} | NOT_RUN |  |  |"
            )

    lines += [
        "",
        "## Open defects",
        "",
        "| ID | Severity | Status | Scenario | Title | Owner |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    open_defects = [
        defect
        for defect in run.defects
        if defect.status in {"OPEN", "IN_PROGRESS", "RETEST"}
    ]
    if open_defects:
        for defect in open_defects:
            lines.append(
                f"| {defect.id} | {defect.severity} | {defect.status} | "
                f"{defect.scenario_id or ''} | {esc(defect.title)} | "
                f"{esc(defect.owner or '')} |"
            )
    else:
        lines.append("| — | — | — | — | No open defects recorded | — |")

    lines += [
        "",
        "## Required sign-offs",
        "",
        "| Role | Signer | Decision | Conditions |",
        "| --- | --- | --- | --- |",
    ]
    if run.signoffs:
        for signoff in run.signoffs:
            lines.append(
                f"| {signoff.role} | {esc(signoff.signer)} | {signoff.decision} | "
                f"{esc('; '.join(signoff.conditions))} |"
            )
    else:
        lines.append("| — | — | No sign-offs recorded | — |")

    lines += ["", "## Gate evaluation", ""]
    if gate.passed:
        lines.append("**PASS — release satisfies the configured UAT gate.**")
    else:
        lines.append("**FAIL — release does not satisfy the configured UAT gate.**")
        lines.append("")
        for reason in gate.reasons:
            lines.append(f"- {reason}")

    lines += [
        "",
        "## Notes",
        "",
        "This report is generated from the structured UAT run record. "
        "Screenshots, logs, browser traces, accessibility output, and defect "
        "attachments remain separate evidence artifacts referenced by scenario results.",
        "",
    ]

    Path(args.output).write_text("\n".join(lines), encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

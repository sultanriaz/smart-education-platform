from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from smartedu_readiness import (
    evaluate_readiness,
    load_checks,
    load_policy,
    load_run,
)


def esc(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run")
    parser.add_argument("--checks", default="config/readiness/checks.yaml")
    parser.add_argument("--policy", default="config/readiness/policy.yaml")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    checks = load_checks(args.checks)
    run = load_run(args.run)
    policy = load_policy(args.policy)
    gate = evaluate_readiness(checks=checks, run=run, policy=policy)

    check_map = {item.id: item for item in checks}
    result_map = {item.check_id: item for item in run.checks}
    statuses = Counter(
        result_map[item.id].status if item.id in result_map else "NOT_RUN"
        for item in checks
    )
    open_risks = [
        risk for risk in run.risks if risk.status in {"OPEN", "MITIGATING"}
    ]

    lines = [
        "# Smart Education Platform — Production Readiness Report",
        "",
        f"- **Run ID:** `{run.run_id}`",
        f"- **Release:** `{run.release_tag}`",
        f"- **Commit:** `{run.commit_sha}`",
        f"- **Production URL:** `{run.production_url}`",
        f"- **Started:** `{run.started_at.isoformat()}`",
        f"- **Completed:** `{run.completed_at.isoformat() if run.completed_at else 'Not recorded'}`",
        f"- **Final decision:** **{run.final_decision or 'NOT RECORDED'}**",
        f"- **Gate:** **{'PASS' if gate.passed else 'FAIL'}**",
        f"- **Mandatory checks:** **{gate.mandatory_passed}/{gate.mandatory_total}**",
        "",
        "## Check summary",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]
    for status in ["PASS", "FAIL", "BLOCKED", "WAIVED", "NOT_RUN"]:
        lines.append(f"| {status} | {statuses.get(status, 0)} |")

    lines += [
        "",
        "## Readiness checks",
        "",
        "| ID | Category | Owner | Check | Result | Evidence |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for check in checks:
        result = result_map.get(check.id)
        status = result.status if result else "NOT_RUN"
        evidence = ", ".join(result.evidence_paths) if result else ""
        lines.append(
            f"| {check.id} | {esc(check.category)} | {esc(check.owner_role)} | "
            f"{esc(check.title)} | {status} | {esc(evidence)} |"
        )

    lines += [
        "",
        "## Open risks",
        "",
        "| ID | Severity | Status | Owner | Risk | Mitigation |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    if open_risks:
        for risk in open_risks:
            lines.append(
                f"| {risk.id} | {risk.severity} | {risk.status} | "
                f"{esc(risk.owner)} | {esc(risk.title)} | {esc(risk.mitigation)} |"
            )
    else:
        lines.append("| — | — | — | — | No open risks recorded | — |")

    lines += [
        "",
        "## Approvals",
        "",
        "| Role | Approver | Decision | Conditions |",
        "| --- | --- | --- | --- |",
    ]
    if run.approvals:
        for approval in run.approvals:
            lines.append(
                f"| {approval.role} | {esc(approval.approver)} | "
                f"{approval.decision} | {esc('; '.join(approval.conditions))} |"
            )
    else:
        lines.append("| — | — | No approvals recorded | — |")

    lines += ["", "## Gate evaluation", ""]
    if gate.passed:
        lines.append("**PASS — configured production-readiness gate is satisfied.**")
    else:
        lines.append("**FAIL — production-readiness gate is not satisfied.**")
        lines.append("")
        for reason in gate.reasons:
            lines.append(f"- {reason}")

    lines += [
        "",
        "## Decision notes",
        "",
        run.decision_notes or "No decision notes recorded.",
        "",
        "This report is generated from the structured readiness run. "
        "Operational screenshots, provider exports, security reports, restore "
        "evidence, and other attachments remain separate evidence artifacts.",
        "",
    ]

    Path(args.output).write_text("\n".join(lines), encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

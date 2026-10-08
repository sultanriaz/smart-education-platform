from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from smartedu_stabilization import (
    evaluate_stabilization,
    load_checkpoints,
    load_policy,
    load_run,
)


def esc(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run")
    parser.add_argument(
        "--checkpoints",
        default="config/stabilization/checkpoints.yaml",
    )
    parser.add_argument(
        "--policy",
        default="config/stabilization/policy.yaml",
    )
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    checkpoints = load_checkpoints(args.checkpoints)
    run = load_run(args.run)
    gate = evaluate_stabilization(
        checkpoints=checkpoints,
        run=run,
        policy=load_policy(args.policy),
    )
    result_map = {item.checkpoint_id: item for item in run.checkpoints}
    statuses = Counter(
        result_map[item.id].status
        if item.id in result_map
        else "NOT_RUN"
        for item in checkpoints
    )

    lines = [
        "# Smart Education Platform — Production Stabilization Report",
        "",
        f"- **Run ID:** `{run.run_id}`",
        f"- **Launch ID:** `{run.launch_id}`",
        f"- **Release:** `{run.release_tag}`",
        f"- **Commit:** `{run.commit_sha}`",
        f"- **Production URL:** `{run.production_url}`",
        f"- **Started:** `{run.started_at.isoformat()}`",
        f"- **Completed:** `{run.completed_at.isoformat() if run.completed_at else 'Not recorded'}`",
        f"- **Disposition:** **{run.disposition or 'NOT RECORDED'}**",
        f"- **Gate:** **{'PASS' if gate.passed else 'FAIL'}**",
        f"- **Mandatory checkpoints:** **{gate.mandatory_passed}/{gate.mandatory_total}**",
        "",
        "## Checkpoint summary",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]
    for status in ["PASS", "WARN", "FAIL", "BLOCKED", "NOT_RUN"]:
        lines.append(f"| {status} | {statuses.get(status, 0)} |")

    lines += [
        "",
        "## Checkpoints",
        "",
        "| ID | Category | Owner | Check | Result | Evidence/Notes |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for checkpoint in checkpoints:
        result = result_map.get(checkpoint.id)
        if result:
            detail = "; ".join(
                [
                    *result.evidence_paths,
                    result.notes,
                ]
            ).strip("; ")
            status = result.status
        else:
            detail = ""
            status = "NOT_RUN"
        lines.append(
            f"| {checkpoint.id} | {esc(checkpoint.category)} | "
            f"{esc(checkpoint.owner_role)} | {esc(checkpoint.title)} | "
            f"{status} | {esc(detail)} |"
        )

    lines += [
        "",
        "## Stabilization issues",
        "",
        "| ID | Severity | Status | Owner | Issue | Linked incident/release |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    if run.issues:
        for issue in run.issues:
            linked = "/".join(
                value
                for value in [
                    issue.linked_incident_id,
                    issue.linked_release_tag,
                ]
                if value
            )
            lines.append(
                f"| {issue.id} | {issue.severity} | {issue.status} | "
                f"{esc(issue.owner)} | {esc(issue.title)} | {esc(linked)} |"
            )
    else:
        lines.append("| — | — | — | — | No stabilization issues recorded | — |")

    lines += [
        "",
        "## Follow-ups",
        "",
        "| ID | Severity | Status | Owner | Target | Follow-up |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    if run.followups:
        for item in run.followups:
            lines.append(
                f"| {item.id} | {item.severity} | {item.status} | "
                f"{esc(item.owner)} | "
                f"{item.target_date.isoformat() if item.target_date else ''} | "
                f"{esc(item.title)} |"
            )
    else:
        lines.append("| — | — | — | — | — | No follow-ups recorded |")

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
                f"{approval.decision} | "
                f"{esc('; '.join(approval.conditions))} |"
            )
    else:
        lines.append("| — | — | No approvals recorded | — |")

    lines += ["", "## Gate evaluation", ""]
    if gate.passed:
        lines.append("**PASS — production stabilization closure criteria are satisfied.**")
    else:
        lines.append("**FAIL — stabilization closure criteria are not satisfied.**")
        lines.append("")
        for reason in gate.reasons:
            lines.append(f"- {reason}")

    lines += [
        "",
        "## Final notes",
        "",
        run.final_notes or "No final notes recorded.",
        "",
    ]

    Path(args.output).write_text("\n".join(lines), encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

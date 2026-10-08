from __future__ import annotations

import argparse
from pathlib import Path

from smartedu_launch import evaluate_launch, load_launch


def esc(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    launch = load_launch(args.record)
    gate = evaluate_launch(launch)

    lines = [
        "# Smart Education Platform — Production Launch Report",
        "",
        f"- **Launch ID:** `{launch.launch_id}`",
        f"- **Release:** `{launch.release_tag}`",
        f"- **Commit:** `{launch.commit_sha}`",
        f"- **Production URL:** `{launch.production_url}`",
        f"- **Kubernetes context:** `{launch.kube_context}`",
        f"- **Readiness run:** `{launch.readiness_run_id}`",
        f"- **Started:** `{launch.started_at.isoformat()}`",
        f"- **Completed:** `{launch.completed_at.isoformat() if launch.completed_at else 'Not recorded'}`",
        f"- **Outcome:** **{launch.outcome or 'NOT RECORDED'}**",
        f"- **Launch gate:** **{'PASS' if gate.passed else 'FAIL'}**",
        f"- **Backup reference:** `{launch.backup_reference or 'Not recorded'}`",
        "",
        "## Phases",
        "",
        "| Phase | Status | Operator | Started | Completed | Evidence / Notes |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    for phase in sorted(launch.phases, key=lambda item: item.name):
        evidence = ", ".join(phase.evidence_paths)
        detail = "; ".join(x for x in [evidence, phase.notes] if x)
        lines.append(
            f"| {esc(phase.name)} | {phase.status} | {esc(phase.operator or '')} | "
            f"{phase.started_at.isoformat() if phase.started_at else ''} | "
            f"{phase.completed_at.isoformat() if phase.completed_at else ''} | "
            f"{esc(detail)} |"
        )

    lines += [
        "",
        "## Incidents",
        "",
        "| ID | Severity | Status | Owner | Summary |",
        "| --- | --- | --- | --- | --- |",
    ]
    if launch.incidents:
        for incident in launch.incidents:
            lines.append(
                f"| {incident.id} | {incident.severity} | {incident.status} | "
                f"{esc(incident.owner or '')} | {esc(incident.summary)} |"
            )
    else:
        lines.append("| — | — | — | — | No launch incidents recorded |")

    lines += ["", "## Launch gate", ""]
    if gate.passed:
        lines.append("**PASS — all required launch phases passed and outcome is SUCCEEDED.**")
    else:
        lines.append("**FAIL — launch record is not a successful completed launch.**")
        lines.append("")
        for reason in gate.reasons:
            lines.append(f"- {reason}")

    lines += [
        "",
        "## Final notes",
        "",
        launch.final_notes or "No final notes recorded.",
        "",
    ]

    Path(args.output).write_text("\n".join(lines), encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
from datetime import datetime, timezone

from smartedu_stabilization import (
    StabilizationIssue,
    load_run,
    save_run,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run")
    parser.add_argument("issue_id")
    parser.add_argument(
        "--severity",
        required=True,
        choices=["SEV1", "SEV2", "SEV3", "SEV4"],
    )
    parser.add_argument("--title", required=True)
    parser.add_argument(
        "--status",
        default="OPEN",
        choices=["OPEN", "MITIGATING", "MONITORING", "CLOSED", "DEFERRED"],
    )
    parser.add_argument("--owner", required=True)
    parser.add_argument("--linked-incident-id")
    parser.add_argument("--linked-release-tag")
    parser.add_argument("--mitigation", default="")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    run = load_run(args.run)
    prior = next(
        (item for item in run.issues if item.id == args.issue_id),
        None,
    )
    now = datetime.now(timezone.utc)
    issue = StabilizationIssue(
        id=args.issue_id,
        severity=args.severity,
        title=args.title,
        status=args.status,
        owner=args.owner,
        opened_at=prior.opened_at if prior else now,
        closed_at=now if args.status == "CLOSED" else None,
        linked_incident_id=args.linked_incident_id,
        linked_release_tag=args.linked_release_tag,
        mitigation=args.mitigation,
        notes=args.notes,
    )

    run.issues = [item for item in run.issues if item.id != args.issue_id]
    run.issues.append(issue)
    run.issues.sort(key=lambda item: item.id)
    save_run(run, args.run)
    print(f"{args.issue_id}={args.status}/{args.severity}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

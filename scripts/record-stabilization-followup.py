from __future__ import annotations

import argparse
from datetime import datetime

from smartedu_stabilization import FollowUp, load_run, save_run


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run")
    parser.add_argument("followup_id")
    parser.add_argument("--title", required=True)
    parser.add_argument("--owner", required=True)
    parser.add_argument(
        "--severity",
        required=True,
        choices=["HIGH", "MEDIUM", "LOW"],
    )
    parser.add_argument(
        "--status",
        default="OPEN",
        choices=["OPEN", "IN_PROGRESS", "CLOSED"],
    )
    parser.add_argument("--target-date")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    followup = FollowUp(
        id=args.followup_id,
        title=args.title,
        owner=args.owner,
        severity=args.severity,
        status=args.status,
        target_date=(
            datetime.fromisoformat(args.target_date)
            if args.target_date
            else None
        ),
        notes=args.notes,
    )

    run = load_run(args.run)
    run.followups = [
        item for item in run.followups if item.id != args.followup_id
    ]
    run.followups.append(followup)
    run.followups.sort(key=lambda item: item.id)
    save_run(run, args.run)
    print(f"{args.followup_id}={args.status}/{args.severity}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

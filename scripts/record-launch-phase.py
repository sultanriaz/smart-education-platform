from __future__ import annotations

import argparse
from datetime import datetime, timezone

from smartedu_launch import PhaseRecord, load_launch, save_launch


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record")
    parser.add_argument("phase")
    parser.add_argument(
        "--status",
        required=True,
        choices=["NOT_STARTED", "IN_PROGRESS", "PASS", "FAIL", "ABORTED"],
    )
    parser.add_argument("--operator")
    parser.add_argument("--notes", default="")
    parser.add_argument("--evidence", action="append", default=[])
    args = parser.parse_args()

    launch = load_launch(args.record)
    existing = next(
        (item for item in launch.phases if item.name == args.phase),
        None,
    )
    now = datetime.now(timezone.utc)

    started_at = existing.started_at if existing else None
    if args.status == "IN_PROGRESS" and started_at is None:
        started_at = now
    if args.status in {"PASS", "FAIL", "ABORTED"} and started_at is None:
        started_at = now

    completed_at = (
        now if args.status in {"PASS", "FAIL", "ABORTED"} else None
    )

    phase = PhaseRecord(
        name=args.phase,
        status=args.status,
        started_at=started_at,
        completed_at=completed_at,
        operator=args.operator,
        notes=args.notes,
        evidence_paths=args.evidence,
    )
    launch.phases = [item for item in launch.phases if item.name != args.phase]
    launch.phases.append(phase)
    launch.phases.sort(key=lambda item: item.name)
    save_launch(launch, args.record)
    print(f"{args.phase}={args.status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

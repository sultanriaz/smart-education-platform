from __future__ import annotations

import argparse
from datetime import datetime, timezone

from smartedu_launch import LaunchIncident, load_launch, save_launch


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record")
    parser.add_argument("incident_id")
    parser.add_argument(
        "--severity",
        required=True,
        choices=["SEV1", "SEV2", "SEV3", "SEV4"],
    )
    parser.add_argument("--summary", required=True)
    parser.add_argument(
        "--status",
        default="OPEN",
        choices=["OPEN", "MITIGATED", "CLOSED"],
    )
    parser.add_argument("--owner")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    launch = load_launch(args.record)
    prior = next(
        (item for item in launch.incidents if item.id == args.incident_id),
        None,
    )
    incident = LaunchIncident(
        id=args.incident_id,
        severity=args.severity,
        summary=args.summary,
        opened_at=prior.opened_at if prior else datetime.now(timezone.utc),
        status=args.status,
        owner=args.owner,
        notes=args.notes,
    )
    launch.incidents = [
        item for item in launch.incidents if item.id != args.incident_id
    ]
    launch.incidents.append(incident)
    launch.incidents.sort(key=lambda item: item.id)
    save_launch(launch, args.record)
    print(f"{args.incident_id}={args.status}/{args.severity}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

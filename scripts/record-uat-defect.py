from __future__ import annotations

import argparse

from smartedu_uat import UATDefect, load_run, save_run, scenario_map


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run")
    parser.add_argument("defect_id")
    parser.add_argument("--scenario-id")
    parser.add_argument(
        "--severity",
        required=True,
        choices=["BLOCKER", "CRITICAL", "MAJOR", "MINOR", "COSMETIC"],
    )
    parser.add_argument("--title", required=True)
    parser.add_argument(
        "--status",
        default="OPEN",
        choices=["OPEN", "IN_PROGRESS", "FIXED", "RETEST", "CLOSED", "DEFERRED"],
    )
    parser.add_argument("--owner")
    parser.add_argument("--notes", default="")
    parser.add_argument("--workaround")
    parser.add_argument("--scenarios", default="config/uat/scenarios")
    args = parser.parse_args()

    if args.scenario_id:
        catalog = scenario_map(args.scenarios)
        if args.scenario_id not in catalog:
            raise SystemExit(f"unknown UAT scenario: {args.scenario_id}")

    run = load_run(args.run)
    defect = UATDefect(
        id=args.defect_id,
        scenario_id=args.scenario_id,
        severity=args.severity,
        title=args.title,
        status=args.status,
        owner=args.owner,
        notes=args.notes,
        workaround=args.workaround,
    )
    run.defects = [item for item in run.defects if item.id != args.defect_id]
    run.defects.append(defect)
    run.defects.sort(key=lambda item: item.id)
    save_run(run, args.run)
    print(f"{args.defect_id}={args.status}/{args.severity}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

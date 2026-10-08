from __future__ import annotations

import argparse
from datetime import datetime, timezone

from smartedu_uat import (
    ScenarioResult,
    load_run,
    save_run,
    scenario_map,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run")
    parser.add_argument("scenario_id")
    parser.add_argument(
        "--status",
        required=True,
        choices=["NOT_RUN", "PASS", "FAIL", "BLOCKED", "WAIVED"],
    )
    parser.add_argument("--executed-by", required=True)
    parser.add_argument("--notes", default="")
    parser.add_argument("--evidence", action="append", default=[])
    parser.add_argument("--defect", action="append", default=[])
    parser.add_argument("--waiver-id")
    parser.add_argument("--scenarios", default="config/uat/scenarios")
    args = parser.parse_args()

    catalog = scenario_map(args.scenarios)
    if args.scenario_id not in catalog:
        raise SystemExit(f"unknown UAT scenario: {args.scenario_id}")

    run = load_run(args.run)
    result = ScenarioResult(
        scenario_id=args.scenario_id,
        status=args.status,
        executed_by=args.executed_by,
        executed_at=datetime.now(timezone.utc),
        notes=args.notes,
        evidence_paths=args.evidence,
        defect_ids=args.defect,
        waiver_id=args.waiver_id,
    )

    run.results = [
        item
        for item in run.results
        if item.scenario_id != args.scenario_id
    ]
    run.results.append(result)
    run.results.sort(key=lambda item: item.scenario_id)
    save_run(run, args.run)
    print(f"{args.scenario_id}={args.status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

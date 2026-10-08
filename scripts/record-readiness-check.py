from __future__ import annotations

import argparse
from datetime import datetime, timezone

from smartedu_readiness import CheckResult, check_map, load_run, save_run


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run")
    parser.add_argument("check_id")
    parser.add_argument(
        "--status",
        required=True,
        choices=["NOT_RUN", "PASS", "FAIL", "BLOCKED", "WAIVED"],
    )
    parser.add_argument("--verified-by", required=True)
    parser.add_argument("--notes", default="")
    parser.add_argument("--evidence", action="append", default=[])
    parser.add_argument("--waiver-id")
    parser.add_argument("--checks", default="config/readiness/checks.yaml")
    args = parser.parse_args()

    catalog = check_map(args.checks)
    if args.check_id not in catalog:
        raise SystemExit(f"unknown readiness check: {args.check_id}")

    result = CheckResult(
        check_id=args.check_id,
        status=args.status,
        verified_by=args.verified_by,
        verified_at=datetime.now(timezone.utc),
        notes=args.notes,
        evidence_paths=args.evidence,
        waiver_id=args.waiver_id,
    )

    run = load_run(args.run)
    run.checks = [item for item in run.checks if item.check_id != args.check_id]
    run.checks.append(result)
    run.checks.sort(key=lambda item: item.check_id)
    save_run(run, args.run)
    print(f"{args.check_id}={args.status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

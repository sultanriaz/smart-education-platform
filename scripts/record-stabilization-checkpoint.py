from __future__ import annotations

import argparse
from datetime import datetime, timezone

from smartedu_stabilization import (
    CheckpointResult,
    checkpoint_map,
    load_run,
    save_run,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run")
    parser.add_argument("checkpoint_id")
    parser.add_argument(
        "--status",
        required=True,
        choices=["NOT_RUN", "PASS", "WARN", "FAIL", "BLOCKED"],
    )
    parser.add_argument("--observed-by", required=True)
    parser.add_argument("--notes", default="")
    parser.add_argument("--evidence", action="append", default=[])
    parser.add_argument(
        "--catalog",
        default="config/stabilization/checkpoints.yaml",
    )
    args = parser.parse_args()

    catalog = checkpoint_map(args.catalog)
    if args.checkpoint_id not in catalog:
        raise SystemExit(f"unknown checkpoint: {args.checkpoint_id}")

    result = CheckpointResult(
        checkpoint_id=args.checkpoint_id,
        status=args.status,
        observed_by=args.observed_by,
        observed_at=datetime.now(timezone.utc),
        notes=args.notes,
        evidence_paths=args.evidence,
    )

    run = load_run(args.run)
    run.checkpoints = [
        item
        for item in run.checkpoints
        if item.checkpoint_id != args.checkpoint_id
    ]
    run.checkpoints.append(result)
    run.checkpoints.sort(key=lambda item: item.checkpoint_id)
    save_run(run, args.run)
    print(f"{args.checkpoint_id}={args.status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

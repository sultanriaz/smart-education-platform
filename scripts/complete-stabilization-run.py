from __future__ import annotations

import argparse
from datetime import datetime, timezone

from smartedu_stabilization import load_run, save_run


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run")
    parser.add_argument(
        "--disposition",
        required=True,
        choices=["STABLE", "STABLE_WITH_FOLLOWUPS", "UNSTABLE"],
    )
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    run = load_run(args.run)
    run.completed_at = datetime.now(timezone.utc)
    run.disposition = args.disposition
    run.final_notes = args.notes
    save_run(run, args.run)
    print(f"disposition={args.disposition}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

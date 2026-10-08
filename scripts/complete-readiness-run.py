from __future__ import annotations

import argparse
from datetime import datetime, timezone

from smartedu_readiness import load_run, save_run


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run")
    parser.add_argument(
        "--decision",
        required=True,
        choices=["GO", "GO_WITH_CONDITIONS", "NO_GO"],
    )
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    run = load_run(args.run)
    run.completed_at = datetime.now(timezone.utc)
    run.final_decision = args.decision
    run.decision_notes = args.notes
    save_run(run, args.run)
    print(f"decision={args.decision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

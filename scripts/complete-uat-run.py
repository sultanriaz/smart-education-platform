from __future__ import annotations

import argparse
from datetime import datetime, timezone

from smartedu_uat import load_run, save_run


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run")
    args = parser.parse_args()

    run = load_run(args.run)
    run.completed_at = datetime.now(timezone.utc)
    save_run(run, args.run)
    print(f"completed_at={run.completed_at.isoformat()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

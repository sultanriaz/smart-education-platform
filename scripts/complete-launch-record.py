from __future__ import annotations

import argparse
from datetime import datetime, timezone

from smartedu_launch import load_launch, save_launch


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record")
    parser.add_argument(
        "--outcome",
        required=True,
        choices=["SUCCEEDED", "ROLLED_BACK", "ABORTED", "FAILED"],
    )
    parser.add_argument("--backup-reference")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    launch = load_launch(args.record)
    launch.completed_at = datetime.now(timezone.utc)
    launch.outcome = args.outcome
    launch.final_notes = args.notes
    if args.backup_reference:
        launch.backup_reference = args.backup_reference
    save_launch(launch, args.record)
    print(f"outcome={args.outcome}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

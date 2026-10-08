from __future__ import annotations

import argparse

from smartedu_launch import load_launch, save_launch


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record")
    parser.add_argument("backup_reference")
    args = parser.parse_args()

    reference = args.backup_reference.strip()
    if not reference:
        raise SystemExit("backup reference cannot be empty")

    launch = load_launch(args.record)
    launch.backup_reference = reference
    save_launch(launch, args.record)
    print(f"backup_reference={reference}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("profile")
    parser.add_argument(
        "--config",
        default="tests/performance/config/load-profiles.yaml",
    )
    parser.add_argument(
        "--field",
        choices=["users", "spawn_rate", "duration_seconds"],
        required=True,
    )
    args = parser.parse_args()

    payload = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    for profile in payload["profiles"]:
        if profile["name"] == args.profile:
            print(profile[args.field])
            return
    raise SystemExit(f"Unknown profile: {args.profile}")


if __name__ == "__main__":
    main()

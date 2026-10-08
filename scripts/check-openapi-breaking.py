from __future__ import annotations

import argparse
import json
from pathlib import Path

from smartedu_testkit import breaking_changes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline")
    parser.add_argument("candidate")
    args = parser.parse_args()

    baseline = Path(args.baseline)
    candidate = Path(args.candidate)

    failures = []
    for old_path in sorted(baseline.glob("*.openapi.json")):
        new_path = candidate / old_path.name
        if not new_path.exists():
            failures.append(f"{old_path.stem}: candidate snapshot missing")
            continue

        old = json.loads(old_path.read_text(encoding="utf-8"))
        new = json.loads(new_path.read_text(encoding="utf-8"))
        for change in breaking_changes(old, new):
            failures.append(f"{old_path.stem}: {change.message}")

    if failures:
        print("Potential breaking OpenAPI changes:")
        for item in failures:
            print(" - " + item)
        return 1

    print("No path/operation/response removals detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

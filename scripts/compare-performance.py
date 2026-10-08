from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path: str) -> dict[str, dict]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return {
        row["endpoint"]: row
        for row in payload.get("evaluations", [])
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline")
    parser.add_argument("candidate")
    parser.add_argument("--max-p95-regression", type=float, default=0.20)
    parser.add_argument("--max-rps-drop", type=float, default=0.20)
    args = parser.parse_args()

    baseline = load(args.baseline)
    candidate = load(args.candidate)
    failures: list[str] = []

    for endpoint, before in baseline.items():
        after = candidate.get(endpoint)
        if after is None:
            failures.append(f"{endpoint}: missing from candidate")
            continue

        if before["p95_ms"] > 0:
            ratio = after["p95_ms"] / before["p95_ms"] - 1
            if ratio > args.max_p95_regression:
                failures.append(
                    f"{endpoint}: p95 regressed {ratio:.1%} "
                    f"({before['p95_ms']} -> {after['p95_ms']} ms)"
                )

        if before["rps"] > 0:
            drop = 1 - after["rps"] / before["rps"]
            if drop > args.max_rps_drop:
                failures.append(
                    f"{endpoint}: rps dropped {drop:.1%} "
                    f"({before['rps']} -> {after['rps']})"
                )

        if after["error_rate"] > max(0.01, before["error_rate"]):
            failures.append(
                f"{endpoint}: error rate increased "
                f"{before['error_rate']:.2%} -> {after['error_rate']:.2%}"
            )

    if failures:
        print("Performance regression detected:")
        for item in failures:
            print(" - " + item)
        return 1

    print("No configured performance regression detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

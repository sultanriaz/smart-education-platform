from __future__ import annotations

import argparse

from smartedu_launch import evaluate_launch, load_launch


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record")
    args = parser.parse_args()

    gate = evaluate_launch(load_launch(args.record))
    if gate.passed:
        print("PASS production launch gate")
        return 0

    print("FAIL production launch gate")
    for reason in gate.reasons:
        print(" - " + reason)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

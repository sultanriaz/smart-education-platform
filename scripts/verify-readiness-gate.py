from __future__ import annotations

import argparse

from smartedu_readiness import (
    evaluate_readiness,
    load_checks,
    load_policy,
    load_run,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run")
    parser.add_argument("--checks", default="config/readiness/checks.yaml")
    parser.add_argument("--policy", default="config/readiness/policy.yaml")
    args = parser.parse_args()

    gate = evaluate_readiness(
        checks=load_checks(args.checks),
        run=load_run(args.run),
        policy=load_policy(args.policy),
    )

    print(f"mandatory={gate.mandatory_passed}/{gate.mandatory_total}")
    if gate.passed:
        print("PASS production-readiness gate")
        return 0

    print("FAIL production-readiness gate")
    for reason in gate.reasons:
        print(" - " + reason)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

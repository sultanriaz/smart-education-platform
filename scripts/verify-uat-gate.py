from __future__ import annotations

import argparse

from smartedu_uat import (
    evaluate_gate,
    load_policy,
    load_run,
    load_scenarios,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run")
    parser.add_argument("--policy", default="config/uat/policy.yaml")
    parser.add_argument("--scenarios", default="config/uat/scenarios")
    args = parser.parse_args()

    result = evaluate_gate(
        scenarios=load_scenarios(args.scenarios),
        run=load_run(args.run),
        policy=load_policy(args.policy),
    )

    print(f"pass_rate_percent={result.pass_rate_percent:.2f}")
    if result.passed:
        print("PASS UAT promotion gate")
        return 0

    print("FAIL UAT promotion gate")
    for reason in result.reasons:
        print(" - " + reason)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

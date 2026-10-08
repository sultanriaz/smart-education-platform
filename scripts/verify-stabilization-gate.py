from __future__ import annotations

import argparse

from smartedu_stabilization import (
    evaluate_stabilization,
    load_checkpoints,
    load_policy,
    load_run,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run")
    parser.add_argument(
        "--checkpoints",
        default="config/stabilization/checkpoints.yaml",
    )
    parser.add_argument(
        "--policy",
        default="config/stabilization/policy.yaml",
    )
    args = parser.parse_args()

    gate = evaluate_stabilization(
        checkpoints=load_checkpoints(args.checkpoints),
        run=load_run(args.run),
        policy=load_policy(args.policy),
    )
    print(
        f"mandatory={gate.mandatory_passed}/{gate.mandatory_total}"
    )
    if gate.passed:
        print("PASS production stabilization gate")
        return 0

    print("FAIL production stabilization gate")
    for reason in gate.reasons:
        print(" - " + reason)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

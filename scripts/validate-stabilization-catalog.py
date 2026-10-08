from __future__ import annotations

import argparse
from collections import Counter

from smartedu_stabilization import load_checkpoints, load_policy


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--checkpoints",
        default="config/stabilization/checkpoints.yaml",
    )
    parser.add_argument(
        "--policy",
        default="config/stabilization/policy.yaml",
    )
    args = parser.parse_args()

    checkpoints = load_checkpoints(args.checkpoints)
    policy = load_policy(args.policy)
    failures: list[str] = []

    required_roles = set(policy.get("required_approval_roles", []))
    for checkpoint in checkpoints:
        if checkpoint.owner_role not in required_roles:
            failures.append(
                f"{checkpoint.id}: unknown owner role {checkpoint.owner_role}"
            )
        if not checkpoint.evidence_required:
            failures.append(f"{checkpoint.id}: no evidence requirement")
        if not checkpoint.source_refs:
            failures.append(f"{checkpoint.id}: no source reference")

    if failures:
        print("Stabilization catalog validation failed:")
        for failure in failures:
            print(" - " + failure)
        return 1

    categories = Counter(item.category for item in checkpoints)
    print(
        f"PASS checkpoints={len(checkpoints)} "
        f"mandatory={sum(item.mandatory for item in checkpoints)}"
    )
    print(
        "categories="
        + ",".join(
            f"{name}:{count}"
            for name, count in sorted(categories.items())
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

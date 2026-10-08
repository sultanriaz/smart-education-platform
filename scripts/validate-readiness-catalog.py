from __future__ import annotations

import argparse
from collections import Counter

from smartedu_readiness import load_checks, load_policy


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checks", default="config/readiness/checks.yaml")
    parser.add_argument("--policy", default="config/readiness/policy.yaml")
    args = parser.parse_args()

    checks = load_checks(args.checks)
    policy = load_policy(args.policy)
    failures: list[str] = []

    roles = set(policy.required_approval_roles)
    for check in checks:
        if check.owner_role not in roles:
            failures.append(
                f"{check.id}: owner role {check.owner_role} is not an approval role"
            )
        if not check.evidence_required:
            failures.append(f"{check.id}: no evidence requirement")
        if not check.source_refs:
            failures.append(f"{check.id}: no source reference")

    if not checks:
        failures.append("readiness catalog is empty")

    if failures:
        print("Readiness catalog validation failed:")
        for failure in failures:
            print(" - " + failure)
        return 1

    by_category = Counter(item.category for item in checks)
    print(f"PASS checks={len(checks)} mandatory={sum(x.mandatory for x in checks)}")
    print(
        "categories="
        + ",".join(f"{name}:{count}" for name, count in sorted(by_category.items()))
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from smartedu_uat import load_scenarios


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenarios", default="config/uat/scenarios")
    parser.add_argument("--requirements", default="config/uat/requirements.yaml")
    args = parser.parse_args()

    scenarios = load_scenarios(args.scenarios)
    requirement_payload = yaml.safe_load(
        Path(args.requirements).read_text(encoding="utf-8")
    )
    requirement_ids = {
        item["id"]
        for item in requirement_payload["requirements"]
    }

    failures: list[str] = []
    referenced: set[str] = set()

    for scenario in scenarios:
        for ref in scenario.requirement_refs:
            referenced.add(ref)
            if ref not in requirement_ids:
                failures.append(f"{scenario.id}: unknown requirement {ref}")

        if not scenario.steps:
            failures.append(f"{scenario.id}: no steps")
        if not scenario.expected_results:
            failures.append(f"{scenario.id}: no expected results")

    uncovered = sorted(requirement_ids - referenced)
    if uncovered:
        failures.append(f"requirements with no UAT coverage: {uncovered}")

    if failures:
        print("UAT catalog validation failed:")
        for failure in failures:
            print(" - " + failure)
        return 1

    by_role: dict[str, int] = {}
    by_priority: dict[str, int] = {}
    for scenario in scenarios:
        by_role[scenario.role] = by_role.get(scenario.role, 0) + 1
        by_priority[scenario.priority] = by_priority.get(scenario.priority, 0) + 1

    print(f"PASS scenarios={len(scenarios)} requirements={len(requirement_ids)}")
    print("roles=" + ",".join(f"{k}:{v}" for k, v in sorted(by_role.items())))
    print("priorities=" + ",".join(f"{k}:{v}" for k, v in sorted(by_priority.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

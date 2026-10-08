from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from smartedu_uat import load_scenarios


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--requirements", default="config/uat/requirements.yaml")
    parser.add_argument("--scenarios", default="config/uat/scenarios")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    requirements = yaml.safe_load(
        Path(args.requirements).read_text(encoding="utf-8")
    )["requirements"]
    scenarios = load_scenarios(args.scenarios)

    by_requirement: dict[str, list[str]] = {
        item["id"]: [] for item in requirements
    }
    for scenario in scenarios:
        for ref in scenario.requirement_refs:
            by_requirement.setdefault(ref, []).append(scenario.id)

    lines = [
        "# UAT Requirements Traceability",
        "",
        "This matrix uses project-level normalized requirement aliases. "
        "Where the final SRS has formal requirement IDs, Codex must map them "
        "without changing the supported requirement meaning.",
        "",
        "| Requirement | Domain | Acceptance statement | UAT scenarios | Source reference |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in requirements:
        scenario_ids = ", ".join(sorted(by_requirement.get(item["id"], []))) or "UNMAPPED"
        statement = item["statement"].replace("|", "\\|")
        source = item["source_reference"].replace("|", "\\|")
        lines.append(
            f"| {item['id']} | {item['domain']} | {statement} | "
            f"{scenario_ids} | {source} |"
        )

    Path(args.output).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

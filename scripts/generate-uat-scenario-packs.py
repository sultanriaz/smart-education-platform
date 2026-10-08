from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from smartedu_uat import load_scenarios


def render_scenario(scenario) -> str:
    lines = [
        f"## {scenario.id} — {scenario.title}",
        "",
        f"**Role:** {scenario.role}  ",
        f"**Domain:** {scenario.domain}  ",
        f"**Priority:** {scenario.priority}  ",
        f"**Execution:** {scenario.execution}  ",
        f"**Requirements:** {', '.join(scenario.requirement_refs)}",
        "",
    ]
    if scenario.preconditions:
        lines += ["### Preconditions", ""]
        lines += [f"- {item}" for item in scenario.preconditions]
        lines.append("")

    lines += ["### Steps", ""]
    lines += [f"{index}. {step}" for index, step in enumerate(scenario.steps, start=1)]
    lines.append("")

    lines += ["### Expected results", ""]
    lines += [f"- {item}" for item in scenario.expected_results]
    lines.append("")

    lines += ["### Evidence", ""]
    lines += [f"- {item}" for item in scenario.evidence]
    lines += [
        "",
        "**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED",
        "",
        "**Tester:** ____________________",
        "",
        "**Defect IDs / notes:** ____________________________________________",
        "",
        "---",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenarios", default="config/uat/scenarios")
    parser.add_argument("--output-dir", default="uat/scenario-packs")
    args = parser.parse_args()

    scenarios = load_scenarios(args.scenarios)
    grouped = defaultdict(list)
    for scenario in scenarios:
        grouped[scenario.role].append(scenario)

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)

    for role, items in sorted(grouped.items()):
        path = output / f"{role.lower()}-uat-pack.md"
        body = [
            f"# {role} UAT Scenario Pack",
            "",
            "Release tag: ____________________  ",
            "Commit SHA: ____________________  ",
            "Staging/UAT URL: ____________________  ",
            "Execution date: ____________________",
            "",
            "Use the structured CLI run record as the source of truth for final gate evaluation. "
            "This document is a human-friendly execution worksheet.",
            "",
        ]
        for scenario in sorted(items, key=lambda item: item.id):
            body.append(render_scenario(scenario))
        path.write_text("\n".join(body), encoding="utf-8")
        print(path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

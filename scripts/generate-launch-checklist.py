from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from smartedu_readiness import load_checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checks", default="config/readiness/checks.yaml")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    grouped = defaultdict(list)
    for check in load_checks(args.checks):
        grouped[check.category].append(check)

    lines = [
        "# Production Readiness Human Checklist",
        "",
        "Release tag: ____________________  ",
        "Commit SHA: ____________________  ",
        "Production URL: ____________________  ",
        "Review date: ____________________",
        "",
        "The structured readiness run is the machine-readable source of truth. "
        "This checklist is a human review worksheet.",
        "",
    ]
    for category in sorted(grouped):
        lines += [f"## {category}", ""]
        for check in sorted(grouped[category], key=lambda item: item.id):
            lines.append(
                f"- [ ] **{check.id}** — {check.title} "
                f"_(owner: {check.owner_role})_"
            )
        lines.append("")

    Path(args.output).write_text("\n".join(lines), encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

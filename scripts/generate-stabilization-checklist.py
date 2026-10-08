from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from smartedu_stabilization import load_checkpoints


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--checkpoints",
        default="config/stabilization/checkpoints.yaml",
    )
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    grouped = defaultdict(list)
    for checkpoint in load_checkpoints(args.checkpoints):
        grouped[checkpoint.category].append(checkpoint)

    lines = [
        "# Production Stabilization Human Checklist",
        "",
        "Release tag: ____________________  ",
        "Launch ID: ____________________  ",
        "Production URL: ____________________  ",
        "Closure review date: ____________________",
        "",
        "The structured stabilization run is the machine-readable source of truth.",
        "",
    ]

    for category in sorted(grouped):
        lines += [f"## {category}", ""]
        for checkpoint in sorted(
            grouped[category],
            key=lambda item: item.id,
        ):
            lines.append(
                f"- [ ] **{checkpoint.id}** — {checkpoint.title} "
                f"_(owner: {checkpoint.owner_role})_"
            )
        lines.append("")

    Path(args.output).write_text("\n".join(lines), encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

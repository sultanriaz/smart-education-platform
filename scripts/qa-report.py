from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path


def parse_junit(path: Path) -> dict:
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))

    result = {
        "tests": 0,
        "failures": 0,
        "errors": 0,
        "skipped": 0,
        "time": 0.0,
    }
    for suite in suites:
        for key in ["tests", "failures", "errors", "skipped"]:
            result[key] += int(suite.attrib.get(key, 0))
        result["time"] += float(suite.attrib.get("time", 0.0))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", nargs="?", default="test-results")
    parser.add_argument("--output", default="test-results/qa-summary.json")
    args = parser.parse_args()

    root = Path(args.results)
    files = sorted(root.rglob("*.xml"))
    summary = {
        "files": {},
        "totals": {
            "tests": 0,
            "failures": 0,
            "errors": 0,
            "skipped": 0,
            "time": 0.0,
        },
    }

    for path in files:
        parsed = parse_junit(path)
        summary["files"][str(path.relative_to(root))] = parsed
        for key, value in parsed.items():
            summary["totals"][key] += value

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    totals = summary["totals"]
    print(
        f"tests={totals['tests']} failures={totals['failures']} "
        f"errors={totals['errors']} skipped={totals['skipped']} "
        f"time={totals['time']:.2f}s"
    )
    print(f"summary={output}")

    return 1 if totals["failures"] or totals["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

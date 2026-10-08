from __future__ import annotations

import argparse
import fnmatch
import json
from pathlib import Path

import yaml

from smartedu_perf import MetricBudget, evaluate_budget, parse_locust_stats


def matching_budget(name: str, config: dict) -> MetricBudget:
    for item in config.get("budgets", []):
        if fnmatch.fnmatch(name, item["match"]):
            return MetricBudget(
                name=item["name"],
                p95_ms=item["p95_ms"],
                max_error_rate=item.get("max_error_rate", 0.01),
                min_rps=item.get("min_rps"),
            )

    defaults = config.get("defaults", {})
    return MetricBudget(
        name=f"default:{name}",
        p95_ms=int(defaults.get("p95_ms", 3000)),
        max_error_rate=float(defaults.get("max_error_rate", 0.01)),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("stats_csv")
    parser.add_argument(
        "--budgets",
        default="tests/performance/config/performance-budgets.yaml",
    )
    parser.add_argument(
        "--output",
        default="tests/performance/results/evaluation.json",
    )
    args = parser.parse_args()

    config = yaml.safe_load(Path(args.budgets).read_text(encoding="utf-8"))
    rows = parse_locust_stats(args.stats_csv)

    evaluations = []
    failed = False
    for row in rows:
        budget = matching_budget(row.name, config)
        evaluation = evaluate_budget(row, budget)
        failed = failed or not evaluation.passed
        evaluations.append(
            {
                "endpoint": row.name,
                "requests": row.requests,
                "failures": row.failures,
                "error_rate": row.error_rate,
                "p50_ms": row.p50_ms,
                "p95_ms": row.p95_ms,
                "p99_ms": row.p99_ms,
                "avg_ms": row.avg_ms,
                "rps": row.rps,
                "budget": budget.model_dump(),
                "passed": evaluation.passed,
                "reasons": evaluation.reasons,
            }
        )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "passed": not failed,
        "endpoint_count": len(evaluations),
        "evaluations": evaluations,
    }
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    for item in evaluations:
        status = "PASS" if item["passed"] else "FAIL"
        print(
            f"{status:4} {item['endpoint']:<32} "
            f"p95={item['p95_ms']:.0f}ms "
            f"err={item['error_rate']:.2%} "
            f"rps={item['rps']:.2f}"
        )
        for reason in item["reasons"]:
            print("     - " + reason)

    print(f"evaluation={output}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

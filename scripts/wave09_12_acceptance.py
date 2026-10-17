"""Evidence-only Wave 9 gate runner. No silent passes for unexecuted load/recovery checks.

Examples:
  python scripts/wave09_12_acceptance.py plan
  python scripts/wave09_12_acceptance.py evaluate --locust-csv-prefix artifacts/benchmarks/my-run --users 500 --seconds 900

The 'evaluate' command parses completed Locust _stats.csv; this script never initiates
an unapproved load test or production mutation. Use Locust separately on a disposable target.
"""
from __future__ import annotations
import argparse
import csv
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = (
    ("D18", "end_to_end_flows", "Executed E2E 18/18 + all integration checks; live evidence required"),
    ("D20", "normal_latency", "Measured at least 95% of end-user requests <=3000ms"),
    ("D21", "five_hundred_users", "At least 500 actual concurrent virtual users, >=900 seconds"),
    ("D24", "restore_drill", "Actual backup and successful restore under documented time budget"),
    ("D25", "uptime", "Observed >=99% on an explicitly defined period"),
    ("D31", "large_query", "PG EXPLAIN and latency at pre-approved dataset scale"),
    ("D32", "compatibility", "Browsers/devices and accessibility check on real devices"),
)


def evaluate_csv(prefix: Path, users: int, seconds: int):
    path = Path(str(prefix) + "_stats.csv")
    if not path.is_file():
        raise ValueError(f"Missing Locust statistics file: {path}")
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError("Empty Locust statistics")
    aggregated = next((r for r in rows if (r.get("Name") or "").strip().lower() == "aggregated"), None)
    if aggregated is None:
        raise ValueError("Locust statistics are missing an Aggregated row")
    req = int(aggregated.get("Request Count") or 0)
    failures = int(aggregated.get("Failure Count") or 0)
    p95_key = next((k for k in aggregated if "95%" in k), None)
    p95 = float(aggregated.get(p95_key) or 0) if p95_key else 0.0
    if req <= 0 or p95 <= 0:
        raise ValueError("Zero requests or missing p95 — benchmark cannot pass")
    # --users/--seconds are operator-declared; do not infer achieved concurrency
    # from them. Concurrency evidence requires an independent Locust timeseries.
    history = Path(str(prefix) + "_stats_history.csv")
    max_users = 0
    sustained_500_seconds = 0
    if history.is_file():
        with history.open(encoding="utf-8-sig", newline="") as f:
            hist = list(csv.DictReader(f))
        for row in hist:
            try:
                max_users = max(max_users, int(row.get("User Count") or 0))
            except (ValueError, TypeError):
                pass
        active = [int(row["Timestamp"]) for row in hist if str(row.get("Timestamp", "")).isdigit()
                  and str(row.get("User Count", "")).isdigit() and int(row["User Count"]) >= 500]
        # A point estimate cannot establish a 15-minute 500-user soak: require
        # consecutive time-series samples spanning the entire window.
        longest = 0
        current_start = previous = None
        for row in hist:
            try:
                timestamp, count = int(row["Timestamp"]), int(row["User Count"])
            except (TypeError, ValueError, KeyError):
                continue
            if count < 500:
                current_start = previous = None
            elif current_start is None or (previous is not None and timestamp - previous > 15):
                current_start = timestamp
                previous = timestamp
            else:
                previous = timestamp
                longest = max(longest, timestamp - current_start)
        sustained_500_seconds = longest
    actual_duration = 0
    if history.is_file() and len(hist) > 1:
        from datetime import datetime as dt
        timestamps = [int(row["Timestamp"]) for row in hist if str(row.get("Timestamp", "")).isdigit()]
        if timestamps:
            actual_duration = max(timestamps) - min(timestamps)
    error_rate = failures / req
    statuses = {
        "D20": "BLOCKED",  # HTTP p95 does not measure actual browser page-load percentile.
        "D21": "PASS" if sustained_500_seconds >= 900 and error_rate <= .01 else "BLOCKED",
    }
    return {"statuses": statuses, "requests": req, "failures": failures,
            "error_rate": error_rate, "p95_ms": p95, "http_latency_budget": "PASS" if p95 <= 3000 and error_rate <= .01 else "FAIL", "observed_max_users": max_users,
            "observed_duration_seconds": actual_duration,
            "observed_sustained_500_seconds": sustained_500_seconds,
            "reported_users": users, "reported_duration_seconds": seconds,
            "status_reason": "Only consecutive stats_history samples at >=500 concurrent users for >=900 seconds establish D21"}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=["plan", "evaluate"])
    p.add_argument("--locust-csv-prefix", type=Path)
    p.add_argument("--users", type=int, default=0)
    p.add_argument("--seconds", type=int, default=0)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    report = {"generated_at_utc": datetime.now(UTC).isoformat(),
              "source": "Waves 9-12 acceptance evaluator", "cases": []}
    evidence = None
    if args.action == "evaluate":
        if args.locust_csv_prefix is None:
            p.error("evaluate requires --locust-csv-prefix")
        try:
            evidence = evaluate_csv(args.locust_csv_prefix, args.users, args.seconds)
        except (ValueError, OSError) as exc:
            report["evaluation_error"] = str(exc)
    for finding, label, gate in CASES:
        status = evidence["statuses"].get(finding, "BLOCKED") if evidence else "BLOCKED"
        report["cases"].append({"finding": finding, "gate": label, "status": status,
                                "required_evidence": gate})
    if evidence:
        report["benchmark"] = evidence
    output = args.output or ROOT / "artifacts" / "wave09_12" / "acceptance.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"report": str(output), "result": {x["finding"]: x["status"] for x in report["cases"]}}, indent=2))
    print("Unexecuted Wave 9 gates remain BLOCKED, not PASS")
    return 2 if any(x["status"] == "BLOCKED" for x in report["cases"]) else (1 if any(x["status"] == "FAIL" for x in report["cases"]) else 0)

if __name__ == "__main__":
    raise SystemExit(main())

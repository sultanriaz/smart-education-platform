from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from smartedu_perf import ConnectionBudget, total_connection_budget


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="tests/performance/config/connection-budgets.yaml",
    )
    args = parser.parse_args()

    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    budgets = [
        ConnectionBudget(
            service=item["service"],
            replicas=int(item["replicas"]),
            pool_size=int(item["pool_size"]),
            max_overflow=int(item["max_overflow"]),
        )
        for item in config["services"]
    ]

    steady, burst = total_connection_budget(budgets)
    maximum = int(config["database_server_max_connections"])
    reserved = int(config["reserved_connections"])
    usable = maximum - reserved

    for item in budgets:
        print(
            f"{item.service:<24} replicas={item.replicas:<2} "
            f"steady={item.steady_connections:<3} "
            f"burst={item.burst_connections:<3}"
        )

    print(f"steady_total={steady}")
    print(f"burst_total={burst}")
    print(f"usable_connections={usable}")

    if burst > usable:
        print("FAIL: configured burst pools exceed usable PostgreSQL connections.")
        return 1

    utilization = burst / usable if usable else 1
    if utilization > 0.85:
        print(
            "WARN: burst pool budget uses more than 85% of usable connections; "
            "leave headroom for migrations, backup, and operational sessions."
        )
    else:
        print("PASS: connection budget leaves operational headroom.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

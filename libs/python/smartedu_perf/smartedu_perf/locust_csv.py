from __future__ import annotations

import csv
from pathlib import Path

from .models import EndpointResult


def _float(row: dict[str, str], *names: str) -> float:
    for name in names:
        if name in row and row[name] != "":
            return float(row[name])
    raise KeyError(names[0])


def _int(row: dict[str, str], *names: str) -> int:
    return int(_float(row, *names))


def parse_locust_stats(path: str | Path) -> list[EndpointResult]:
    results: list[EndpointResult] = []
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            name = row.get("Name", "").strip()
            if not name or name == "Aggregated":
                continue

            results.append(
                EndpointResult(
                    name=name,
                    requests=_int(row, "Request Count"),
                    failures=_int(row, "Failure Count"),
                    p50_ms=_float(row, "50%", "Median Response Time"),
                    p95_ms=_float(row, "95%"),
                    p99_ms=_float(row, "99%"),
                    avg_ms=_float(row, "Average Response Time"),
                    rps=_float(row, "Requests/s"),
                )
            )
    return results

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request


def get_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=5) as response:
        body = response.read()
        if response.status != 200:
            raise RuntimeError(f"{url} returned {response.status}")
        return json.loads(body)


def get_text(url: str) -> str:
    with urllib.request.urlopen(url, timeout=5) as response:
        body = response.read().decode(errors="replace")
        if response.status != 200:
            raise RuntimeError(f"{url} returned {response.status}")
        return body


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prometheus", default="http://localhost:9090")
    parser.add_argument("--grafana", default="http://localhost:3001")
    parser.add_argument("--loki", default="http://localhost:3100")
    parser.add_argument("--tempo", default="http://localhost:3200")
    parser.add_argument("--alertmanager", default="http://localhost:9093")
    parser.add_argument(
        "--require-services",
        action="store_true",
        help="Fail unless all ten FastAPI scrape targets are up.",
    )
    args = parser.parse_args()

    failures: list[str] = []

    checks = [
        ("prometheus", args.prometheus + "/-/ready", "text"),
        ("grafana", args.grafana + "/api/health", "json"),
        ("loki", args.loki + "/ready", "text"),
        ("tempo", args.tempo + "/ready", "text"),
        ("alertmanager", args.alertmanager + "/-/ready", "text"),
    ]

    for name, url, kind in checks:
        try:
            if kind == "json":
                get_json(url)
            else:
                get_text(url)
            print(f"PASS {name}")
        except Exception as exc:
            failures.append(f"{name}: {exc}")
            print(f"FAIL {name}: {exc}")

    try:
        targets = get_json(
            args.prometheus.rstrip("/")
            + "/api/v1/targets?state=active"
        )
        active = targets["data"]["activeTargets"]
        smartedu = [
            item
            for item in active
            if item.get("labels", {}).get("job") == "smartedu-services"
        ]
        up = [
            item
            for item in smartedu
            if item.get("health") == "up"
        ]
        print(f"service_targets_up={len(up)}/{len(smartedu)}")
        if args.require_services and (len(smartedu) != 10 or len(up) != 10):
            failures.append(
                f"expected 10/10 service scrape targets up, got "
                f"{len(up)}/{len(smartedu)}"
            )
    except Exception as exc:
        failures.append(f"prometheus targets: {exc}")

    if failures:
        print("\nObservability verification failures:")
        for failure in failures:
            print(" - " + failure)
        return 1

    print("\nObservability stack verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

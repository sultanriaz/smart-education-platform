from __future__ import annotations

import argparse
import ssl
import time
import urllib.request
from pathlib import Path

import yaml


def check(url: str, expected: int, timeout: int) -> tuple[bool, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "smartedu-production-smoke/1.0",
            "Accept": "application/json,text/html",
        },
    )
    try:
        with urllib.request.urlopen(
            request,
            timeout=timeout,
            context=ssl.create_default_context(),
        ) as response:
            body = response.read(256).decode(errors="replace")
            return response.status == expected, f"{response.status} {body[:100]}"
    except Exception as exc:
        return False, str(exc)


def wait(url: str, expected: int, timeout: int, overall: int) -> tuple[bool, str]:
    deadline = time.monotonic() + overall
    last = ""
    while time.monotonic() < deadline:
        ok, detail = check(url, expected, timeout)
        last = detail
        if ok:
            return True, detail
        time.sleep(3)
    return False, last


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--config", default="config/launch/smoke.yaml")
    parser.add_argument("--request-timeout", type=int, default=8)
    parser.add_argument("--overall-timeout", type=int, default=180)
    args = parser.parse_args()

    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    base = args.base_url.rstrip("/")
    failures = []

    for item in config["public_checks"]:
        path = "/" + item["path"].lstrip("/")
        url = base + path
        ok, detail = wait(
            url,
            int(item.get("expected_status", 200)),
            args.request_timeout,
            args.overall_timeout,
        )
        print(("PASS" if ok else "FAIL"), item["name"], detail)
        if not ok:
            failures.append(item["name"])

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

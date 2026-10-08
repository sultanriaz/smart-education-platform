from __future__ import annotations

import argparse
import ssl
import time
import urllib.request


def get(url: str) -> tuple[int, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "smartedu-staging-smoke/1.0",
            "Accept": "application/json,text/html",
        },
    )
    with urllib.request.urlopen(
        request,
        timeout=8,
        context=ssl.create_default_context(),
    ) as response:
        return response.status, response.read(512).decode(errors="replace")


def wait(url: str, timeout: int) -> tuple[bool, str]:
    deadline = time.monotonic() + timeout
    last = ""
    while time.monotonic() < deadline:
        try:
            status, body = get(url)
            last = f"{status} {body[:120]}"
            if status == 200:
                return True, last
        except Exception as exc:
            last = str(exc)
        time.sleep(2)
    return False, last


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument(
        "--gateway-health-path",
        default="/api/health",
        help=(
            "Public Gateway health/smoke path after Ingress routing. "
            "Reconcile this with the merged Gateway contract."
        ),
    )
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    gateway_path = "/" + args.gateway_health_path.lstrip("/")
    checks = [
        ("frontend", base + "/"),
        ("gateway-health", base + gateway_path),
    ]
    failures = []
    for name, url in checks:
        ok, detail = wait(url, args.timeout)
        print(("PASS" if ok else "FAIL"), name, detail)
        if not ok:
            failures.append(name)

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

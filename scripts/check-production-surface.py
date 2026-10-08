from __future__ import annotations

import argparse
import socket
import ssl
from datetime import datetime, timezone
from urllib.parse import urlparse
from urllib.request import Request, urlopen


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--minimum-cert-days", type=int, default=14)
    parser.add_argument("--timeout", type=int, default=8)
    parser.add_argument("--gateway-path", default="/api/health")
    args = parser.parse_args()

    parsed = urlparse(args.url)
    failures: list[str] = []
    if parsed.scheme != "https" or not parsed.hostname:
        raise SystemExit("production URL must be an HTTPS URL with hostname")

    host = parsed.hostname
    port = parsed.port or 443
    if host.endswith((".example.edu", ".example.org", ".example.com")):
        failures.append(f"placeholder hostname is not allowed: {host}")

    try:
        addresses = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
        print(f"dns_addresses={len(addresses)}")
    except Exception as exc:
        failures.append(f"DNS resolution failed: {exc}")

    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=args.timeout) as raw:
            with context.wrap_socket(raw, server_hostname=host) as tls:
                cert = tls.getpeercert()
                expires = datetime.strptime(
                    cert["notAfter"],
                    "%b %d %H:%M:%S %Y %Z",
                ).replace(tzinfo=timezone.utc)
                days = (expires - datetime.now(timezone.utc)).total_seconds() / 86400
                print(f"tls_days_remaining={days:.1f}")
                if days < args.minimum_cert_days:
                    failures.append(
                        f"TLS certificate expires in {days:.1f} days"
                    )
    except Exception as exc:
        failures.append(f"TLS validation failed: {exc}")

    base = args.url.rstrip("/")
    for label, url in (
        ("frontend", base + "/"),
        ("gateway", base + "/" + args.gateway_path.lstrip("/")),
    ):
        try:
            request = Request(
                url,
                headers={"User-Agent": "smartedu-production-readiness/1.0"},
            )
            with urlopen(request, timeout=args.timeout) as response:
                print(f"{label}_status={response.status}")
                if response.status != 200:
                    failures.append(f"{label} returned {response.status}")
        except Exception as exc:
            failures.append(f"{label} HTTPS check failed: {exc}")

    if failures:
        print("Production surface validation failed:")
        for failure in failures:
            print(" - " + failure)
        return 1

    print("PASS production DNS/TLS/public-surface checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

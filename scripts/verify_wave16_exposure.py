"""Negative edge exposure check: defaults to failure on any public 2xx reply."""
import argparse
import sys
import urllib.error
import urllib.parse
import urllib.request

TARGETS = ["/metrics", "/prometheus", "/alertmanager", "/tempo", "/loki", "/api/v1/platform/metrics", "/api/v1/reporting/metrics", "/api/v1/platform/internal/events"]


def verify(url: str):
    failed = []
    for path in TARGETS:
        try:
            with urllib.request.urlopen(urllib.parse.urljoin(url.rstrip("/") + "/", path.lstrip("/")), timeout=4) as response:
                code = response.status
        except urllib.error.HTTPError as exc:
            code = exc.code
        except urllib.error.URLError as exc:
            print(f"FAIL {path}: gateway cannot be reached: {exc}")
            failed.append(path)
            continue
        success = code in (403, 404)
        print(f"{'PASS' if success else 'FAIL'} {path}: HTTP {code}")
        if not success:
            failed.append(path)
    return not failed


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gateway", required=True, help="Public-facing API gateway base URL")
    args = parser.parse_args()
    sys.exit(0 if verify(args.gateway) else 1)

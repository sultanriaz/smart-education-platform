from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse


def load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def image_map(payload: dict) -> dict[str, str]:
    return {
        item["component"]: item["immutable_ref"]
        for item in payload.get("images", [])
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("release_manifest")
    parser.add_argument(
        "--staging-release-manifest",
        help="Manifest recorded as accepted/deployed by Sprint 24.",
    )
    parser.add_argument("--staging-url", required=True)
    args = parser.parse_args()

    release = load(args.release_manifest)
    failures: list[str] = []

    parsed = urlparse(args.staging_url)
    if parsed.scheme != "https":
        failures.append("UAT staging URL must use HTTPS")
    if not parsed.hostname:
        failures.append("UAT staging URL has no hostname")
    elif parsed.hostname.endswith((".example.edu", ".example.org", ".example.com")):
        failures.append(
            f"UAT staging URL still uses a placeholder hostname: {parsed.hostname}"
        )

    if len(release.get("commit_sha", "")) != 40:
        failures.append("release manifest must contain a full 40-character commit SHA")

    images = image_map(release)
    if len(images) != 12:
        failures.append(f"expected 12 release images, got {len(images)}")
    for component, ref in images.items():
        if "@sha256:" not in ref:
            failures.append(f"{component}: release image is not digest pinned")

    if args.staging_release_manifest:
        deployed = load(args.staging_release_manifest)
        if release.get("release_tag") != deployed.get("release_tag"):
            failures.append("candidate release tag differs from staged release tag")
        if release.get("commit_sha") != deployed.get("commit_sha"):
            failures.append("candidate commit differs from staged release commit")
        if image_map(release) != image_map(deployed):
            failures.append("candidate image digests differ from staged release images")

    if failures:
        print("UAT preflight failed:")
        for failure in failures:
            print(" - " + failure)
        return 1

    print(
        f"PASS release={release['release_tag']} "
        f"images={len(images)} staging_url={args.staging_url.rstrip('/')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

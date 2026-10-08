from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse


REQUIRED_LAUNCH_PHASES = {
    "preflight",
    "backup",
    "migrations",
    "application-rollout",
    "public-smoke",
    "role-smoke",
    "event-smoke",
    "observability",
}


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def image_map(payload: dict) -> dict[str, str]:
    return {
        item["component"]: item["immutable_ref"]
        for item in payload.get("images", [])
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("release_manifest")
    parser.add_argument("--launch-record", required=True)
    parser.add_argument("--production-url", required=True)
    args = parser.parse_args()

    release = load_json(args.release_manifest)
    launch = load_json(args.launch_record)
    failures: list[str] = []

    if launch.get("release_tag") != release.get("release_tag"):
        failures.append("launch release tag does not match release manifest")
    if launch.get("commit_sha") != release.get("commit_sha"):
        failures.append("launch commit SHA does not match release manifest")
    if launch.get("outcome") != "SUCCEEDED":
        failures.append(
            f"Sprint 27 launch outcome is not SUCCEEDED: {launch.get('outcome')}"
        )
    if launch.get("completed_at") is None:
        failures.append("Sprint 27 launch record is not completed")

    phase_map = {
        item.get("name"): item.get("status")
        for item in launch.get("phases", [])
    }
    missing_or_failed = sorted(
        name
        for name in REQUIRED_LAUNCH_PHASES
        if phase_map.get(name) != "PASS"
    )
    if missing_or_failed:
        failures.append(
            f"required launch phases not PASS: {missing_or_failed}"
        )

    open_sev1 = [
        item.get("id")
        for item in launch.get("incidents", [])
        if item.get("severity") == "SEV1"
        and item.get("status") != "CLOSED"
    ]
    if open_sev1:
        failures.append(f"open Sprint 27 SEV1 incidents: {open_sev1}")

    images = image_map(release)
    if len(images) != 12:
        failures.append(f"expected 12 release images, got {len(images)}")
    if any("@sha256:" not in ref for ref in images.values()):
        failures.append("one or more release images are not digest pinned")

    parsed = urlparse(args.production_url)
    if parsed.scheme != "https" or not parsed.hostname:
        failures.append("production URL must be HTTPS with hostname")
    elif parsed.hostname.endswith(
        (".example.edu", ".example.org", ".example.com")
    ):
        failures.append(
            f"production hostname remains a placeholder: {parsed.hostname}"
        )

    launch_url = launch.get("production_url", "").rstrip("/")
    if launch_url != args.production_url.rstrip("/"):
        failures.append(
            "stabilization production URL differs from launch record"
        )

    if failures:
        print("Stabilization preflight failed:")
        for failure in failures:
            print(" - " + failure)
        return 1

    print(
        f"PASS launch_id={launch.get('launch_id')} "
        f"release={release.get('release_tag')} images={len(images)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

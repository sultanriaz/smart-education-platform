from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

import yaml


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def image_map(payload: dict) -> dict[str, str]:
    return {
        item["component"]: item["immutable_ref"]
        for item in payload.get("images", [])
    }


def uat_gate_pass(payload: dict) -> bool:
    # Supports the structured Sprint 25 run JSON. The final Sprint 25 gate
    # remains authoritative; this preflight rejects obviously incomplete or
    # failing UAT records before readiness work begins.
    results = payload.get("results", [])
    signoffs = payload.get("signoffs", [])
    if payload.get("completed_at") is None:
        return False
    if len(results) < 40:
        return False
    if any(
        result.get("status") in {"NOT_RUN", "FAIL", "BLOCKED"}
        for result in results
    ):
        return False

    required_roles = {
        "StudentRepresentative",
        "TeacherRepresentative",
        "AdminRepresentative",
        "ProductOwner",
        "ProjectSupervisor",
    }
    approved_roles = {
        item.get("role")
        for item in signoffs
        if item.get("decision") in {"APPROVE", "APPROVE_WITH_CONDITIONS"}
    }
    if not required_roles <= approved_roles:
        return False
    if any(item.get("decision") == "REJECT" for item in signoffs):
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("release_manifest")
    parser.add_argument("--uat-run", required=True)
    parser.add_argument("--production-url", required=True)
    parser.add_argument("--staging-release-manifest")
    parser.add_argument(
        "--production-topology",
        default="config/deployment/production-topology.yaml",
    )
    args = parser.parse_args()

    failures: list[str] = []
    release = load_json(args.release_manifest)
    uat = load_json(args.uat_run)

    parsed = urlparse(args.production_url)
    if parsed.scheme != "https":
        failures.append("production URL must use HTTPS")
    if not parsed.hostname:
        failures.append("production URL is missing a hostname")
    elif parsed.hostname.endswith((".example.edu", ".example.org", ".example.com")):
        failures.append(f"production URL still uses placeholder host {parsed.hostname}")

    if len(release.get("commit_sha", "")) != 40:
        failures.append("release manifest must contain full 40-character commit SHA")

    images = image_map(release)
    if len(images) != 12:
        failures.append(f"expected 12 release images, got {len(images)}")
    for component, ref in images.items():
        if "@sha256:" not in ref:
            failures.append(f"{component}: image is not digest pinned")

    if uat.get("release_tag") != release.get("release_tag"):
        failures.append("UAT release tag does not match release manifest")
    if uat.get("commit_sha") != release.get("commit_sha"):
        failures.append("UAT commit SHA does not match release manifest")
    if not uat_gate_pass(uat):
        failures.append("UAT run is not complete/signable enough for readiness preflight")

    if args.staging_release_manifest:
        staged = load_json(args.staging_release_manifest)
        if image_map(staged) != images:
            failures.append("production candidate image digests differ from staged release")
        if staged.get("release_tag") != release.get("release_tag"):
            failures.append("production candidate tag differs from staged release")

    topology_path = Path(args.production_topology)
    if topology_path.exists():
        topology = yaml.safe_load(topology_path.read_text(encoding="utf-8"))
        host = topology.get("public_host", "")
        if host.endswith((".example.edu", ".example.org", ".example.com")):
            failures.append(
                f"production topology still uses placeholder public_host {host}"
            )

    if failures:
        print("Production-readiness preflight failed:")
        for failure in failures:
            print(" - " + failure)
        return 1

    print(
        f"PASS release={release['release_tag']} "
        f"images={len(images)} production_url={args.production_url.rstrip('/')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

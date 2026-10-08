from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

import yaml

from smartedu_launch import load_release


REQUIRED_APPROVAL_ROLES = {
    "TechnicalLead",
    "OperationsOwner",
    "SecurityOwner",
    "ProductOwner",
    "ProjectSupervisor",
}


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def image_map(payload: dict) -> dict[str, str]:
    return {
        item["component"]: item["immutable_ref"]
        for item in payload.get("images", [])
    }


def readiness_passed(payload: dict) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if payload.get("completed_at") is None:
        failures.append("readiness run is not completed")
    if payload.get("final_decision") not in {"GO", "GO_WITH_CONDITIONS"}:
        failures.append(
            f"readiness decision is {payload.get('final_decision')!r}"
        )

    results = payload.get("checks", [])
    not_pass = [
        item.get("check_id")
        for item in results
        if item.get("status") != "PASS"
    ]
    if not_pass:
        failures.append(f"readiness checks not PASS: {sorted(not_pass)}")

    approvals = payload.get("approvals", [])
    approved = {
        item.get("role")
        for item in approvals
        if item.get("decision") in {"APPROVE", "APPROVE_WITH_CONDITIONS"}
    }
    missing = sorted(REQUIRED_APPROVAL_ROLES - approved)
    if missing:
        failures.append(f"missing readiness approvals: {missing}")
    if any(item.get("decision") == "REJECT" for item in approvals):
        failures.append("readiness contains a REJECT approval")

    blocking = [
        risk.get("id")
        for risk in payload.get("risks", [])
        if risk.get("severity") in {"BLOCKER", "CRITICAL", "HIGH"}
        and risk.get("status") in {"OPEN", "MITIGATING"}
    ]
    if blocking:
        failures.append(f"blocking readiness risks remain: {blocking}")

    return not failures, failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("release_manifest")
    parser.add_argument("--readiness-run", required=True)
    parser.add_argument("--production-url", required=True)
    parser.add_argument("--accepted-release-manifest")
    parser.add_argument(
        "--production-topology",
        default="config/deployment/production-topology.yaml",
    )
    args = parser.parse_args()

    failures: list[str] = []
    release = load_release(args.release_manifest)
    readiness = load_json(args.readiness_run)

    if readiness.get("release_tag") != release.release_tag:
        failures.append("readiness release tag does not match release manifest")
    if readiness.get("commit_sha") != release.commit_sha:
        failures.append("readiness commit SHA does not match release manifest")

    ok, readiness_failures = readiness_passed(readiness)
    if not ok:
        failures.extend(readiness_failures)

    if len(release.images) != 12:
        failures.append(f"expected 12 release images, got {len(release.images)}")

    parsed = urlparse(args.production_url)
    if parsed.scheme != "https" or not parsed.hostname:
        failures.append("production URL must be HTTPS with a hostname")
    elif parsed.hostname.endswith((".example.edu", ".example.org", ".example.com")):
        failures.append(f"production hostname is still a placeholder: {parsed.hostname}")

    if args.accepted_release_manifest:
        accepted = load_json(args.accepted_release_manifest)
        candidate = load_json(args.release_manifest)
        if accepted.get("release_tag") != candidate.get("release_tag"):
            failures.append("accepted/candidate release tags differ")
        if accepted.get("commit_sha") != candidate.get("commit_sha"):
            failures.append("accepted/candidate commits differ")
        if image_map(accepted) != image_map(candidate):
            failures.append("accepted/candidate image digests differ")

    topology_path = Path(args.production_topology)
    if topology_path.exists():
        topology = yaml.safe_load(topology_path.read_text(encoding="utf-8"))
        host = topology.get("public_host", "")
        if host.endswith((".example.edu", ".example.org", ".example.com")):
            failures.append(f"production topology still uses placeholder host {host}")

    if failures:
        print("Production launch preflight failed:")
        for failure in failures:
            print(" - " + failure)
        return 1

    print(
        f"PASS release={release.release_tag} images={len(release.images)} "
        f"production_url={args.production_url.rstrip('/')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

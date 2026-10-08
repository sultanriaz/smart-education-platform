from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from smartedu_staging import load_release, load_topology


PLACEHOLDER_SUFFIXES = (
    ".example.edu",
    ".example.org",
    ".example.com",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--topology",
        default="config/staging/staging-topology.yaml",
    )
    parser.add_argument("--release-manifest")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    topology = load_topology(args.topology)
    failures: list[str] = []
    warnings: list[str] = []

    if topology.public_host.endswith(PLACEHOLDER_SUFFIXES):
        target = failures if args.strict else warnings
        target.append(
            f"staging public host still uses placeholder {topology.public_host}"
        )

    if len(topology.workload_overrides) != 12:
        failures.append(
            f"expected 12 staging workloads, got "
            f"{len(topology.workload_overrides)}"
        )

    if any(item.replicas < 2 for item in topology.workload_overrides):
        failures.append(
            "all staging workloads must have >=2 replicas for failure/rollout drills"
        )

    dependencies = yaml.safe_load(
        Path("config/staging/dependencies.yaml").read_text(encoding="utf-8")
    )["dependencies"]
    required = {item["name"] for item in dependencies if item["required"]}
    declared = set(topology.stateful_dependencies)
    if required != declared:
        failures.append(
            f"dependency mismatch missing={sorted(required-declared)} "
            f"extra={sorted(declared-required)}"
        )

    if args.release_manifest:
        release = load_release(args.release_manifest)
        images = {item.component for item in release.images}
        workloads = {item.component for item in topology.workload_overrides}
        if images != workloads:
            failures.append(
                f"release component mismatch missing={sorted(workloads-images)} "
                f"extra={sorted(images-workloads)}"
            )

    for warning in warnings:
        print("WARN " + warning)

    if failures:
        print("Staging preflight failed:")
        for failure in failures:
            print(" - " + failure)
        return 1

    print(
        f"PASS workloads={len(topology.workload_overrides)} "
        f"dependencies={len(required)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

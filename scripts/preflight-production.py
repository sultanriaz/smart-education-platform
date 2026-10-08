from __future__ import annotations

import argparse

from smartedu_deploy import load_release_manifest, load_topology


REQUIRED_BACKUP_KINDS = {
    "postgresql",
    "redis-durable",
    "rabbitmq",
    "object-storage",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--topology",
        default="config/deployment/production-topology.yaml",
    )
    parser.add_argument("--release-manifest")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    topology = load_topology(args.topology)
    failures: list[str] = []
    warnings: list[str] = []

    if topology.public_host.endswith("example.edu"):
        message = (
            "production public_host still uses the placeholder "
            f"{topology.public_host}"
        )
        (failures if args.strict else warnings).append(message)

    if len(topology.workloads) != 12:
        failures.append(f"expected 12 application workloads, got {len(topology.workloads)}")

    for dependency in topology.external_dependencies:
        if dependency.kind in REQUIRED_BACKUP_KINDS and not dependency.backup_required:
            failures.append(f"{dependency.name}: backup_required must be true")
        if dependency.kind != "email" and not dependency.private_network_only:
            failures.append(f"{dependency.name}: should be private-network only")
        if not dependency.highly_available:
            failures.append(f"{dependency.name}: production dependency is not HA")

    if args.release_manifest:
        release = load_release_manifest(args.release_manifest)
        images = {item.component for item in release.images}
        workloads = {item.component for item in topology.workloads}
        if workloads != images:
            failures.append(
                f"release/topology mismatch missing={sorted(workloads-images)} "
                f"extra={sorted(images-workloads)}"
            )

    for warning in warnings:
        print("WARN " + warning)

    if failures:
        print("Production preflight failed:")
        for failure in failures:
            print(" - " + failure)
        return 1

    print(
        f"PASS workloads={len(topology.workloads)} "
        f"dependencies={len(topology.external_dependencies)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

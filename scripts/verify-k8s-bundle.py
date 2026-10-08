from __future__ import annotations

import argparse
from pathlib import Path

import yaml


def docs(path: str):
    return [
        doc
        for doc in yaml.safe_load_all(Path(path).read_text(encoding="utf-8"))
        if isinstance(doc, dict)
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle")
    parser.add_argument("--expected-workloads", type=int, default=12)
    args = parser.parse_args()

    documents = docs(args.bundle)
    failures: list[str] = []

    deployments = [d for d in documents if d.get("kind") == "Deployment"]
    services = [d for d in documents if d.get("kind") == "Service"]
    hpas = [d for d in documents if d.get("kind") == "HorizontalPodAutoscaler"]
    pdbs = [d for d in documents if d.get("kind") == "PodDisruptionBudget"]
    ingresses = [d for d in documents if d.get("kind") == "Ingress"]

    for label, items in [
        ("deployments", deployments),
        ("services", services),
        ("hpas", hpas),
        ("pdbs", pdbs),
    ]:
        if len(items) != args.expected_workloads:
            failures.append(
                f"expected {args.expected_workloads} {label}, got {len(items)}"
            )

    if len(ingresses) != 1:
        failures.append(f"expected exactly one Ingress, got {len(ingresses)}")

    deployment_names = {d["metadata"]["name"] for d in deployments}
    service_names = {d["metadata"]["name"] for d in services}
    if deployment_names != service_names:
        failures.append("deployment/service name sets differ")

    for deployment in deployments:
        name = deployment["metadata"]["name"]
        pod_spec = deployment["spec"]["template"]["spec"]
        containers = pod_spec.get("containers", [])
        if len(containers) != 1:
            failures.append(f"{name}: expected one app container")
            continue

        container = containers[0]
        image = container.get("image", "")
        if "@sha256:" not in image:
            failures.append(f"{name}: image is not digest pinned: {image}")
        if ":bootstrap" in image or "REPLACE" in image:
            failures.append(f"{name}: placeholder image remains")

        pod_security = pod_spec.get("securityContext", {})
        if pod_security.get("runAsNonRoot") is not True:
            failures.append(f"{name}: runAsNonRoot is not true")
        if pod_security.get("seccompProfile", {}).get("type") != "RuntimeDefault":
            failures.append(f"{name}: seccomp RuntimeDefault missing")

        container_security = container.get("securityContext", {})
        if container_security.get("allowPrivilegeEscalation") is not False:
            failures.append(f"{name}: privilege escalation is not disabled")
        if container_security.get("readOnlyRootFilesystem") is not True:
            failures.append(f"{name}: root filesystem is not read-only")
        if "ALL" not in container_security.get("capabilities", {}).get("drop", []):
            failures.append(f"{name}: Linux capabilities are not dropped")

        if not container.get("resources", {}).get("requests"):
            failures.append(f"{name}: resource requests missing")
        if not container.get("resources", {}).get("limits"):
            failures.append(f"{name}: resource limits missing")
        if not container.get("readinessProbe"):
            failures.append(f"{name}: readiness probe missing")
        if not container.get("livenessProbe"):
            failures.append(f"{name}: liveness probe missing")

        if pod_spec.get("automountServiceAccountToken") is not False:
            failures.append(f"{name}: service-account token automount enabled")

    for service in services:
        if service.get("spec", {}).get("type") != "ClusterIP":
            failures.append(
                f"{service['metadata']['name']}: public Service type is forbidden"
            )

    if ingresses:
        ingress = ingresses[0]
        paths = ingress["spec"]["rules"][0]["http"]["paths"]
        backends = {
            path["backend"]["service"]["name"]
            for path in paths
        }
        if backends != {"frontend", "api-gateway"}:
            failures.append(
                f"Ingress may expose only frontend/api-gateway, got {sorted(backends)}"
            )
        if not ingress["spec"].get("tls"):
            failures.append("Ingress TLS is missing")

    if failures:
        print("Deployment bundle verification failed:")
        for failure in failures:
            print(" - " + failure)
        return 1

    print(
        f"PASS documents={len(documents)} "
        f"deployments={len(deployments)} "
        f"services={len(services)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

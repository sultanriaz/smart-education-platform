from __future__ import annotations

import argparse
from pathlib import Path

import yaml


def load_documents(path: str):
    return [
        doc
        for doc in yaml.safe_load_all(Path(path).read_text(encoding="utf-8"))
        if isinstance(doc, dict)
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle")
    parser.add_argument("--expected-deployments", type=int, default=12)
    args = parser.parse_args()

    docs = load_documents(args.bundle)
    failures: list[str] = []

    deployments = [d for d in docs if d.get("kind") == "Deployment"]
    services = [d for d in docs if d.get("kind") == "Service"]
    hpas = [d for d in docs if d.get("kind") == "HorizontalPodAutoscaler"]
    pdbs = [d for d in docs if d.get("kind") == "PodDisruptionBudget"]
    ingresses = [d for d in docs if d.get("kind") == "Ingress"]

    for label, items in (
        ("Deployments", deployments),
        ("Services", services),
        ("HPAs", hpas),
        ("PDBs", pdbs),
    ):
        if len(items) != args.expected_deployments:
            failures.append(
                f"{label}: expected {args.expected_deployments}, got {len(items)}"
            )

    if len(ingresses) != 1:
        failures.append(f"Ingress: expected 1, got {len(ingresses)}")

    for deployment in deployments:
        name = deployment["metadata"]["name"]
        spec = deployment["spec"]
        if spec.get("replicas", 0) < 2:
            failures.append(f"{name}: replicas below 2")
        strategy = spec.get("strategy", {})
        rolling = strategy.get("rollingUpdate", {})
        if strategy.get("type") != "RollingUpdate":
            failures.append(f"{name}: strategy is not RollingUpdate")
        if str(rolling.get("maxUnavailable")) != "0":
            failures.append(f"{name}: maxUnavailable is not 0")

        pod = spec["template"]["spec"]
        containers = pod.get("containers", [])
        if len(containers) != 1:
            failures.append(f"{name}: expected one application container")
            continue
        container = containers[0]
        image = container.get("image", "")
        if "@sha256:" not in image:
            failures.append(f"{name}: image is not digest pinned")
        if ":bootstrap" in image or ":latest" in image:
            failures.append(f"{name}: mutable/bootstrap image remains")
        if not container.get("readinessProbe"):
            failures.append(f"{name}: readinessProbe missing")
        if not container.get("livenessProbe"):
            failures.append(f"{name}: livenessProbe missing")
        if not container.get("resources", {}).get("requests"):
            failures.append(f"{name}: resource requests missing")
        if not container.get("resources", {}).get("limits"):
            failures.append(f"{name}: resource limits missing")

        pod_security = pod.get("securityContext", {})
        security = container.get("securityContext", {})
        if pod_security.get("runAsNonRoot") is not True:
            failures.append(f"{name}: runAsNonRoot not true")
        if pod_security.get("seccompProfile", {}).get("type") != "RuntimeDefault":
            failures.append(f"{name}: seccomp RuntimeDefault missing")
        if security.get("allowPrivilegeEscalation") is not False:
            failures.append(f"{name}: privilege escalation not disabled")
        if security.get("readOnlyRootFilesystem") is not True:
            failures.append(f"{name}: read-only root filesystem missing")
        if "ALL" not in security.get("capabilities", {}).get("drop", []):
            failures.append(f"{name}: capabilities are not fully dropped")
        if pod.get("automountServiceAccountToken") is not False:
            failures.append(f"{name}: service-account token automount enabled")

    for service in services:
        if service.get("spec", {}).get("type") != "ClusterIP":
            failures.append(
                f"{service['metadata']['name']}: public Service type is forbidden"
            )

    if ingresses:
        ingress = ingresses[0]
        if not ingress.get("spec", {}).get("tls"):
            failures.append("Ingress TLS missing")
        paths = ingress["spec"]["rules"][0]["http"]["paths"]
        public_targets = {
            path["backend"]["service"]["name"]
            for path in paths
        }
        if public_targets != {"frontend", "api-gateway"}:
            failures.append(
                f"unexpected public targets: {sorted(public_targets)}"
            )
        host = ingress["spec"]["rules"][0].get("host", "")
        if host.endswith((".example.edu", ".example.org", ".example.com")):
            failures.append(f"placeholder Ingress host remains: {host}")

    text = Path(args.bundle).read_text(encoding="utf-8").casefold()
    for token in (
        "replace_with_secret_manager_value",
        "replace_or_remove_after",
    ):
        if token in text:
            failures.append(f"secret/config placeholder remains: {token}")

    if failures:
        print("Production bundle verification failed:")
        for failure in failures:
            print(" - " + failure)
        return 1

    print(
        f"PASS documents={len(docs)} deployments={len(deployments)} "
        f"services={len(services)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

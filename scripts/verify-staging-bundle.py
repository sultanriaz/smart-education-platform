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
    parser.add_argument("--namespace", default="smartedu-staging")
    parser.add_argument("--expected-deployments", type=int, default=12)
    args = parser.parse_args()

    docs = load_documents(args.bundle)
    failures: list[str] = []

    deployments = [doc for doc in docs if doc.get("kind") == "Deployment"]
    services = [doc for doc in docs if doc.get("kind") == "Service"]
    hpas = [doc for doc in docs if doc.get("kind") == "HorizontalPodAutoscaler"]
    pdbs = [doc for doc in docs if doc.get("kind") == "PodDisruptionBudget"]
    jobs = [doc for doc in docs if doc.get("kind") == "Job"]
    ingress = [doc for doc in docs if doc.get("kind") == "Ingress"]

    for label, items in [
        ("Deployment", deployments),
        ("Service", services),
        ("HPA", hpas),
        ("PDB", pdbs),
    ]:
        if len(items) != args.expected_deployments:
            failures.append(
                f"{label}: expected {args.expected_deployments}, got {len(items)}"
            )

    if len(ingress) != 1:
        failures.append(f"Ingress: expected 1, got {len(ingress)}")

    for doc in docs:
        metadata = doc.get("metadata", {})
        if doc.get("kind") == "Namespace":
            if metadata.get("name") != args.namespace:
                failures.append(
                    f"Namespace is {metadata.get('name')}, expected {args.namespace}"
                )
            continue
        if metadata.get("namespace") and metadata.get("namespace") != args.namespace:
            failures.append(
                f"{doc.get('kind')}/{metadata.get('name')}: wrong namespace "
                f"{metadata.get('namespace')}"
            )

    for deployment in deployments:
        name = deployment["metadata"]["name"]
        containers = deployment["spec"]["template"]["spec"]["containers"]
        if len(containers) != 1:
            failures.append(f"{name}: expected one application container")
            continue
        image = containers[0].get("image", "")
        if "@sha256:" not in image:
            failures.append(f"{name}: image is not digest pinned")
        if ":bootstrap" in image:
            failures.append(f"{name}: bootstrap image remains")
        if deployment["spec"].get("replicas", 0) < 2:
            failures.append(f"{name}: staging replica count below 2")

    for service in services:
        if service["spec"].get("type") != "ClusterIP":
            failures.append(
                f"{service['metadata']['name']}: service is not ClusterIP"
            )

    for job in jobs:
        image = job["spec"]["template"]["spec"]["containers"][0]["image"]
        if "@sha256:" not in image:
            failures.append(
                f"{job['metadata']['name']}: migration image is not digest pinned"
            )

    if ingress:
        spec = ingress[0]["spec"]
        if not spec.get("tls"):
            failures.append("staging Ingress has no TLS")
        targets = {
            path["backend"]["service"]["name"]
            for path in spec["rules"][0]["http"]["paths"]
        }
        if targets != {"frontend", "api-gateway"}:
            failures.append(
                f"unexpected public targets: {sorted(targets)}"
            )

    text = Path(args.bundle).read_text(encoding="utf-8")
    if "REPLACE_WITH_SECRET_MANAGER_VALUE" in text:
        failures.append("secret example value leaked into rendered bundle")

    if failures:
        print("Staging bundle verification failed:")
        for failure in failures:
            print(" - " + failure)
        return 1

    print(
        f"PASS documents={len(docs)} deployments={len(deployments)} "
        f"services={len(services)} migration_jobs={len(jobs)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

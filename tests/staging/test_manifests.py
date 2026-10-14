"""Staging Kubernetes contracts for API deployments and dedicated event workers.

Wave 08 adds ten single-replica, Recreate-strategy queue consumers. Only
HTTP-serving API/gateway/frontend deployments require two replicas and HTTP
readiness/liveness probes. All pods remain subject to the security baseline.
"""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
STAGING = ROOT / "deploy" / "kubernetes" / "staging"
WORKER_NAMES = {
    f"{name}-service-worker"
    for name in (
        "identity", "academic", "attendance", "scheduling", "notification",
        "facility", "learning", "assessment", "reporting", "platform",
    )
}


def documents():
    docs = []
    for path in sorted(STAGING.rglob("*.yaml")):
        if "examples" in path.parts:
            continue
        if path.name in {
            "kustomization.yaml",
            "migrations.kustomization.yaml",
            "secrets.example.yaml",
        }:
            continue
        docs.extend(
            doc
            for doc in yaml.safe_load_all(path.read_text(encoding="utf-8"))
            if isinstance(doc, dict)
        )
    return docs


def test_resource_counts():
    docs = documents()
    counts = {}
    for doc in docs:
        counts[doc["kind"]] = counts.get(doc["kind"], 0) + 1

    deployments = [doc for doc in docs if doc["kind"] == "Deployment"]
    workers = {
        doc["metadata"]["name"]
        for doc in deployments
        if doc["metadata"]["name"].endswith("-worker")
    }
    assert workers == WORKER_NAMES
    assert len(deployments) - len(workers) == 12
    assert counts["Deployment"] == 22  # 12 HTTP services + 10 event workers
    assert counts["Service"] == 12       # workers are private queue consumers
    assert counts["HorizontalPodAutoscaler"] == 12
    assert counts["PodDisruptionBudget"] == 12
    assert counts["Job"] == 10
    assert counts["Ingress"] == 1


def test_staging_services_are_private_clusterip():
    for doc in documents():
        if doc.get("kind") == "Service":
            assert doc["spec"]["type"] == "ClusterIP"


def test_staging_api_and_worker_deployments_are_hardened():
    for doc in documents():
        if doc.get("kind") != "Deployment":
            continue
        name = doc["metadata"]["name"]
        is_worker = name in WORKER_NAMES
        pod = doc["spec"]["template"]["spec"]
        container = pod["containers"][0]
        if is_worker:
            # A single consumer avoids duplicate message processing in the
            # existing event-worker design; it has no HTTP health endpoint.
            assert doc["spec"]["replicas"] == 1, name
            assert doc["spec"]["strategy"]["type"] == "Recreate", name
            assert container["command"] == ["python", "-m", "app.event_worker"], name
            assert pod["terminationGracePeriodSeconds"] >= 30, name
        else:
            assert not name.endswith("-worker"), name
            assert doc["spec"]["replicas"] >= 2, name
            assert container["readinessProbe"], name
            assert container["livenessProbe"], name
        assert pod["securityContext"]["runAsNonRoot"] is True, name
        assert pod["securityContext"]["seccompProfile"]["type"] == "RuntimeDefault", name
        assert pod["automountServiceAccountToken"] is False, name
        assert container["securityContext"]["allowPrivilegeEscalation"] is False, name
        assert container["securityContext"]["readOnlyRootFilesystem"] is True, name
        assert "ALL" in container["securityContext"]["capabilities"]["drop"], name
        assert container["resources"]["requests"], name
        assert container["resources"]["limits"], name


def test_public_ingress_only_routes_frontend_and_gateway():
    ingress = next(doc for doc in documents() if doc.get("kind") == "Ingress")
    paths = ingress["spec"]["rules"][0]["http"]["paths"]
    targets = {path["backend"]["service"]["name"] for path in paths}
    assert targets == {"frontend", "api-gateway"}
    assert ingress["spec"]["tls"]

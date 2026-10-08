from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
STAGING = ROOT / "deploy" / "kubernetes" / "staging"


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

    assert counts["Deployment"] == 12
    assert counts["Service"] == 12
    assert counts["HorizontalPodAutoscaler"] == 12
    assert counts["PodDisruptionBudget"] == 12
    assert counts["Job"] == 10
    assert counts["Ingress"] == 1


def test_staging_services_are_private_clusterip():
    for doc in documents():
        if doc.get("kind") == "Service":
            assert doc["spec"]["type"] == "ClusterIP"


def test_all_staging_deployments_are_multi_replica_and_hardened():
    for doc in documents():
        if doc.get("kind") != "Deployment":
            continue
        assert doc["spec"]["replicas"] >= 2
        pod = doc["spec"]["template"]["spec"]
        container = pod["containers"][0]
        assert pod["securityContext"]["runAsNonRoot"] is True
        assert pod["securityContext"]["seccompProfile"]["type"] == "RuntimeDefault"
        assert pod["automountServiceAccountToken"] is False
        assert container["securityContext"]["allowPrivilegeEscalation"] is False
        assert container["securityContext"]["readOnlyRootFilesystem"] is True
        assert "ALL" in container["securityContext"]["capabilities"]["drop"]
        assert container["readinessProbe"]
        assert container["livenessProbe"]


def test_public_ingress_only_routes_frontend_and_gateway():
    ingress = next(doc for doc in documents() if doc.get("kind") == "Ingress")
    paths = ingress["spec"]["rules"][0]["http"]["paths"]
    targets = {path["backend"]["service"]["name"] for path in paths}
    assert targets == {"frontend", "api-gateway"}
    assert ingress["spec"]["tls"]

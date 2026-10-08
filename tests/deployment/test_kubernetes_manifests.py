from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
PROD = ROOT / "deploy" / "kubernetes" / "production"


def documents():
    result = []
    for path in sorted(PROD.rglob("*.yaml")):
        if "examples" in path.parts:
            continue
        if path.name in {"kustomization.yaml", "secrets.example.yaml"}:
            continue
        result.extend(
            doc
            for doc in yaml.safe_load_all(path.read_text(encoding="utf-8"))
            if isinstance(doc, dict)
        )
    return result


def test_kubernetes_resource_counts():
    docs = documents()
    kinds = {}
    for doc in docs:
        kinds[doc["kind"]] = kinds.get(doc["kind"], 0) + 1

    assert kinds["Deployment"] == 12
    assert kinds["Service"] == 12
    assert kinds["HorizontalPodAutoscaler"] == 12
    assert kinds["PodDisruptionBudget"] == 12
    assert kinds["Ingress"] == 1
    assert kinds["Namespace"] == 1


def test_services_are_cluster_internal():
    for doc in documents():
        if doc.get("kind") == "Service":
            assert doc["spec"]["type"] == "ClusterIP"


def test_deployments_have_security_resources_and_probes():
    for doc in documents():
        if doc.get("kind") != "Deployment":
            continue
        name = doc["metadata"]["name"]
        pod = doc["spec"]["template"]["spec"]
        container = pod["containers"][0]

        assert pod["securityContext"]["runAsNonRoot"] is True, name
        assert pod["securityContext"]["seccompProfile"]["type"] == "RuntimeDefault", name
        assert pod["automountServiceAccountToken"] is False, name
        assert container["securityContext"]["allowPrivilegeEscalation"] is False, name
        assert container["securityContext"]["readOnlyRootFilesystem"] is True, name
        assert "ALL" in container["securityContext"]["capabilities"]["drop"], name
        assert container["resources"]["requests"], name
        assert container["resources"]["limits"], name
        assert container["readinessProbe"], name
        assert container["livenessProbe"], name


def test_ingress_only_routes_to_frontend_and_gateway_and_uses_tls():
    ingress = next(doc for doc in documents() if doc.get("kind") == "Ingress")
    paths = ingress["spec"]["rules"][0]["http"]["paths"]
    targets = {path["backend"]["service"]["name"] for path in paths}
    assert targets == {"frontend", "api-gateway"}
    assert ingress["spec"]["tls"]

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml

from .models import ReleaseManifest, StagingTopology


def _load_documents(root: Path) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.yaml")):
        if "examples" in path.parts:
            continue
        if path.name in {
            "kustomization.yaml",
            "secrets.example.yaml",
            "migrations.kustomization.yaml",
        }:
            continue
        for document in yaml.safe_load_all(path.read_text(encoding="utf-8")):
            if isinstance(document, dict):
                documents.append(document)
    return documents


def render_bundle(
    manifest_root: str | Path,
    topology: StagingTopology,
    release: ReleaseManifest,
) -> list[dict[str, Any]]:
    images = {item.component: item.immutable_ref for item in release.images}
    overrides = {item.component: item for item in topology.workload_overrides}
    required = set(overrides)
    missing = required - set(images)
    if missing:
        raise ValueError(f"release missing images: {sorted(missing)}")

    result: list[dict[str, Any]] = []
    for source in _load_documents(Path(manifest_root)):
        doc = copy.deepcopy(source)
        metadata = doc.setdefault("metadata", {})
        kind = doc.get("kind")
        labels = metadata.get("labels", {})
        component = labels.get("smartedu.io/component")

        if kind == "Namespace":
            metadata["name"] = topology.namespace
        elif metadata.get("namespace") == "smartedu-staging":
            metadata["namespace"] = topology.namespace

        if kind == "Deployment" and component in overrides:
            override = overrides[component]
            doc["spec"]["replicas"] = override.replicas
            containers = doc["spec"]["template"]["spec"]["containers"]
            if len(containers) != 1:
                raise ValueError(f"{component}: expected one application container")
            containers[0]["image"] = images[component]

        if kind == "HorizontalPodAutoscaler" and component in overrides:
            override = overrides[component]
            doc["spec"]["minReplicas"] = override.min_replicas
            doc["spec"]["maxReplicas"] = override.max_replicas

        if kind == "Job" and component:
            if component not in release.migration_components:
                continue
            containers = doc["spec"]["template"]["spec"]["containers"]
            containers[0]["image"] = images[component]

        if kind == "ConfigMap" and metadata.get("name") == "smartedu-staging-runtime":
            data = doc.setdefault("data", {})
            data["FRONTEND_ORIGIN"] = f"https://{topology.public_host}"
            data["PUBLIC_BASE_URL"] = f"https://{topology.public_host}"

        if kind == "Ingress":
            rules = doc["spec"].get("rules", [])
            if rules:
                rules[0]["host"] = topology.public_host
            tls = doc["spec"].get("tls", [])
            if tls:
                tls[0]["hosts"] = [topology.public_host]
                tls[0]["secretName"] = topology.tls_secret_name
            doc["spec"]["ingressClassName"] = topology.ingress_class

        result.append(doc)

    return result


def write_bundle(documents: list[dict[str, Any]], output: str | Path) -> None:
    Path(output).write_text(
        yaml.safe_dump_all(
            documents,
            sort_keys=False,
            explicit_start=True,
        ),
        encoding="utf-8",
    )

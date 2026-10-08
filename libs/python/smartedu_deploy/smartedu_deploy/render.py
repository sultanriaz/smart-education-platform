from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml

from .models import ProductionTopology, ReleaseManifest
from .release import release_image_map
from .topology import workload_map


def _documents(path: Path) -> list[dict[str, Any]]:
    return [
        document
        for document in yaml.safe_load_all(path.read_text(encoding="utf-8"))
        if isinstance(document, dict)
    ]


def _replace_workload(
    document: dict[str, Any],
    *,
    images: dict[str, str],
    topology: ProductionTopology,
) -> dict[str, Any]:
    result = copy.deepcopy(document)
    kind = result.get("kind")
    metadata = result.get("metadata", {})
    component = metadata.get("labels", {}).get("smartedu.io/component")
    workloads = workload_map(topology)

    if kind == "Deployment" and component in workloads:
        spec = result["spec"]
        item = workloads[component]
        spec["replicas"] = item.replicas

        containers = spec["template"]["spec"]["containers"]
        if len(containers) != 1:
            raise ValueError(f"{component}: expected exactly one app container")
        containers[0]["image"] = images[component]

    if kind == "HorizontalPodAutoscaler" and component in workloads:
        item = workloads[component]
        result["spec"]["minReplicas"] = item.min_replicas
        result["spec"]["maxReplicas"] = item.max_replicas

    if kind == "ConfigMap" and metadata.get("name") == "smartedu-runtime-config":
        data = result.setdefault("data", {})
        data["FRONTEND_ORIGIN"] = f"https://{topology.public_host}"
        data["PUBLIC_BASE_URL"] = f"https://{topology.public_host}"

    if kind == "Ingress":
        rules = result["spec"].get("rules", [])
        if rules:
            rules[0]["host"] = topology.public_host
        tls = result["spec"].get("tls", [])
        if tls:
            tls[0]["hosts"] = [topology.public_host]
            tls[0]["secretName"] = topology.tls_secret_name

    return result


def render_bundle(
    *,
    manifest_dir: str | Path,
    release: ReleaseManifest,
    topology: ProductionTopology,
) -> list[dict[str, Any]]:
    manifest_dir = Path(manifest_dir)
    images = release_image_map(release)
    required = {item.component for item in topology.workloads}
    missing = required - set(images)
    if missing:
        raise ValueError(f"release manifest missing images: {sorted(missing)}")

    documents: list[dict[str, Any]] = []
    for path in sorted(manifest_dir.rglob("*.yaml")):
        if "examples" in path.parts:
            continue
        if path.name in {"kustomization.yaml", "secrets.example.yaml"}:
            continue
        for document in _documents(path):
            documents.append(
                _replace_workload(
                    document,
                    images=images,
                    topology=topology,
                )
            )
    return documents


def write_bundle(documents: list[dict[str, Any]], output: str | Path) -> None:
    Path(output).write_text(
        yaml.safe_dump_all(
            documents,
            sort_keys=False,
            explicit_start=True,
        ),
        encoding="utf-8",
    )

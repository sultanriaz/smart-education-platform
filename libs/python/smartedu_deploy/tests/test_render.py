import json
from pathlib import Path

import yaml

from smartedu_deploy import (
    load_release_manifest,
    load_topology,
    render_bundle,
)


def test_render_replaces_bootstrap_images_and_public_host(tmp_path: Path):
    topology_path = tmp_path / "topology.yaml"
    topology_path.write_text(
        yaml.safe_dump(
            {
                "public_host": "prod.example.org",
                "tls_secret_name": "prod-tls",
                "workloads": [
                    {
                        "component": "identity-service",
                        "kind": "python-service",
                        "port": 8000,
                        "replicas": 2,
                        "min_replicas": 2,
                        "max_replicas": 4,
                        "resources": {
                            "cpu_request": "100m",
                            "memory_request": "128Mi",
                            "cpu_limit": "500m",
                            "memory_limit": "256Mi",
                        },
                    }
                ],
                "external_dependencies": [],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    manifest_dir = tmp_path / "manifests"
    manifest_dir.mkdir()
    (manifest_dir / "deployment.yaml").write_text(
        yaml.safe_dump(
            {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "name": "identity-service",
                    "labels": {"smartedu.io/component": "identity-service"},
                },
                "spec": {
                    "replicas": 2,
                    "template": {
                        "spec": {
                            "containers": [
                                {
                                    "name": "identity-service",
                                    "image": "smartedu.local/identity-service:bootstrap",
                                }
                            ]
                        }
                    },
                },
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    release_path = tmp_path / "release.json"
    release_path.write_text(
        json.dumps(
            {
                "release_tag": "v1.0.0",
                "commit_sha": "a" * 40,
                "generated_at": "2026-10-07T00:00:00+00:00",
                "source_repository": "owner/repo",
                "images": [
                    {
                        "component": "identity-service",
                        "repository": "ghcr.io/owner/identity-service",
                        "digest": "sha256:" + "b" * 64,
                        "immutable_ref": ("ghcr.io/owner/identity-service@sha256:" + "b" * 64),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    documents = render_bundle(
        manifest_dir=manifest_dir,
        release=load_release_manifest(release_path),
        topology=load_topology(topology_path),
    )
    assert documents[0]["spec"]["template"]["spec"]["containers"][0]["image"].endswith(
        "@sha256:" + "b" * 64
    )

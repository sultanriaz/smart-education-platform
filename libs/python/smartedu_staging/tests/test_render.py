import json
from pathlib import Path

import yaml

from smartedu_staging import load_release, load_topology, render_bundle


def test_renderer_replaces_image_host_and_migration_selection(tmp_path: Path):
    manifests = tmp_path / "manifests"
    manifests.mkdir()

    docs = [
        {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "identity-service",
                "namespace": "smartedu-staging",
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
        {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": "migrate-identity-service",
                "namespace": "smartedu-staging",
                "labels": {"smartedu.io/component": "identity-service"},
            },
            "spec": {
                "template": {
                    "spec": {
                        "containers": [
                            {
                                "name": "migration",
                                "image": "smartedu.local/identity-service:bootstrap",
                            }
                        ]
                    }
                }
            },
        },
        {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {"name": "smartedu-staging", "namespace": "smartedu-staging"},
            "spec": {
                "ingressClassName": "nginx",
                "tls": [{"hosts": ["old.example.org"], "secretName": "old"}],
                "rules": [{"host": "old.example.org", "http": {"paths": []}}],
            },
        },
    ]
    (manifests / "all.yaml").write_text(
        yaml.safe_dump_all(docs, sort_keys=False),
        encoding="utf-8",
    )

    topology_path = tmp_path / "topology.yaml"
    topology_path.write_text(
        yaml.safe_dump(
            {
                "namespace": "smartedu-staging",
                "public_host": "staging.example.org",
                "tls_secret_name": "staging-tls",
                "workload_overrides": [
                    {
                        "component": "identity-service",
                        "replicas": 2,
                        "min_replicas": 2,
                        "max_replicas": 4,
                    }
                ],
                "required_secrets": ["identity-service-secrets"],
                "stateful_dependencies": ["postgresql"],
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
                "images": [
                    {
                        "component": "identity-service",
                        "digest": "sha256:" + "b" * 64,
                        "immutable_ref": ("ghcr.io/example/identity@sha256:" + "b" * 64),
                    }
                ],
                "migration_components": ["identity-service"],
            }
        ),
        encoding="utf-8",
    )

    rendered = render_bundle(
        manifests,
        load_topology(topology_path),
        load_release(release_path),
    )
    deployment = next(doc for doc in rendered if doc["kind"] == "Deployment")
    job = next(doc for doc in rendered if doc["kind"] == "Job")
    ingress = next(doc for doc in rendered if doc["kind"] == "Ingress")

    assert "@sha256:" in deployment["spec"]["template"]["spec"]["containers"][0]["image"]
    assert "@sha256:" in job["spec"]["template"]["spec"]["containers"][0]["image"]
    assert ingress["spec"]["rules"][0]["host"] == "staging.example.org"
    assert ingress["spec"]["tls"][0]["secretName"] == "staging-tls"

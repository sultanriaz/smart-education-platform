from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml

from smartedu_launch import load_release


def safe_suffix(value: str) -> str:
    value = value.lower().lstrip("v")
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value[:40] or "release"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("release_manifest")
    parser.add_argument(
        "--components",
        default="config/launch/components.yaml",
    )
    parser.add_argument(
        "--namespace",
        default="smartedu",
    )
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    release = load_release(args.release_manifest)
    config = yaml.safe_load(
        Path(args.components).read_text(encoding="utf-8")
    )
    component_map = {
        item["component"]: item
        for item in config["components"]
    }
    images = {
        item.component: item.immutable_ref
        for item in release.images
    }

    unknown = sorted(set(release.migration_components) - set(component_map))
    if unknown:
        raise SystemExit(f"unknown migration components: {unknown}")

    documents = []
    suffix = safe_suffix(release.release_tag)
    for component in release.migration_components:
        cfg = component_map[component]
        if not cfg.get("migration"):
            raise SystemExit(
                f"{component} is listed for migration but config says migration=false"
            )
        if component not in images:
            raise SystemExit(f"release image missing for migration component {component}")

        command = cfg.get("migration_command")
        if not command:
            raise SystemExit(f"{component}: migration command is empty")

        documents.append({
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": f"migrate-{component.removesuffix('-service')}-{suffix}",
                "namespace": args.namespace,
                "labels": {
                    "app.kubernetes.io/part-of": "smart-education-platform",
                    "smartedu.io/component": component,
                    "smartedu.io/job": "production-migration",
                    "smartedu.io/release": release.release_tag,
                },
            },
            "spec": {
                "backoffLimit": 0,
                "ttlSecondsAfterFinished": 86400,
                "template": {
                    "metadata": {
                        "labels": {
                            "smartedu.io/component": component,
                            "smartedu.io/job": "production-migration",
                        }
                    },
                    "spec": {
                        "restartPolicy": "Never",
                        "serviceAccountName": component,
                        "automountServiceAccountToken": False,
                        "securityContext": {
                            "runAsNonRoot": True,
                            "seccompProfile": {"type": "RuntimeDefault"},
                        },
                        "containers": [{
                            "name": "migration",
                            "image": images[component],
                            "imagePullPolicy": "IfNotPresent",
                            "command": command,
                            "envFrom": [
                                {
                                    "configMapRef": {
                                        "name": "smartedu-runtime-config"
                                    }
                                },
                                {
                                    "secretRef": {
                                        "name": f"{component}-secrets"
                                    }
                                },
                            ],
                            "securityContext": {
                                "allowPrivilegeEscalation": False,
                                "readOnlyRootFilesystem": True,
                                "capabilities": {"drop": ["ALL"]},
                            },
                            "resources": {
                                "requests": {
                                    "cpu": "100m",
                                    "memory": "128Mi",
                                },
                                "limits": {
                                    "cpu": "1000m",
                                    "memory": "1Gi",
                                },
                            },
                            "volumeMounts": [
                                {"name": "tmp", "mountPath": "/tmp"}
                            ],
                        }],
                        "volumes": [
                            {
                                "name": "tmp",
                                "emptyDir": {"sizeLimit": "128Mi"},
                            }
                        ],
                    },
                },
            },
        })

    Path(args.output).write_text(
        yaml.safe_dump_all(documents, sort_keys=False, explicit_start=True),
        encoding="utf-8",
    )
    print(f"release={release.release_tag}")
    print(f"migration_jobs={len(documents)}")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("release_manifest")
    parser.add_argument("--context", required=True)
    parser.add_argument("--namespace", default="smartedu")
    args = parser.parse_args()

    release = json.loads(
        Path(args.release_manifest).read_text(encoding="utf-8")
    )
    expected = {
        item["component"]: item["immutable_ref"]
        for item in release.get("images", [])
    }

    result = subprocess.run(
        [
            "kubectl",
            "--context",
            args.context,
            "-n",
            args.namespace,
            "get",
            "deployment",
            "-o",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    deployments = json.loads(result.stdout)

    actual: dict[str, str] = {}
    for item in deployments.get("items", []):
        name = item["metadata"]["name"]
        containers = item["spec"]["template"]["spec"].get("containers", [])
        if len(containers) != 1:
            print(f"FAIL {name}: expected exactly one application container")
            return 1
        actual[name] = containers[0]["image"]

    failures: list[str] = []
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    if missing:
        failures.append(f"missing Deployments: {missing}")
    if extra:
        failures.append(f"unexpected Deployments: {extra}")

    for component in sorted(set(expected) & set(actual)):
        if expected[component] != actual[component]:
            failures.append(
                f"{component}: expected {expected[component]} got {actual[component]}"
            )

    if failures:
        print("Live production image verification failed:")
        for failure in failures:
            print(" - " + failure)
        return 1

    print(
        f"PASS release={release.get('release_tag')} "
        f"deployments={len(actual)} exact_images=true"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

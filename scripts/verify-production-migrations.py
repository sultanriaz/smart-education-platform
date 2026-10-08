from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from smartedu_launch import load_release


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("release_manifest")
    parser.add_argument("migration_bundle")
    args = parser.parse_args()

    release = load_release(args.release_manifest)
    docs = [
        doc
        for doc in yaml.safe_load_all(
            Path(args.migration_bundle).read_text(encoding="utf-8")
        )
        if isinstance(doc, dict)
    ]

    failures: list[str] = []
    expected = set(release.migration_components)
    seen: set[str] = set()

    for doc in docs:
        if doc.get("kind") != "Job":
            failures.append(f"unexpected kind {doc.get('kind')}")
            continue
        component = doc.get("metadata", {}).get("labels", {}).get("smartedu.io/component")
        if not component:
            failures.append("migration Job missing component label")
            continue
        seen.add(component)
        container = doc["spec"]["template"]["spec"]["containers"][0]
        image = container.get("image", "")
        if "@sha256:" not in image:
            failures.append(f"{component}: migration image not digest pinned")
        if doc["spec"].get("backoffLimit") != 0:
            failures.append(f"{component}: backoffLimit must be 0")
        if container["securityContext"].get("allowPrivilegeEscalation") is not False:
            failures.append(f"{component}: privilege escalation not disabled")

    if seen != expected:
        failures.append(
            f"migration set mismatch missing={sorted(expected-seen)} "
            f"extra={sorted(seen-expected)}"
        )

    if failures:
        print("Production migration bundle verification failed:")
        for failure in failures:
            print(" - " + failure)
        return 1

    print(f"PASS migration_jobs={len(docs)} components={sorted(seen)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

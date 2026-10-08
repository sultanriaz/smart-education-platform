from __future__ import annotations

import argparse

from smartedu_staging import (
    load_release,
    load_topology,
    render_bundle,
    write_bundle,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("release_manifest")
    parser.add_argument(
        "--topology",
        default="config/staging/staging-topology.yaml",
    )
    parser.add_argument(
        "--manifests",
        default="deploy/kubernetes/staging",
    )
    parser.add_argument(
        "--output",
        default="deploy/kubernetes/rendered-staging.yaml",
    )
    args = parser.parse_args()

    topology = load_topology(args.topology)
    release = load_release(args.release_manifest)

    documents = render_bundle(
        args.manifests,
        topology,
        release,
    )
    write_bundle(documents, args.output)

    jobs = sum(1 for doc in documents if doc.get("kind") == "Job")
    print(f"release={release.release_tag}")
    print(f"documents={len(documents)}")
    print(f"migration_jobs={jobs}")
    print(f"output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

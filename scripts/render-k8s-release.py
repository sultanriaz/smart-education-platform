from __future__ import annotations

import argparse

from smartedu_deploy import (
    load_release_manifest,
    load_topology,
    render_bundle,
    write_bundle,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("release_manifest")
    parser.add_argument(
        "--topology",
        default="config/deployment/production-topology.yaml",
    )
    parser.add_argument(
        "--manifests",
        default="deploy/kubernetes/production",
    )
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    release = load_release_manifest(args.release_manifest)
    topology = load_topology(args.topology)
    documents = render_bundle(
        manifest_dir=args.manifests,
        release=release,
        topology=topology,
    )
    write_bundle(documents, args.output)

    print(f"release={release.release_tag}")
    print(f"documents={len(documents)}")
    print(f"output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


FOUNDATION = {
    "Namespace",
    "ConfigMap",
    "ServiceAccount",
    "NetworkPolicy",
}
APPLICATION = {
    "Service",
    "Deployment",
    "HorizontalPodAutoscaler",
    "PodDisruptionBudget",
    "Ingress",
}


def write(path: Path, documents: list[dict]) -> None:
    path.write_text(
        yaml.safe_dump_all(documents, sort_keys=False, explicit_start=True),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    documents = [
        doc
        for doc in yaml.safe_load_all(
            Path(args.bundle).read_text(encoding="utf-8")
        )
        if isinstance(doc, dict)
    ]

    foundation = [doc for doc in documents if doc.get("kind") in FOUNDATION]
    migrations = [doc for doc in documents if doc.get("kind") == "Job"]
    application = [doc for doc in documents if doc.get("kind") in APPLICATION]

    unknown = [
        doc.get("kind")
        for doc in documents
        if doc.get("kind") not in FOUNDATION | APPLICATION | {"Job"}
    ]
    if unknown:
        raise SystemExit(f"Unknown resource kinds in bundle: {sorted(set(unknown))}")

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    write(output / "01-foundation.yaml", foundation)
    write(output / "02-migrations.yaml", migrations)
    write(output / "03-application.yaml", application)

    print(f"foundation={len(foundation)}")
    print(f"migrations={len(migrations)}")
    print(f"application={len(application)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

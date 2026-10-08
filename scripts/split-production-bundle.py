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

    docs = [
        doc
        for doc in yaml.safe_load_all(
            Path(args.bundle).read_text(encoding="utf-8")
        )
        if isinstance(doc, dict)
    ]

    foundation = [doc for doc in docs if doc.get("kind") in FOUNDATION]
    application = [doc for doc in docs if doc.get("kind") in APPLICATION]
    unknown = [
        doc.get("kind")
        for doc in docs
        if doc.get("kind") not in FOUNDATION | APPLICATION
    ]
    if unknown:
        raise SystemExit(
            f"unexpected resource kinds in production bundle: {sorted(set(unknown))}"
        )

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    write(output / "01-foundation.yaml", foundation)
    write(output / "03-application.yaml", application)

    print(f"foundation={len(foundation)}")
    print(f"application={len(application)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

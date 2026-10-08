from __future__ import annotations

import argparse
from pathlib import Path

import yaml


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    docs = [
        doc
        for doc in yaml.safe_load_all(
            Path(args.bundle).read_text(encoding="utf-8")
        )
        if isinstance(doc, dict) and doc.get("kind") == "Deployment"
    ]
    Path(args.output).write_text(
        yaml.safe_dump_all(docs, sort_keys=False, explicit_start=True),
        encoding="utf-8",
    )
    print(f"deployments={len(docs)}")
    return 0 if docs else 1


if __name__ == "__main__":
    raise SystemExit(main())

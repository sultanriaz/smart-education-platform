from __future__ import annotations

from pathlib import Path

import yaml


def main() -> int:
    source = Path("deploy/kubernetes/production/secrets.example.yaml")
    documents = [
        doc
        for doc in yaml.safe_load_all(source.read_text(encoding="utf-8"))
        if isinstance(doc, dict)
    ]

    print("# Production Secret Checklist")
    print()
    print(
        "Create these Kubernetes Secret objects from the approved secret manager. "
        "Do not apply the example values."
    )
    print()
    for document in documents:
        name = document["metadata"]["name"]
        keys = sorted(document.get("stringData", {}))
        print(f"## {name}")
        for key in keys:
            print(f"- [ ] `{key}`")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

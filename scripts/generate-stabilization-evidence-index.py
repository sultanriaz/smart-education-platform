from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="stabilization/evidence")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    root = Path(args.root)
    files = []
    if root.exists():
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.name != ".gitkeep":
                files.append({
                    "path": path.relative_to(root).as_posix(),
                    "size_bytes": path.stat().st_size,
                    "sha256": sha256(path),
                })

    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evidence_root": root.as_posix(),
        "files": files,
    }
    Path(args.output).write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"evidence_files={len(files)}")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

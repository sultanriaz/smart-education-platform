"""Validate and stage sprint inputs without overwriting the working tree."""
from __future__ import annotations

import hashlib
import json
import re
import stat
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / ".integration" / "staging"


def safe_name(name: str) -> PurePosixPath:
    path = PurePosixPath(name.replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts or any(":" in p for p in path.parts):
        raise ValueError(f"Unsafe archive path: {name}")
    return path


def main() -> None:
    archives = sorted(set(ROOT.glob("sprint_*.zip")) | set((ROOT / "sprint-zips").glob("*.zip")))
    inventory = []
    versions: dict[str, list[dict]] = {}
    for archive in archives:
        match = re.search(r"sprint[_-](\d+)", archive.stem, re.I)
        if not match:
            raise ValueError(f"Unidentified sprint: {archive.name}")
        sprint = int(match.group(1))
        target = STAGE / archive.stem
        with zipfile.ZipFile(archive) as zf:
            infos = zf.infolist()
            names = set()
            total = 0
            for info in infos:
                path = safe_name(info.filename)
                if stat.S_ISLNK(info.external_attr >> 16):
                    raise ValueError(f"Symlink rejected: {info.filename}")
                if str(path).casefold() in names:
                    raise ValueError(f"Duplicate path: {info.filename}")
                names.add(str(path).casefold())
                total += info.file_size
                if total > 1_000_000_000 or info.file_size > 100_000_000:
                    raise ValueError("Archive exceeds staging size limits")
            files = []
            for info in infos:
                if info.is_dir():
                    continue
                path = safe_name(info.filename)
                data = zf.read(info)
                dest = target.joinpath(*path.parts)
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(data)
                digest = hashlib.sha256(data).hexdigest()
                files.append(str(path))
                versions.setdefault(str(path), []).append({"sprint": sprint, "sha256": digest})
        inventory.append({"sprint": sprint, "archive": archive.name, "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(), "files": files, "bytes": total})
    STAGE.parent.mkdir(parents=True, exist_ok=True)
    (STAGE.parent / "inventory.json").write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    (STAGE.parent / "versions.json").write_text(json.dumps(versions, indent=2), encoding="utf-8")
    lines = ["# Sprint inventory", "", "Archives validated for traversal, duplicate paths, symlinks and size before staged extraction.", "", "| Sprint | Source | Files | State |", "|---|---|---:|---|"]
    for sprint in range(1, 29):
        entries = [x for x in inventory if x["sprint"] == sprint]
        if not entries:
            lines.append(f"| {sprint} | Package unavailable | — | Existing implementation {'present; not reimported' if sprint <= 3 else 'missing'} |")
        for entry in entries:
            lines.append(f"| {sprint} | `{entry['archive']}` | {len(entry['files'])} | Safely staged; integration pending |")
    (ROOT / "docs/integration/SPRINT_INVENTORY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for entry in inventory:
        roots = sorted(set(p.split("/")[0] for p in entry["files"]))
        print(f"Sprint {entry['sprint']:02}: {len(entry['files'])} files; roots: {', '.join(roots)}")
    conflicts = {p: entries for p, entries in versions.items() if len(set(e["sha256"] for e in entries)) > 1}
    print(f"Changed paths across archives: {len(conflicts)}")
    for path, entries in conflicts.items():
        print(f"  {path}: {[e['sprint'] for e in entries]}")


if __name__ == "__main__":
    main()

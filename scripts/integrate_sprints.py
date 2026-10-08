"""Apply reviewed chronological overlays, retaining per-sprint provenance."""
from __future__ import annotations

import ast
import difflib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".integration"
REVIEWED = {
    "apps/frontend/src/app/AppRouter.tsx": "Sprint 18 retains all Student/Teacher/Admin routes from Sprint 15 and adds recovery routes.",
    "apps/frontend/src/lib/api-client.ts": "Sprint 18 retains Sprint 16 stable idempotency retries and Sprint 13 downloads; adopts HttpOnly refresh.",
    "apps/frontend/src/lib/token-store.ts": "Remove browser refresh-token persistence; keep access tokens in memory.",
    "services/assessment-service/app/api/v1/router.py": "Sprint 14 includes both Sprint 13 student_read and teacher_read routers.",
    "services/notification-service/app/api/v1/router.py": "Sprint 14 retains prior routes and adds teacher announcements.",
}


def definitions(data: bytes, path: str) -> set[str]:
    if not path.endswith(".py"):
        return set()
    return {n.name for n in ast.walk(ast.parse(data)) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}


def main() -> None:
    if (WORK / "merge-manifest.json").exists():
        raise SystemExit("Packages were already imported. Review diffs manually; rerunning would overwrite integration fixes.")
    inventory = json.loads((WORK / "inventory.json").read_text())
    changes = []
    diffs = []
    for entry in sorted(inventory, key=lambda x: x["sprint"]):
        sprint = entry["sprint"]
        stage = WORK / "staging" / Path(entry["archive"]).stem
        for name in entry["files"]:
            source = stage / name
            dest = ROOT / name
            if "/" not in name and name.endswith(".md"):
                dest = ROOT / "docs/sprints" / f"sprint-{sprint:02}" / name
            if name.startswith(".gitignore.sprint"):
                dest = ROOT / "docs/sprints" / f"sprint-{sprint:02}" / name
            data = source.read_bytes()
            action = "add"
            if dest.exists():
                previous = dest.read_bytes()
                if data == previous:
                    continue
                removed = definitions(previous, name) - definitions(data, name)
                if removed:
                    raise RuntimeError(f"Overlay removes Python definitions: {name}: {removed}")
                action = "consolidate"
                backup = WORK / "before-overlay" / f"sprint-{sprint:02}" / name
                backup.parent.mkdir(parents=True, exist_ok=True)
                backup.write_bytes(previous)
                try:
                    diffs.extend(difflib.unified_diff(previous.decode("utf-8").splitlines(True), data.decode("utf-8").splitlines(True), fromfile=f"before sprint {sprint}/{name}", tofile=f"sprint {sprint}/{name}"))
                except UnicodeDecodeError:
                    pass
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            changes.append({"sprint": sprint, "path": str(dest.relative_to(ROOT)).replace("\\", "/"), "action": action})
    (WORK / "merge-diffs.patch").write_text("".join(diffs), encoding="utf-8")
    (WORK / "merge-manifest.json").write_text(json.dumps(changes, indent=2), encoding="utf-8")
    lines = ["# Merge decisions", "", "Original tracked work retained in the Git bundle. Every replaced file also has a staged pre-overlay backup. Source ZIPs preserved.", "", "Root sprint instructions and verification reports are stored under `docs/sprints/sprint-NN/`; reports are historical package evidence, not results of this integration.", "", "## Overlapping files", ""]
    for change in changes:
        if change["action"] == "consolidate":
            path = change["path"]
            reason = REVIEWED.get(path, "Chronological extension retained with before/after diff; regression verification required.")
            lines.append(f"- Sprint {change['sprint']}: `{path}` — {reason}")
    lines.extend(["", "Legacy `apps/backend` scaffold retained for recovery, excluded from the active distributed runtime. Ten service databases remain separately owned.", "", "Complete per-file provenance: `.integration/merge-manifest.json`. Consolidation diff: `.integration/merge-diffs.patch`."])
    (ROOT / "docs/integration/MERGE_DECISIONS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Applied {len(changes)} file additions/consolidations from {len(inventory)} validated packages.")


if __name__ == "__main__":
    main()

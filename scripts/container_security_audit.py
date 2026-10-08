from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


def final_stage(text: str) -> str:
    parts = re.split(r"(?im)^FROM\s+", text)
    return parts[-1] if len(parts) > 1 else text


def audit_dockerfile(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    stage = final_stage(text)
    findings: list[str] = []

    user_matches = re.findall(r"(?im)^USER\s+([^\s]+)", stage)
    if not user_matches:
        findings.append("final image has no USER directive")
    elif user_matches[-1].casefold() in {"root", "0", "0:0"}:
        findings.append("final image runs as root")

    if re.search(r"(?im)^ADD\s+https?://", text):
        findings.append("remote URL used with ADD")

    if re.search(
        r"(?im)^ENV\s+.*(?:PASSWORD|SECRET|TOKEN|PRIVATE_KEY)\s*=",
        text,
    ):
        findings.append("secret-like value configured with Docker ENV")

    if re.search(r"(?im)^FROM\s+\S+:latest\b", text):
        findings.append("uses mutable :latest base image")

    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    inventory = subprocess.run(["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard", "-z"], capture_output=True)
    paths = [root / name for name in inventory.stdout.decode("utf-8").split("\0") if name] if inventory.returncode == 0 else root.rglob("*")
    dockerfiles = [
        path
        for path in paths
        if path.is_file()
        and (
            path.name == "Dockerfile"
            or path.name.startswith("Dockerfile.")
            or path.name.endswith(".Dockerfile")
        )
        and ".git" not in path.parts
        and "node_modules" not in path.parts
        and not {".integration", ".venv", "artifacts"}.intersection(path.parts)
    ]

    findings = []
    audited = 0
    for path in dockerfiles:
        if not path.read_text(encoding="utf-8").strip():
            print(f"SKIPPED empty legacy scaffold: {path.relative_to(root)}")
            continue
        audited += 1
        for issue in audit_dockerfile(path):
            findings.append((path.relative_to(root), issue))

    if findings:
        print("Container hardening findings:")
        for path, issue in findings:
            print(f"{path}: {issue}")
        return 1 if args.strict else 0

    print(f"Container audit passed for {audited} Dockerfiles.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

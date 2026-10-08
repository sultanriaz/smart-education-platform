from __future__ import annotations

import argparse
import math
import re
import sys
import subprocess
from pathlib import Path

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".pytest_cache",
    ".integration",
    "artifacts",
    "test-results",
    "playwright-report",
    ".ruff_cache",
}

TEXT_SUFFIXES = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".yaml", ".yml",
    ".toml", ".ini", ".conf", ".env", ".md", ".txt", ".ps1", ".sh",
    ".dockerfile", ".sql",
}

ALLOW_PLACEHOLDER_FRAGMENTS = (
    "CHANGE_ME_",
    "<secret",
    "<password",
    "<token",
    "${",
    "development-only-change-me",
    "example",
)

PATTERNS = [
    (
        "private-key",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |ED25519 )?PRIVATE KEY-----"),
    ),
    (
        "aws-access-key",
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    ),
    (
        "github-token",
        re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b"),
    ),
    (
        "slack-token",
        re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    ),
    (
        "generic-secret-assignment",
        re.compile(
            r"""(?ix)
            \b(password|passwd|secret|api[_-]?key|access[_-]?token|refresh[_-]?token)
            \s*[:=]\s*
            ["']([^"'\r\n]{12,})["']
            """
        ),
    ),
]


def entropy(value: str) -> float:
    if not value:
        return 0.0
    counts = {ch: value.count(ch) for ch in set(value)}
    result = 0.0
    for count in counts.values():
        p = count / len(value)
        result -= p * math.log2(p)
    return result


def should_scan(path: Path) -> bool:
    if any(part in SKIP_DIRS for part in path.parts):
        return False
    if path.name.endswith(".example"):
        return False
    if path.suffix.lower() in TEXT_SUFFIXES:
        return True
    if path.name in {"Dockerfile", ".env", ".gitignore"}:
        return True
    return False


def placeholder(value: str) -> bool:
    folded = value.casefold()
    return any(fragment.casefold() in folded for fragment in ALLOW_PLACEHOLDER_FRAGMENTS)


def scan_file(path: Path) -> list[tuple[int, str, str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []

    findings: list[tuple[int, str, str]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        for name, pattern in PATTERNS:
            match = pattern.search(line)
            if not match:
                continue

            value = match.group(match.lastindex or 0) if match.lastindex else match.group(0)
            if placeholder(value):
                continue
            if name == "generic-secret-assignment" and "# secret-scan: test-fixture" in line and ("tests" in path.parts or path.name == "sprint_identity_service.ps1"):
                continue
            findings.append((number, name, "[redacted]"))

        # Catch high-entropy literals assigned to obvious secret-like names even
        # when quoting/format differs from the generic pattern.
        if re.search(r"(?i)\b(secret|password|token|api[_-]?key)\b", line):
            for literal in re.findall(r"""["']([A-Za-z0-9+/=_-]{24,})["']""", line):
                if not placeholder(literal) and entropy(literal) >= 4.0:
                    findings.append(
                        (number, "high-entropy-secret-like-literal", "[redacted]")
                    )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    findings = []

    git_files = subprocess.run(["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard", "-z"], capture_output=True)
    paths = [root / name for name in git_files.stdout.decode("utf-8").split("\0") if name] if git_files.returncode == 0 else root.rglob("*")
    for path in paths:
        if path.is_file() and should_scan(path.relative_to(root)):
            for line, kind, excerpt in scan_file(path):
                findings.append(
                    (str(path.relative_to(root)), line, kind, excerpt)
                )

    if findings:
        print("Potential secrets found:")
        for path, line, kind, excerpt in findings:
            print(f"{path}:{line}: {kind}: {excerpt}")
        return 1 if args.strict else 0

    print("Secret scan passed: no high-confidence findings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

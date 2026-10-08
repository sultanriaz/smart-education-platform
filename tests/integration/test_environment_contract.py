from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.architecture
def test_no_production_example_uses_plain_http_for_external_endpoints():
    production_files = list(ROOT.rglob("*production*.example"))
    findings = []

    for path in production_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for number, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if re.search(r"=(?:http|redis|amqp)://", stripped):
                findings.append(f"{path.relative_to(ROOT)}:{number}: {stripped}")

    assert not findings, (
        "Production templates contain plaintext external protocols:\n"
        + "\n".join(findings)
    )

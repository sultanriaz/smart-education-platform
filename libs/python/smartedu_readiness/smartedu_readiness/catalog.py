from __future__ import annotations

from pathlib import Path

import yaml

from .models import ReadinessCheck


def load_checks(path: str | Path) -> list[ReadinessCheck]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    checks = [ReadinessCheck.model_validate(item) for item in payload.get("checks", [])]
    ids = [item.id for item in checks]
    if len(ids) != len(set(ids)):
        raise ValueError("readiness check IDs must be unique")
    return checks


def check_map(path: str | Path) -> dict[str, ReadinessCheck]:
    return {item.id: item for item in load_checks(path)}

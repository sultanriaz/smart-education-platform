from __future__ import annotations

from pathlib import Path

import yaml

from .models import StabilizationCheckpoint


def load_checkpoints(path: str | Path) -> list[StabilizationCheckpoint]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    checkpoints = [
        StabilizationCheckpoint.model_validate(item) for item in payload.get("checkpoints", [])
    ]
    ids = [item.id for item in checkpoints]
    if len(ids) != len(set(ids)):
        raise ValueError("stabilization checkpoint IDs must be unique")
    return checkpoints


def checkpoint_map(path: str | Path) -> dict[str, StabilizationCheckpoint]:
    return {item.id: item for item in load_checkpoints(path)}

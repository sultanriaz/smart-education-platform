from __future__ import annotations

import json
from pathlib import Path

import yaml

from .models import StabilizationRun


def load_run(path: str | Path) -> StabilizationRun:
    return StabilizationRun.model_validate(json.loads(Path(path).read_text(encoding="utf-8")))


def save_run(run: StabilizationRun, path: str | Path) -> None:
    Path(path).write_text(
        json.dumps(run.model_dump(mode="json"), indent=2) + "\n",
        encoding="utf-8",
    )


def load_policy(path: str | Path) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}

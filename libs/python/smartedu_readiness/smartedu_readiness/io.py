from __future__ import annotations

import json
from pathlib import Path

import yaml

from .models import ReadinessPolicy, ReadinessRun


def load_policy(path: str | Path) -> ReadinessPolicy:
    return ReadinessPolicy.model_validate(yaml.safe_load(Path(path).read_text(encoding="utf-8")))


def load_run(path: str | Path) -> ReadinessRun:
    return ReadinessRun.model_validate(json.loads(Path(path).read_text(encoding="utf-8")))


def save_run(run: ReadinessRun, path: str | Path) -> None:
    Path(path).write_text(
        json.dumps(run.model_dump(mode="json"), indent=2) + "\n",
        encoding="utf-8",
    )

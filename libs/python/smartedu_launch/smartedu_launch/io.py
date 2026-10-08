from __future__ import annotations

import json
from pathlib import Path

from .models import LaunchRecord, ReleaseManifest


def load_release(path: str | Path) -> ReleaseManifest:
    return ReleaseManifest.model_validate(json.loads(Path(path).read_text(encoding="utf-8")))


def load_launch(path: str | Path) -> LaunchRecord:
    return LaunchRecord.model_validate(json.loads(Path(path).read_text(encoding="utf-8")))


def save_launch(record: LaunchRecord, path: str | Path) -> None:
    Path(path).write_text(
        json.dumps(record.model_dump(mode="json"), indent=2) + "\n",
        encoding="utf-8",
    )

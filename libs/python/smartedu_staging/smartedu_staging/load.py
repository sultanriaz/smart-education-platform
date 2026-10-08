from __future__ import annotations

import json
from pathlib import Path

import yaml

from .models import ReleaseManifest, StagingTopology


def load_topology(path: str | Path) -> StagingTopology:
    return StagingTopology.model_validate(yaml.safe_load(Path(path).read_text(encoding="utf-8")))


def load_release(path: str | Path) -> ReleaseManifest:
    return ReleaseManifest.model_validate(json.loads(Path(path).read_text(encoding="utf-8")))

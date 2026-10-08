from __future__ import annotations

import json
from pathlib import Path

from .models import ReleaseManifest


def load_release_manifest(path: str | Path) -> ReleaseManifest:
    return ReleaseManifest.model_validate(json.loads(Path(path).read_text(encoding="utf-8")))


def release_image_map(manifest: ReleaseManifest) -> dict[str, str]:
    return {item.component: item.immutable_ref for item in manifest.images}

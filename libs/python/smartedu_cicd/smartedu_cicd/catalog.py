from __future__ import annotations

import fnmatch
from pathlib import Path

import yaml

from .models import Component, ComponentCatalog


def load_catalog(path: str | Path) -> ComponentCatalog:
    return ComponentCatalog.model_validate(yaml.safe_load(Path(path).read_text(encoding="utf-8")))


def _matches(path: str, pattern: str) -> bool:
    path = path.replace("\\", "/").lstrip("./")
    pattern = pattern.replace("\\", "/").lstrip("./")
    prefix = pattern.removesuffix("**").rstrip("/")
    return fnmatch.fnmatch(path, pattern) or (bool(prefix) and path.startswith(prefix + "/"))


def affected_components(catalog: ComponentCatalog, changed_files: list[str]) -> list[Component]:
    if not changed_files:
        return []
    if any(
        _matches(changed, pattern)
        for changed in changed_files
        for pattern in catalog.global_watched_paths
    ):
        return list(catalog.components)
    result = []
    for component in catalog.components:
        patterns = [
            component.path.rstrip("/") + "/**",
            component.dockerfile,
            *component.watched_paths,
        ]
        if any(_matches(changed, pattern) for changed in changed_files for pattern in patterns):
            result.append(component)
    return result

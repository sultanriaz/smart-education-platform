from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


def load_schema(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_json(payload: Any, schema: dict[str, Any]) -> None:
    Draft202012Validator(schema).validate(payload)


def collect_openapi_paths(document: dict[str, Any]) -> set[str]:
    paths = document.get("paths", {})
    return set(paths.keys()) if isinstance(paths, dict) else set()


def assert_no_internal_paths(document: dict[str, Any]) -> None:
    for path in collect_openapi_paths(document):
        if "/internal/" in path:
            raise AssertionError(f"Internal path leaked into public contract: {path}")

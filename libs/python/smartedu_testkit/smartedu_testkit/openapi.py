from __future__ import annotations

from dataclasses import dataclass
from typing import Any

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head"}


@dataclass(frozen=True)
class OpenApiBreakingChange:
    kind: str
    location: str
    message: str


def breaking_changes(
    old: dict[str, Any],
    new: dict[str, Any],
) -> list[OpenApiBreakingChange]:
    changes: list[OpenApiBreakingChange] = []
    old_paths = old.get("paths", {}) if isinstance(old.get("paths", {}), dict) else {}
    new_paths = new.get("paths", {}) if isinstance(new.get("paths", {}), dict) else {}

    for path, old_item in old_paths.items():
        if path not in new_paths:
            changes.append(
                OpenApiBreakingChange(
                    "removed_path",
                    path,
                    f"Public path removed: {path}",
                )
            )
            continue

        if not isinstance(old_item, dict) or not isinstance(new_paths[path], dict):
            continue

        new_item = new_paths[path]
        for method in HTTP_METHODS:
            if method in old_item and method not in new_item:
                changes.append(
                    OpenApiBreakingChange(
                        "removed_operation",
                        f"{method.upper()} {path}",
                        f"Operation removed: {method.upper()} {path}",
                    )
                )

            if method not in old_item or method not in new_item:
                continue

            old_responses = old_item[method].get("responses", {})
            new_responses = new_item[method].get("responses", {})
            for status in old_responses:
                if status not in new_responses:
                    changes.append(
                        OpenApiBreakingChange(
                            "removed_response",
                            f"{method.upper()} {path} {status}",
                            f"Documented response removed: {status}",
                        )
                    )

    return changes

from __future__ import annotations

from pathlib import Path

import yaml

from .models import UATScenario


def load_scenarios(root: str | Path) -> list[UATScenario]:
    root = Path(root)
    scenarios: list[UATScenario] = []
    for path in sorted(root.glob("*.yaml")):
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for raw in payload.get("scenarios", []):
            scenarios.append(UATScenario.model_validate(raw))
    ids = [item.id for item in scenarios]
    if len(ids) != len(set(ids)):
        raise ValueError("UAT scenario IDs must be globally unique")
    return scenarios


def scenario_map(root: str | Path) -> dict[str, UATScenario]:
    return {item.id: item for item in load_scenarios(root)}

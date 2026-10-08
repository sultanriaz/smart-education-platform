from __future__ import annotations

from pathlib import Path

import yaml

from .models import ProductionTopology


def load_topology(path: str | Path) -> ProductionTopology:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return ProductionTopology.model_validate(payload)


def workload_map(topology: ProductionTopology):
    return {item.component: item for item in topology.workloads}

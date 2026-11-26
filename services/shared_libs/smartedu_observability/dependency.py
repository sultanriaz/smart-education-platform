from __future__ import annotations

import time
from collections.abc import Iterator
from contextlib import contextmanager

from .metrics import Metrics


@contextmanager
def observe_dependency(
    metrics: Metrics,
    *,
    dependency: str,
    operation: str,
) -> Iterator[None]:
    started = time.perf_counter()
    outcome = "success"
    try:
        yield
    except Exception:
        outcome = "failure"
        raise
    finally:
        duration = time.perf_counter() - started
        metrics.dependency_requests.labels(
            metrics.service_name,
            dependency,
            operation,
            outcome,
        ).inc()
        metrics.dependency_duration.labels(
            metrics.service_name,
            dependency,
            operation,
        ).observe(duration)

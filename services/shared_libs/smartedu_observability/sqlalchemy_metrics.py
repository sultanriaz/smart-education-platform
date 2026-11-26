from __future__ import annotations

from sqlalchemy import event

from .metrics import Metrics


def install_pool_metrics(
    engine,
    *,
    metrics: Metrics,
    database_name: str,
) -> None:
    service = metrics.service_name

    @event.listens_for(engine.pool, "checkout")
    def _checkout(*_args) -> None:
        metrics.db_pool_checked_out.labels(
            service,
            database_name,
        ).inc()

    @event.listens_for(engine.pool, "checkin")
    def _checkin(*_args) -> None:
        metrics.db_pool_checked_out.labels(
            service,
            database_name,
        ).dec()

    @event.listens_for(engine.pool, "invalidate")
    def _invalidate(*_args) -> None:
        metrics.db_pool_checkout_failures.labels(
            service,
            database_name,
        ).inc()

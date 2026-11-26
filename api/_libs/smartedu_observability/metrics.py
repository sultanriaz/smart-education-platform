from __future__ import annotations

from datetime import UTC, datetime

from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
)


class Metrics:
    def __init__(
        self,
        *,
        service_name: str,
        service_version: str = "unknown",
        environment: str = "development",
        registry: CollectorRegistry | None = None,
    ):
        self.registry = registry or CollectorRegistry(auto_describe=True)

        self.build = Info(
            "smartedu_build",
            "Service build information.",
            registry=self.registry,
        )
        self.build.info(
            {
                "service": service_name,
                "version": service_version,
                "environment": environment,
            }
        )

        self.http_requests = Counter(
            "smartedu_http_requests_total",
            "HTTP requests completed.",
            ["service", "method", "route", "status_class"],
            registry=self.registry,
        )
        self.http_duration = Histogram(
            "smartedu_http_request_duration_seconds",
            "HTTP request duration.",
            ["service", "method", "route"],
            buckets=(
                0.005,
                0.01,
                0.025,
                0.05,
                0.1,
                0.25,
                0.5,
                1,
                2,
                3,
                5,
                10,
                30,
            ),
            registry=self.registry,
        )
        self.http_inflight = Gauge(
            "smartedu_http_inflight_requests",
            "Currently in-flight HTTP requests.",
            ["service"],
            registry=self.registry,
        )

        self.dependency_requests = Counter(
            "smartedu_dependency_requests_total",
            "Outbound dependency requests.",
            ["service", "dependency", "operation", "outcome"],
            registry=self.registry,
        )
        self.dependency_duration = Histogram(
            "smartedu_dependency_request_duration_seconds",
            "Outbound dependency request duration.",
            ["service", "dependency", "operation"],
            buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10),
            registry=self.registry,
        )

        self.outbox_pending = Gauge(
            "smartedu_outbox_pending",
            "Pending transactional outbox events.",
            ["service"],
            registry=self.registry,
        )
        self.outbox_oldest_age = Gauge(
            "smartedu_outbox_oldest_age_seconds",
            "Age of oldest pending outbox event.",
            ["service"],
            registry=self.registry,
        )
        self.event_processed = Counter(
            "smartedu_events_processed_total",
            "Consumed events by type and outcome.",
            ["service", "event_type", "outcome"],
            registry=self.registry,
        )
        self.event_lag = Histogram(
            "smartedu_event_processing_lag_seconds",
            "Delay between event occurred_at and processing.",
            ["service", "event_type"],
            buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 30, 60, 300),
            registry=self.registry,
        )
        self.worker_queue_depth = Gauge(
            "smartedu_worker_queue_depth",
            "Observed background-work queue depth.",
            ["service", "queue"],
            registry=self.registry,
        )
        self.worker_failures = Counter(
            "smartedu_worker_failures_total",
            "Background worker failures.",
            ["service", "worker", "reason"],
            registry=self.registry,
        )

        self.db_pool_checked_out = Gauge(
            "smartedu_db_pool_checked_out",
            "Checked-out SQLAlchemy pool connections.",
            ["service", "database"],
            registry=self.registry,
        )
        self.db_pool_checkout_failures = Counter(
            "smartedu_db_pool_checkout_failures_total",
            "Database pool checkout failures.",
            ["service", "database"],
            registry=self.registry,
        )

        self.service_name = service_name

    def exposition(self) -> bytes:
        return generate_latest(self.registry)

    def set_outbox(
        self,
        *,
        pending: int,
        oldest_created_at: datetime | None,
    ) -> None:
        self.outbox_pending.labels(self.service_name).set(max(0, pending))
        age = 0.0
        if oldest_created_at is not None:
            if oldest_created_at.tzinfo is None:
                oldest_created_at = oldest_created_at.replace(tzinfo=UTC)
            age = max(
                0.0,
                (datetime.now(UTC) - oldest_created_at).total_seconds(),
            )
        self.outbox_oldest_age.labels(self.service_name).set(age)

    def observe_event(
        self,
        *,
        event_type: str,
        outcome: str,
        occurred_at: datetime | None = None,
    ) -> None:
        self.event_processed.labels(
            self.service_name,
            event_type,
            outcome,
        ).inc()
        if occurred_at is not None:
            if occurred_at.tzinfo is None:
                occurred_at = occurred_at.replace(tzinfo=UTC)
            lag = max(
                0.0,
                (datetime.now(UTC) - occurred_at).total_seconds(),
            )
            self.event_lag.labels(
                self.service_name,
                event_type,
            ).observe(lag)

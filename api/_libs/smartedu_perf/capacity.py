from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConnectionBudget:
    service: str
    replicas: int
    pool_size: int
    max_overflow: int

    @property
    def steady_connections(self) -> int:
        return self.replicas * self.pool_size

    @property
    def burst_connections(self) -> int:
        return self.replicas * (self.pool_size + self.max_overflow)


def total_connection_budget(
    budgets: list[ConnectionBudget],
) -> tuple[int, int]:
    steady = sum(item.steady_connections for item in budgets)
    burst = sum(item.burst_connections for item in budgets)
    return steady, burst


def little_law_concurrency(
    *,
    throughput_per_second: float,
    response_time_seconds: float,
) -> float:
    if throughput_per_second < 0:
        raise ValueError("throughput_per_second cannot be negative")
    if response_time_seconds < 0:
        raise ValueError("response_time_seconds cannot be negative")
    return throughput_per_second * response_time_seconds


def estimated_rps(
    *,
    users: int,
    average_think_time_seconds: float,
    average_response_time_seconds: float,
) -> float:
    if users < 0:
        raise ValueError("users cannot be negative")
    cycle = average_think_time_seconds + average_response_time_seconds
    if cycle <= 0:
        raise ValueError("combined think + response time must be positive")
    return users / cycle

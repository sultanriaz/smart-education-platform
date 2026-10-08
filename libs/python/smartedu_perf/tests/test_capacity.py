import pytest

from smartedu_perf import (
    ConnectionBudget,
    estimated_rps,
    little_law_concurrency,
    total_connection_budget,
)


def test_connection_budget_totals_replicas_and_overflow():
    budgets = [
        ConnectionBudget("academic", replicas=3, pool_size=10, max_overflow=5),
        ConnectionBudget("attendance", replicas=2, pool_size=8, max_overflow=4),
    ]
    steady, burst = total_connection_budget(budgets)
    assert steady == 46
    assert burst == 69


def test_little_law_and_estimated_rps():
    assert (
        little_law_concurrency(
            throughput_per_second=100,
            response_time_seconds=0.5,
        )
        == 50
    )
    assert (
        estimated_rps(
            users=500,
            average_think_time_seconds=4.0,
            average_response_time_seconds=1.0,
        )
        == 100
    )


def test_estimated_rps_rejects_zero_cycle():
    with pytest.raises(ValueError):
        estimated_rps(
            users=1,
            average_think_time_seconds=0,
            average_response_time_seconds=0,
        )

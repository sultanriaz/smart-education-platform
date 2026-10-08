from smartedu_perf import EndpointResult, MetricBudget, evaluate_budget


def test_budget_passes_when_p95_errors_and_rps_are_inside_limits():
    result = EndpointResult(
        name="attendance.mark",
        requests=1000,
        failures=2,
        p50_ms=400,
        p95_ms=1200,
        p99_ms=1800,
        avg_ms=520,
        rps=40,
    )
    budget = MetricBudget(
        name="attendance.mark",
        p95_ms=2000,
        max_error_rate=0.01,
        min_rps=25,
    )

    evaluation = evaluate_budget(result, budget)
    assert evaluation.passed
    assert evaluation.reasons == []


def test_budget_reports_all_regressions():
    result = EndpointResult(
        name="page",
        requests=100,
        failures=5,
        p50_ms=1200,
        p95_ms=3500,
        p99_ms=5000,
        avg_ms=1800,
        rps=5,
    )
    budget = MetricBudget(
        name="page",
        p95_ms=3000,
        max_error_rate=0.01,
        min_rps=10,
    )

    evaluation = evaluate_budget(result, budget)
    assert not evaluation.passed
    assert len(evaluation.reasons) == 3

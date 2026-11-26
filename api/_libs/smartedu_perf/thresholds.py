from __future__ import annotations

from .models import BudgetEvaluation, EndpointResult, MetricBudget


def evaluate_budget(
    result: EndpointResult,
    budget: MetricBudget,
) -> BudgetEvaluation:
    reasons: list[str] = []

    if result.p95_ms > budget.p95_ms:
        reasons.append(f"p95 {result.p95_ms:.1f}ms exceeds budget {budget.p95_ms}ms")

    if result.error_rate > budget.max_error_rate:
        reasons.append(f"error rate {result.error_rate:.2%} exceeds {budget.max_error_rate:.2%}")

    if budget.min_rps is not None and result.rps < budget.min_rps:
        reasons.append(f"throughput {result.rps:.2f} rps below minimum {budget.min_rps:.2f}")

    return BudgetEvaluation(
        name=budget.name,
        passed=not reasons,
        reasons=reasons,
    )

from datetime import UTC, datetime

import pytest

from smartedu_readiness import Approval, CheckResult, ReadinessRisk


def test_waived_check_requires_waiver_id():
    with pytest.raises(ValueError):
        CheckResult(
            check_id="PR-X-001",
            status="WAIVED",
            verified_by="tester",
            verified_at=datetime.now(UTC),
        )


def test_conditional_approval_requires_condition():
    with pytest.raises(ValueError):
        Approval(
            role="ProductOwner",
            approver="tester",
            decision="APPROVE_WITH_CONDITIONS",
            approved_at=datetime.now(UTC),
        )


def test_accepted_risk_requires_reason():
    with pytest.raises(ValueError):
        ReadinessRisk(
            id="R-1",
            title="Known issue",
            severity="MEDIUM",
            status="ACCEPTED",
            owner="owner",
            mitigation="Monitor",
        )

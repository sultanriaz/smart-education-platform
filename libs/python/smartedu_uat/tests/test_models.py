from datetime import UTC, datetime

import pytest

from smartedu_uat import ScenarioResult


def test_waived_result_requires_waiver_id():
    with pytest.raises(ValueError):
        ScenarioResult(
            scenario_id="UAT-X-001",
            status="WAIVED",
            executed_by="tester",
            executed_at=datetime.now(UTC),
        )


def test_pass_result_does_not_require_waiver():
    result = ScenarioResult(
        scenario_id="UAT-X-001",
        status="PASS",
        executed_by="tester",
        executed_at=datetime.now(UTC),
    )
    assert result.status == "PASS"


def test_conditional_signoff_requires_condition():
    from smartedu_uat import Signoff

    with pytest.raises(ValueError):
        Signoff(
            role="ProductOwner",
            signer="tester",
            decision="APPROVE_WITH_CONDITIONS",
            signed_at=datetime.now(UTC),
        )

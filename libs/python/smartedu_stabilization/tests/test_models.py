from datetime import UTC, datetime

import pytest

from smartedu_stabilization import (
    CheckpointResult,
    StabilizationApproval,
    StabilizationIssue,
)


def test_warn_checkpoint_requires_notes():
    with pytest.raises(ValueError):
        CheckpointResult(
            checkpoint_id="STAB-X-001",
            status="WARN",
            observed_by="tester",
            observed_at=datetime.now(UTC),
        )


def test_closed_issue_requires_closed_at():
    with pytest.raises(ValueError):
        StabilizationIssue(
            id="ISS-1",
            severity="SEV3",
            title="Issue",
            status="CLOSED",
            owner="owner",
            opened_at=datetime.now(UTC),
        )


def test_conditional_approval_requires_followup_condition():
    with pytest.raises(ValueError):
        StabilizationApproval(
            role="ProductOwner",
            approver="tester",
            approved_at=datetime.now(UTC),
            decision="APPROVE_WITH_FOLLOWUPS",
        )

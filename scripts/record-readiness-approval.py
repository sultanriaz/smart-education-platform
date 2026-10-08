from __future__ import annotations

import argparse
from datetime import datetime, timezone

from smartedu_readiness import Approval, load_run, save_run


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run")
    parser.add_argument(
        "--role",
        required=True,
        choices=[
            "TechnicalLead",
            "OperationsOwner",
            "SecurityOwner",
            "ProductOwner",
            "ProjectSupervisor",
        ],
    )
    parser.add_argument("--approver", required=True)
    parser.add_argument(
        "--decision",
        required=True,
        choices=["APPROVE", "APPROVE_WITH_CONDITIONS", "REJECT"],
    )
    parser.add_argument("--condition", action="append", default=[])
    args = parser.parse_args()

    approval = Approval(
        role=args.role,
        approver=args.approver,
        decision=args.decision,
        approved_at=datetime.now(timezone.utc),
        conditions=args.condition,
    )
    run = load_run(args.run)
    run.approvals = [item for item in run.approvals if item.role != args.role]
    run.approvals.append(approval)
    run.approvals.sort(key=lambda item: item.role)
    save_run(run, args.run)
    print(f"{args.role}={args.decision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

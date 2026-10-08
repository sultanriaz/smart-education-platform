from __future__ import annotations

import argparse
from datetime import datetime, timezone

from smartedu_uat import Signoff, load_run, save_run


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run")
    parser.add_argument(
        "--role",
        required=True,
        choices=[
            "StudentRepresentative",
            "TeacherRepresentative",
            "AdminRepresentative",
            "ProductOwner",
            "ProjectSupervisor",
        ],
    )
    parser.add_argument("--signer", required=True)
    parser.add_argument(
        "--decision",
        required=True,
        choices=["APPROVE", "APPROVE_WITH_CONDITIONS", "REJECT"],
    )
    parser.add_argument("--condition", action="append", default=[])
    args = parser.parse_args()

    run = load_run(args.run)
    signoff = Signoff(
        role=args.role,
        signer=args.signer,
        decision=args.decision,
        signed_at=datetime.now(timezone.utc),
        conditions=args.condition,
    )

    run.signoffs = [
        item for item in run.signoffs if item.role != args.role
    ]
    run.signoffs.append(signoff)
    run.signoffs.sort(key=lambda item: item.role)
    save_run(run, args.run)
    print(f"{args.role}={args.decision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

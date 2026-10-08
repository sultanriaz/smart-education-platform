from __future__ import annotations

import argparse
from datetime import datetime

from smartedu_readiness import ReadinessRisk, load_run, save_run


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run")
    parser.add_argument("risk_id")
    parser.add_argument("--title", required=True)
    parser.add_argument(
        "--severity",
        required=True,
        choices=["BLOCKER", "CRITICAL", "HIGH", "MEDIUM", "LOW"],
    )
    parser.add_argument(
        "--status",
        default="OPEN",
        choices=["OPEN", "MITIGATING", "ACCEPTED", "CLOSED"],
    )
    parser.add_argument("--owner", required=True)
    parser.add_argument("--mitigation", required=True)
    parser.add_argument("--due-at")
    parser.add_argument("--acceptance-reason")
    args = parser.parse_args()

    risk = ReadinessRisk(
        id=args.risk_id,
        title=args.title,
        severity=args.severity,
        status=args.status,
        owner=args.owner,
        mitigation=args.mitigation,
        due_at=datetime.fromisoformat(args.due_at) if args.due_at else None,
        acceptance_reason=args.acceptance_reason,
    )

    run = load_run(args.run)
    run.risks = [item for item in run.risks if item.id != args.risk_id]
    run.risks.append(risk)
    run.risks.sort(key=lambda item: item.id)
    save_run(run, args.run)
    print(f"{args.risk_id}={args.status}/{args.severity}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

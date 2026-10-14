"""B13 backfill/reconciliation for schedules predating Facility synchronization.

Default is dry-run. --apply writes ONLY Facility Service external reservations;
Scheduling rows, Docker volumes, and event tables are not modified.
"""
from __future__ import annotations

import argparse
import sys

from sqlalchemy import select

from app.clients.facility import FacilityClient
from app.db.session import SessionLocal
from app.domain.models import ScheduleEntry
from app.services.scheduling_service import SchedulingService


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Actually reconcile; otherwise dry-run")
    parser.add_argument("--max-schedules", type=int, default=500, help="Safety cap")
    args = parser.parse_args()
    if args.max_schedules < 1 or args.max_schedules > 10000:
        parser.error("--max-schedules must be between 1 and 10000")

    with SessionLocal() as db:
        # Canceled schedules also need to release any historical reservation state.
        schedules = list(db.scalars(select(ScheduleEntry).order_by(ScheduleEntry.created_at).limit(args.max_schedules + 1)).all())
        if len(schedules) > args.max_schedules:
            print("ABORT: More schedules than the --max-schedules safety cap. No writes made.")
            return 2
        service = SchedulingService(db, academic=None, facility=FacilityClient())  # type: ignore[arg-type]
        pending = []
        try:
            for row in schedules:
                desired = service._desired_reservations(row)
                pending.append((row.id, row.status, desired))
        except Exception as exc:
            print(f"ABORT: Could not calculate desired reservations: {type(exc).__name__}: {exc}")
            return 2
        print(f"Mode: {'APPLY' if args.apply else 'DRY RUN'}; schedules: {len(pending)}; "
              f"occurrences: {sum(len(item[2]) for item in pending)}")
        if not args.apply:
            print("No Facility writes performed. Re-run with --apply after reviewing counts.")
            return 0
        failed = []
        for schedule_id, status, desired in pending:
            try:
                service.facility.replace_schedule(schedule_id, desired)
                print(f"OK schedule={schedule_id} status={status} active={len(desired)}")
            except Exception as exc:
                print(f"FAILED schedule={schedule_id}: {type(exc).__name__}: {exc}")
                failed.append(str(schedule_id))
        print(f"Complete: {len(pending) - len(failed)} synchronized, {len(failed)} failed")
        if failed:
            print("WARNING: Do not declare B13 fully backfilled until every failure is resolved.")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

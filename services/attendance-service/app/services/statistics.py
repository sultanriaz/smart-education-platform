from __future__ import annotations

from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal

from app.domain.models import AttendanceStatus
from app.schemas.attendance import AttendanceSummary, Counts


def calculate_counts(rows: list[dict], threshold: float) -> Counts:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        counts[row["status"]] += row["count"]
    present = counts[AttendanceStatus.PRESENT]
    absent = counts[AttendanceStatus.ABSENT]
    late = counts[AttendanceStatus.LATE]
    excused = counts[AttendanceStatus.EXCUSED]
    considered = present + absent + late
    exact = Decimal(present + late) * 100 / considered if considered else None
    return Counts(
        present_sessions=present,
        absent_sessions=absent,
        late_sessions=late,
        excused_sessions=excused,
        total_considered_sessions=considered,
        attendance_percentage=float(exact.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
        if exact is not None
        else None,
        is_low_attendance=exact is not None and exact < Decimal(str(threshold)),
    )


def grouped_summaries(
    rows: list[dict], group_by: tuple[str, ...], threshold: float
) -> list[AttendanceSummary]:
    groups = defaultdict(list)
    for row in rows:
        groups[tuple(row[key] for key in group_by)].append(row)
    return [
        AttendanceSummary(
            **dict(zip(group_by, key, strict=True)),
            **calculate_counts(groups[key], threshold).model_dump(),
        )
        for key in sorted(groups)
    ]

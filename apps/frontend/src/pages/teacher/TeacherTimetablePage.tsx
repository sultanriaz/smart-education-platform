import { PageHeader } from "../../components/ui/PageHeader";
import { TimetableHub } from "../../components/timetable/TimetableHub";

export function TeacherTimetablePage() {
  return (
    <div className="page-container space-y-6">
      <PageHeader
        eyebrow="Faculty Teaching Timetable"
        title="Lecture Schedule & Room Allocations"
        description="Assigned teaching periods, room capacity, swap alerts, and 1-click digital attendance launch."
      />

      <TimetableHub initialRole="teacher" />
    </div>
  );
}

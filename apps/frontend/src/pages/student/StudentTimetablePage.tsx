import { PageHeader } from "../../components/ui/PageHeader";
import { TimetableHub } from "../../components/timetable/TimetableHub";

export function StudentTimetablePage() {
  return (
    <div className="page-container space-y-6">
      <PageHeader
        eyebrow="Student Academic Timetable"
        title="Class Schedule & Slot Timeline"
        description="Day timeline with live time tracking, weekly master matrix, room locator, swap alerts, and calendar export."
      />

      <TimetableHub initialRole="student" />
    </div>
  );
}

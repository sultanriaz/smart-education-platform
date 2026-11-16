import { PageHeader } from "../../components/ui/PageHeader";
import { IntelligentTimetableEngine } from "../../components/timetable/IntelligentTimetableEngine";
import { STUDENT_SCHEDULE } from "../../features/timetable/timetable-engine";
import { useTimetable } from "../../features/student/hooks";

export function StudentTimetablePage() {
  const timetable = useTimetable();

  return (
    <div className="page-container space-y-6">
      <PageHeader
        eyebrow="Student Academic Timetable"
        title="Class Schedule & Slot Timeline"
        description="Day timeline with live time tracking, weekly master matrix, room locator, swap alerts, and calendar export."
      />

      <IntelligentTimetableEngine
        schedule={STUDENT_SCHEDULE}
        mode="student"
        title="Student Weekly Lecture Engine"
        description="Hour-by-hour visual schedule with moving current time indicator, room blueprints, and 1-click .ics export."
      />
    </div>
  );
}

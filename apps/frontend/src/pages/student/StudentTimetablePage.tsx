import { PageHeader } from "../../components/ui/PageHeader";
import { TimetableHub } from "../../components/timetable/TimetableHub";

export function StudentTimetablePage() {
  return (
    <div className="page-container space-y-6">
      <PageHeader
        eyebrow="Student Timetable"
        title="Weekly Class Schedule"
        description="See your weekly classes, lecture times, teachers, classrooms, and open seats."
      />

      <TimetableHub initialRole="student" signedInRole="student" />
    </div>
  );
}

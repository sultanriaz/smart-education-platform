import { PageHeader } from "../../components/ui/PageHeader";
import { TimetableHub } from "../../components/timetable/TimetableHub";

export function TeacherTimetablePage() {
  return (
    <div className="page-container space-y-6">
      <PageHeader
        eyebrow="Teacher Timetable"
        title="Teaching Schedule & Rooms"
        description="See your weekly classes, sections, classrooms, and any room changes."
      />

      <TimetableHub initialRole="teacher" signedInRole="teacher" />
    </div>
  );
}

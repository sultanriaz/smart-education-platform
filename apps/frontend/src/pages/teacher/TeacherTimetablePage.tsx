import { PageHeader } from "../../components/ui/PageHeader";
import { IntelligentTimetableEngine } from "../../components/timetable/IntelligentTimetableEngine";
import { TEACHER_SCHEDULE } from "../../features/timetable/timetable-engine";
import { useTeacherTimetable } from "../../features/teacher/hooks";

export function TeacherTimetablePage() {
  const timetable = useTeacherTimetable();

  return (
    <div className="page-container space-y-6">
      <PageHeader
        eyebrow="Faculty Teaching Timetable"
        title="Lecture Schedule & Room Allocations"
        description="Assigned teaching periods, room capacity, swap alerts, and 1-click digital attendance launch."
      />

      <IntelligentTimetableEngine
        schedule={TEACHER_SCHEDULE}
        mode="teacher"
        title="Dr. Munir Ahmad · Weekly Lecture Timetable"
        description="Assigned courses: Compiler Construction (BCS-7C, BCS-7A) & Advanced Compilers (MCS-2A)."
      />
    </div>
  );
}

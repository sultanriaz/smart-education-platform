import { ChevronRight, UserCheck } from "lucide-react";
import { Link } from "react-router-dom";
import { StudentPortalHeader } from "../../components/student/StudentPortalHeader";
import { COURSES_CATALOG } from "../../features/student/courses-data";

interface CourseAccentTheme {
  topBar: string;
  codePill: string;
  creditBadge: string;
}

const DEFAULT_ACCENT_THEME: CourseAccentTheme = {
  topBar: "bg-primary",
  codePill: "bg-primary-soft text-primary-ink",
  creditBadge: "bg-primary-soft text-primary-ink",
};

const COURSE_ACCENT_THEMES: CourseAccentTheme[] = [
  DEFAULT_ACCENT_THEME,
  {
    topBar: "bg-secondary",
    codePill: "bg-secondary-soft text-secondary-ink",
    creditBadge: "bg-secondary-soft text-secondary-ink",
  },
  {
    topBar: "bg-accent",
    codePill: "bg-accent-soft text-accent-ink",
    creditBadge: "bg-accent-soft text-accent-ink",
  },
  {
    topBar: "bg-success",
    codePill: "bg-success-soft text-success-ink",
    creditBadge: "bg-success-soft text-success-ink",
  },
  {
    topBar: "bg-warning",
    codePill: "bg-warning-soft text-warning-ink",
    creditBadge: "bg-warning-soft text-warning-ink",
  },
  {
    topBar: "bg-danger",
    codePill: "bg-danger-soft text-danger-ink",
    creditBadge: "bg-danger-soft text-danger-ink",
  },
];

function getAttendanceTone(percentage: number): { text: string; bar: string } {
  if (percentage < 75) {
    return { text: "text-danger-ink", bar: "bg-danger" };
  }
  if (percentage < 82) {
    return { text: "text-warning-ink", bar: "bg-warning" };
  }
  return { text: "text-success-ink", bar: "bg-success" };
}

/**
 * Student Portal landing dashboard showing the curved student header and
 * only the minimal registered course cards requested in the redesign spec.
 */
export function StudentDashboardPage() {
  return (
    <div className="mx-auto w-full max-w-5xl space-y-6 pb-8 sm:px-4 sm:pt-4">
      <StudentPortalHeader />

      <section aria-labelledby="registered-courses-heading" className="px-4 sm:px-0">
        <div className="mb-4 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <span className="h-5 w-1 rounded-full bg-primary" aria-hidden="true" />
            <h2
              id="registered-courses-heading"
              className="text-xs font-bold tracking-wider text-ink uppercase sm:text-sm"
            >
              REGISTERED COURSES
            </h2>
          </div>

          <span className="rounded-full border border-line bg-panel px-3 py-1 text-xs font-semibold text-muted">
            {COURSES_CATALOG.length} courses
          </span>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {COURSES_CATALOG.map((course, index) => {
            const accent =
              COURSE_ACCENT_THEMES[index % COURSE_ACCENT_THEMES.length] ??
              DEFAULT_ACCENT_THEME;
            const attendanceTone = getAttendanceTone(course.attendance.percentage);
            const compactCode = course.code.replace(/\s+/g, "");

            return (
              <Link
                key={course.id}
                to={`/app/student/courses/${course.id}`}
                aria-label={`${course.title} (${compactCode})`}
                className="group relative flex flex-col overflow-hidden rounded-2xl border border-line bg-panel shadow-sm transition hover:-translate-y-0.5 hover:border-primary/40 hover:shadow-md"
              >
                <div className={`h-1.5 w-full ${accent.topBar}`} aria-hidden="true" />

                <div className="flex flex-1 flex-col gap-3.5 p-5">
                  <div className="flex items-center justify-between gap-2">
                    <span
                      className={`inline-flex items-center rounded-lg px-2.5 py-1 text-xs font-bold tracking-wide ${accent.codePill}`}
                    >
                      {compactCode}
                    </span>

                    <span
                      className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-subtle text-muted transition group-hover:bg-primary-soft group-hover:text-primary-ink"
                      aria-hidden="true"
                    >
                      <ChevronRight className="h-4 w-4" />
                    </span>
                  </div>

                  <div>
                    <h3 className="text-base font-bold leading-snug text-ink sm:text-lg">
                      {course.title}
                    </h3>
                  </div>

                  <div className="flex flex-wrap items-center gap-3">
                    <div className="inline-flex items-center gap-2">
                      <span
                        className={`inline-flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold ${accent.creditBadge}`}
                      >
                        {course.creditHours}
                      </span>
                      <span className="text-xs font-semibold text-muted">Credits</span>
                    </div>

                    <span className="rounded-lg border border-line bg-subtle px-2.5 py-1 text-xs font-semibold text-ink">
                      {course.section}
                    </span>
                  </div>

                  <div className="flex items-center gap-2 text-xs font-medium text-muted">
                    <UserCheck className="h-4 w-4 shrink-0 text-primary-ink" aria-hidden="true" />
                    <span className="truncate text-ink">{course.teacher.name}</span>
                  </div>

                  <div className="mt-auto space-y-1.5 border-t border-line pt-3">
                    <div className="flex items-center justify-between text-xs font-semibold">
                      <span className="text-muted">Attendance summary</span>
                      <span className={attendanceTone.text}>
                        {course.attendance.percentage}%
                      </span>
                    </div>
                    <div
                      className="h-1.5 w-full overflow-hidden rounded-full bg-subtle"
                      role="progressbar"
                      aria-valuenow={course.attendance.percentage}
                      aria-valuemin={0}
                      aria-valuemax={100}
                      aria-label={`${course.title} attendance ${course.attendance.percentage}%`}
                    >
                      <div
                        className={`h-full rounded-full transition-all ${attendanceTone.bar}`}
                        style={{ width: `${course.attendance.percentage}%` }}
                      />
                    </div>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      </section>
    </div>
  );
}

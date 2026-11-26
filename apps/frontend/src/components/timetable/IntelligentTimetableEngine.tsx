import { useEffect } from "react";
import { Link } from "react-router-dom";
import {
  CalendarDays,
  Clock,
  MapPin,
  Users,
  AlertTriangle,
  Building,
  X,
  ArrowRight,
  CheckCircle2,
  UserCheck,
  GraduationCap
} from "lucide-react";

import {
  type TimetableSlot,
  STANDARD_PERIODS,
  getStudentCourseSlug
} from "../../features/timetable/timetable-engine";

const WEEKDAYS: Array<TimetableSlot["day"]> = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday"
];

interface TableViewProps {
  schedule: TimetableSlot[];
  mode: "student" | "teacher";
  onSelectSlot: (slot: TimetableSlot) => void;
}

/** Plain-English weekly table showing Slots 1-5 across Monday to Friday. */
export function TimetableTableView({ schedule, mode, onSelectSlot }: TableViewProps) {
  return (
    <div className="rounded-2xl border border-line bg-panel p-4 sm:p-5 shadow-2xs space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h3 className="font-bold text-base text-ink">Weekly Class Table</h3>
          <p className="text-xs text-muted">
            Click any class box to see full room and teacher details. Empty spaces mean no class.
          </p>
        </div>
        <p className="text-xs font-medium text-muted sm:hidden">
          Swipe sideways to see all days →
        </p>
      </div>

      <div className="overflow-x-auto rounded-xl border border-line">
        <table className="w-full text-xs text-left border-collapse">
          <thead className="bg-subtle text-muted font-bold border-b border-line">
            <tr>
              <th className="sticky left-0 z-10 bg-subtle p-3 min-w-[152px] border-r border-line text-ink">
                Class Time
              </th>
              {WEEKDAYS.map((day) => (
                <th key={day} className="p-3 min-w-[165px] font-bold text-ink">
                  {day}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {STANDARD_PERIODS.map((period) => (
              <tr key={period.slot} className="hover:bg-subtle/20">
                <td className="sticky left-0 z-10 bg-panel p-3 border-r border-line align-top">
                  <p className="font-bold text-ink">{period.label}</p>
                  <p className="text-2xs text-muted whitespace-nowrap mt-0.5">{period.time}</p>
                </td>

                {WEEKDAYS.map((day) => {
                  const matches = schedule.filter(
                    (s) => s.day === day && s.slotNumber === period.slot
                  );

                  if (matches.length === 0) {
                    return (
                      <td
                        key={day}
                        className="p-3 text-muted/60 italic border-r border-line/50 last:border-r-0 align-middle"
                      >
                        Free
                      </td>
                    );
                  }

                  return (
                    <td
                      key={day}
                      className="p-2 border-r border-line/50 last:border-r-0 align-top space-y-2"
                    >
                      {matches.map((match) => (
                        <button
                          key={match.id}
                          type="button"
                          onClick={() => onSelectSlot(match)}
                          className={`w-full text-left cursor-pointer rounded-xl border ${match.colorScheme.border} ${match.colorScheme.bg} p-2.5 space-y-1 hover:shadow-sm transition focus-visible:outline-2`}
                        >
                          <div className="flex items-center justify-between gap-1">
                            <span
                              className={`inline-block text-2xs font-bold px-1.5 py-0.5 rounded-md ${match.colorScheme.badge}`}
                            >
                              {match.courseCode}
                            </span>
                            {match.swapAlert && (
                              <span className="rounded-full bg-warning-soft px-1.5 py-0.5 text-[10px] font-bold text-warning-ink">
                                Room Changed
                              </span>
                            )}
                          </div>
                          <p className="font-bold text-xs text-ink leading-snug">
                            {match.courseTitle}
                          </p>
                          <p className="text-2xs text-muted">
                            {match.room} · {match.block}
                          </p>
                          <p className="text-2xs font-semibold text-primary-ink">
                            {mode === "student"
                              ? match.instructorName
                              : `${match.section} · ${match.enrolledStudents}/${match.capacity} seats`}
                          </p>
                        </button>
                      ))}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

interface ModalProps {
  slot: TimetableSlot | null;
  mode: "student" | "teacher";
  signedInRole?: "student" | "teacher" | null;
  onClose: () => void;
}

/** Accessible details popup for any selected class slot. */
export function TimetableSlotModal({ slot, mode, signedInRole = null, onClose }: ModalProps) {
  useEffect(() => {
    if (!slot) return;
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [slot, onClose]);

  if (!slot) return null;

  const seatPercent = Math.min(Math.round((slot.enrolledStudents / slot.capacity) * 100), 100);
  const floorGuide = slot.floor.toLowerCase().includes("ground")
    ? `Located on the Ground Floor inside ${slot.block} — easy access from the main entrance.`
    : `Located inside ${slot.block} on the ${slot.floor}. Take the stairs or lift inside the block.`;
  const studentCourseSlug = getStudentCourseSlug(slot.courseCode);

  const googleTitle = encodeURIComponent(`${slot.courseCode}: ${slot.courseTitle} (${slot.section})`);
  const googleDetails = encodeURIComponent(
    `Teacher: ${slot.instructorName}\nRoom: ${slot.room} (${slot.block}, ${slot.floor})`
  );
  const googleLocation = encodeURIComponent(`${slot.room}, ${slot.block}, COMSATS Sahiwal`);
  const googleCalendarUrl = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${googleTitle}&details=${googleDetails}&location=${googleLocation}`;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="timetable-slot-modal-title"
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-overlay/65 p-0 sm:p-4 backdrop-blur-xs"
      onClick={onClose}
    >
      <div
        className="w-full max-w-lg rounded-t-3xl sm:rounded-3xl border border-line bg-panel p-5 sm:p-6 text-ink shadow-2xl space-y-4"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mx-auto -mt-1 mb-1 h-1.5 w-12 rounded-full bg-subtle sm:hidden" />

        <div className="flex items-start justify-between gap-3 border-b border-line pb-3">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <span className={`rounded-md px-2 py-0.5 text-2xs font-bold ${slot.colorScheme.badge}`}>
                {slot.courseCode}
              </span>
              <span className="text-xs font-semibold text-muted">
                {slot.day} · Slot {slot.slotNumber} ({slot.timeRange})
              </span>
              {slot.swapAlert && (
                <span className="rounded-full bg-warning-soft px-2 py-0.5 text-2xs font-bold text-warning-ink">
                  Room Changed
                </span>
              )}
            </div>
            <h3 id="timetable-slot-modal-title" className="font-bold text-lg text-ink mt-1">
              {slot.courseTitle}
            </h3>
          </div>

          <button
            type="button"
            onClick={onClose}
            aria-label="Close class details"
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-subtle text-muted hover:text-ink transition"
          >
            <X size={16} />
          </button>
        </div>

        {slot.swapAlert && (
          <div className="rounded-xl border border-warning/35 bg-warning-soft p-3 text-xs text-warning-ink flex items-start gap-2">
            <AlertTriangle size={16} className="shrink-0 mt-0.5" />
            <div>
              <p className="font-bold">Room Change Notice</p>
              <p className="mt-0.5">{slot.swapAlert.message}</p>
            </div>
          </div>
        )}

        {/* Location & Seats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          <div className="rounded-2xl border border-line bg-surface p-3.5 space-y-1">
            <div className="flex items-center gap-1.5 font-bold text-primary-ink">
              <MapPin size={14} />
              <span>Classroom Location</span>
            </div>
            <p className="font-bold text-sm text-ink">{slot.room}</p>
            <p className="text-muted">
              {slot.block} · {slot.floor}
            </p>
          </div>

          <div className="rounded-2xl border border-line bg-surface p-3.5 space-y-1.5">
            <div className="flex items-center justify-between gap-2 font-bold text-primary-ink">
              <span className="inline-flex items-center gap-1.5">
                <Users size={14} />
                <span>Class Seats</span>
              </span>
              <span className="text-ink">
                {slot.enrolledStudents} / {slot.capacity}
              </span>
            </div>
            <div className="h-2 w-full rounded-full bg-subtle overflow-hidden">
              <div
                className={`h-full rounded-full ${seatPercent >= 90 ? "bg-warning" : "bg-success"}`}
                style={{ width: `${seatPercent}%` }}
              />
            </div>
            <p className="text-muted">
              {slot.capacity} total seats · {slot.enrolledStudents} students
            </p>
          </div>
        </div>

        {/* Teacher, Class & Simple Directions */}
        <div className="rounded-2xl border border-line bg-subtle/40 p-4 space-y-2 text-xs">
          <p className="flex items-center gap-2 text-ink">
            <UserCheck size={14} className="text-primary-ink shrink-0" />
            <span>
              <strong>Teacher:</strong> {slot.instructorName}{" "}
              <span className="text-muted">({slot.instructorOffice})</span>
            </span>
          </p>
          <p className="flex items-center gap-2 text-ink">
            <GraduationCap size={14} className="text-secondary-ink shrink-0" />
            <span>
              <strong>Class / Section:</strong> {slot.section}
            </span>
          </p>
          <p className="flex items-start gap-2 text-muted pt-1 border-t border-line/60">
            <Building size={14} className="text-primary-ink shrink-0 mt-0.5" />
            <span>{floorGuide}</span>
          </p>
        </div>

        {/* Simple Helpful Actions */}
        <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
          <div className="flex flex-wrap items-center gap-2">
            <a
              href={googleCalendarUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 rounded-xl border border-line bg-surface px-3 py-2 text-xs font-semibold text-ink hover:border-primary transition"
            >
              <CalendarDays size={14} className="text-primary-ink" />
              <span>Add to Google Calendar</span>
            </a>

            <Link
              to="/explore?tab=hub"
              onClick={onClose}
              className="inline-flex items-center gap-1.5 rounded-xl border border-line bg-surface px-3 py-2 text-xs font-semibold text-ink hover:border-primary transition"
            >
              <Building size={14} className="text-secondary-ink" />
              <span>Find Rooms &amp; Offices</span>
            </Link>

            {signedInRole === "student" && studentCourseSlug && (
              <Link
                to={`/app/student/courses/${studentCourseSlug}`}
                onClick={onClose}
                className="inline-flex items-center gap-1.5 rounded-xl border border-primary/40 bg-primary-soft px-3 py-2 text-xs font-bold text-primary-ink hover:bg-primary hover:text-on-primary transition"
              >
                <span>Open Subject</span>
                <ArrowRight size={13} />
              </Link>
            )}

            {signedInRole === "teacher" && mode === "teacher" && (
              <Link
                to="/app/teacher/attendance"
                onClick={onClose}
                className="inline-flex items-center gap-1.5 rounded-xl bg-success px-3 py-2 text-xs font-bold text-success-fg hover:opacity-90 transition"
              >
                <CheckCircle2 size={13} />
                <span>Mark Attendance</span>
              </Link>
            )}
          </div>

          <button
            type="button"
            onClick={onClose}
            className="rounded-xl bg-primary px-4 py-2 text-xs font-bold text-on-primary hover:bg-primary-hover transition ml-auto"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

/** Kept for compatibility if imported directly elsewhere. */
export function IntelligentTimetableEngine({
  schedule,
  mode
}: {
  schedule: TimetableSlot[];
  mode: "student" | "teacher";
  title?: string;
  description?: string;
}) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-xs text-muted">
        <Clock size={14} />
        <span>Showing {schedule.length} classes for the week</span>
      </div>
      <TimetableTableView schedule={schedule} mode={mode} onSelectSlot={() => {}} />
    </div>
  );
}

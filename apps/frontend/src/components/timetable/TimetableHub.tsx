import { useState } from "react";
import {
  GraduationCap,
  BookOpen,
  Calendar,
  Clock,
  MapPin,
  Users,
  UserCheck,
  Download,
  LayoutGrid,
  List
} from "lucide-react";

import {
  STUDENT_TIMETABLES_BY_SECTION,
  TEACHER_TIMETABLES_BY_NAME,
  downloadICSFile,
  type TimetableSlot
} from "../../features/timetable/timetable-engine";
import { IntelligentTimetableEngine } from "./IntelligentTimetableEngine";

const WEEKDAYS: Array<TimetableSlot["day"]> = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday"
];

export function TimetableHub() {
  const [selectedRole, setSelectedRole] = useState<"student" | "teacher">("student");
  const [selectedSection, setSelectedSection] = useState<string>("BCS-7C");
  const [selectedTeacher, setSelectedTeacher] = useState<string>("Sir Munir (Dr. Munir Ahmad)");
  const [displayStyle, setDisplayStyle] = useState<"weekly_list" | "interactive_engine">("weekly_list");

  const sectionNames = Object.keys(STUDENT_TIMETABLES_BY_SECTION);
  const teacherNames = Object.keys(TEACHER_TIMETABLES_BY_NAME);

  const activeSchedule: TimetableSlot[] =
    selectedRole === "student"
      ? STUDENT_TIMETABLES_BY_SECTION[selectedSection] ?? []
      : TEACHER_TIMETABLES_BY_NAME[selectedTeacher] ?? [];

  const totalWeeklyLectures = activeSchedule.length;

  return (
    <div className="space-y-6">
      {/* ================= TWO MAIN OPTIONS: STUDENT VS TEACHER ================= */}
      <div className="grid gap-4 sm:grid-cols-2">
        <button
          type="button"
          onClick={() => setSelectedRole("student")}
          className={`flex items-center justify-between rounded-2xl border p-5 text-left transition shadow-2xs ${
            selectedRole === "student"
              ? "border-brand-600 bg-panel ring-2 ring-brand-500/30 shadow-sm"
              : "border-line bg-panel hover:border-brand-500/50"
          }`}
        >
          <div className="flex items-center gap-3.5">
            <div
              className={`flex h-12 w-12 items-center justify-center rounded-xl transition ${
                selectedRole === "student"
                  ? "bg-brand-600 text-white"
                  : "bg-brand-500/10 text-brand-600"
              }`}
            >
              <GraduationCap size={24} />
            </div>
            <div>
              <h3 className="font-extrabold text-base text-ink">Student</h3>
              <p className="text-xs text-muted mt-0.5">
                Weekly timetable by class/section with slots, subjects, teachers, classrooms &amp; capacity
              </p>
            </div>
          </div>
          <span
            className={`rounded-full px-3 py-1 text-xs font-bold shrink-0 ${
              selectedRole === "student"
                ? "bg-brand-600 text-white"
                : "bg-surface text-muted border border-line"
            }`}
          >
            {selectedRole === "student" ? "Selected" : "View"}
          </span>
        </button>

        <button
          type="button"
          onClick={() => setSelectedRole("teacher")}
          className={`flex items-center justify-between rounded-2xl border p-5 text-left transition shadow-2xs ${
            selectedRole === "teacher"
              ? "border-indigo-600 bg-panel ring-2 ring-indigo-500/30 shadow-sm"
              : "border-line bg-panel hover:border-indigo-500/50"
          }`}
        >
          <div className="flex items-center gap-3.5">
            <div
              className={`flex h-12 w-12 items-center justify-center rounded-xl transition ${
                selectedRole === "teacher"
                  ? "bg-indigo-600 text-white"
                  : "bg-indigo-500/10 text-indigo-600"
              }`}
            >
              <BookOpen size={24} />
            </div>
            <div>
              <h3 className="font-extrabold text-base text-ink">Teacher</h3>
              <p className="text-xs text-muted mt-0.5">
                Complete weekly lecture schedule by faculty member with slots, subjects, rooms &amp; sections
              </p>
            </div>
          </div>
          <span
            className={`rounded-full px-3 py-1 text-xs font-bold shrink-0 ${
              selectedRole === "teacher"
                ? "bg-indigo-600 text-white"
                : "bg-surface text-muted border border-line"
            }`}
          >
            {selectedRole === "teacher" ? "Selected" : "View"}
          </span>
        </button>
      </div>

      {/* ================= SELECTOR BAR (SECTION OR TEACHER) ================= */}
      <div className="rounded-2xl border border-line bg-panel p-4 sm:p-5 shadow-2xs flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-4">
          {selectedRole === "student" ? (
            <div>
              <label htmlFor="tt-section-select" className="block text-xs font-bold text-muted mb-1">
                Select Class / Section
              </label>
              <select
                id="tt-section-select"
                value={selectedSection}
                onChange={(e) => setSelectedSection(e.target.value)}
                className="rounded-xl border border-line bg-surface px-3.5 py-2 text-xs font-bold text-ink focus:outline-hidden focus:ring-2 focus:ring-brand-500"
              >
                {sectionNames.map((sec) => (
                  <option key={sec} value={sec}>
                    {sec}
                  </option>
                ))}
              </select>
            </div>
          ) : (
            <div>
              <label htmlFor="tt-teacher-select" className="block text-xs font-bold text-muted mb-1">
                Select Teacher
              </label>
              <select
                id="tt-teacher-select"
                value={selectedTeacher}
                onChange={(e) => setSelectedTeacher(e.target.value)}
                className="rounded-xl border border-line bg-surface px-3.5 py-2 text-xs font-bold text-ink focus:outline-hidden focus:ring-2 focus:ring-indigo-500"
              >
                {teacherNames.map((tName) => (
                  <option key={tName} value={tName}>
                    {tName}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div className="rounded-xl border border-line bg-surface px-3.5 py-2 text-xs">
            <span className="text-muted">Weekly Load: </span>
            <strong className="text-ink font-mono">{totalWeeklyLectures} Lectures / Week</strong>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <div className="inline-flex rounded-xl border border-line bg-surface p-1 text-xs">
            <button
              type="button"
              onClick={() => setDisplayStyle("weekly_list")}
              className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 font-semibold transition ${
                displayStyle === "weekly_list"
                  ? "bg-brand-600 text-white"
                  : "text-muted hover:text-ink"
              }`}
            >
              <List size={13} />
              <span>Weekly Breakdown</span>
            </button>
            <button
              type="button"
              onClick={() => setDisplayStyle("interactive_engine")}
              className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 font-semibold transition ${
                displayStyle === "interactive_engine"
                  ? "bg-brand-600 text-white"
                  : "text-muted hover:text-ink"
              }`}
            >
              <LayoutGrid size={13} />
              <span>Matrix &amp; Map View</span>
            </button>
          </div>

          <button
            type="button"
            onClick={() =>
              downloadICSFile(
                activeSchedule,
                selectedRole === "student"
                  ? `${selectedSection}_Timetable.ics`
                  : `${selectedTeacher.replace(/\s+/g, "_")}_Timetable.ics`
              )
            }
            className="inline-flex items-center gap-1.5 rounded-xl border border-line bg-surface px-3 py-2 text-xs font-bold text-ink hover:border-brand-500 transition"
          >
            <Download size={13} />
            <span>Export .ics</span>
          </button>
        </div>
      </div>

      {/* ================= DISPLAY VIEW ================= */}
      {displayStyle === "interactive_engine" ? (
        <IntelligentTimetableEngine
          schedule={activeSchedule}
          mode={selectedRole}
          title={
            selectedRole === "student"
              ? `Student Timetable — ${selectedSection}`
              : `Teacher Timetable — ${selectedTeacher}`
          }
          description="Complete weekly lecture matrix, day timeline, room blueprint locator, and calendar sync."
        />
      ) : (
        <div className="space-y-5">
          {WEEKDAYS.map((day) => {
            const daySlots = activeSchedule
              .filter((s) => s.day === day)
              .sort((a, b) => a.slotNumber - b.slotNumber);

            return (
              <div
                key={day}
                className="rounded-2xl border border-line bg-panel p-5 shadow-2xs space-y-4"
              >
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-line pb-3">
                  <div className="flex items-center gap-2">
                    <Calendar size={16} className="text-brand-600" />
                    <h3 className="font-extrabold text-base text-ink">{day}</h3>
                  </div>
                  <span
                    className={`rounded-full px-3 py-0.5 text-xs font-bold ${
                      daySlots.length > 0
                        ? "bg-brand-500/10 text-brand-600"
                        : "bg-surface text-muted border border-line"
                    }`}
                  >
                    {daySlots.length} {daySlots.length === 1 ? "Lecture" : "Lectures"}
                  </span>
                </div>

                {daySlots.length === 0 ? (
                  <p className="text-xs text-muted italic py-1">
                    No lectures scheduled on {day}.
                  </p>
                ) : (
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {daySlots.map((slot) => (
                      <div
                        key={slot.id}
                        className={`rounded-2xl border p-4 space-y-3 ${slot.colorScheme.border} ${slot.colorScheme.bg}`}
                      >
                        <div className="flex items-center justify-between gap-2">
                          <span className={`rounded-md px-2 py-0.5 text-xs font-extrabold ${slot.colorScheme.badge}`}>
                            Slot {slot.slotNumber}
                          </span>
                          <span className="font-mono text-xs font-semibold text-muted flex items-center gap-1">
                            <Clock size={12} />
                            <span>{slot.timeRange}</span>
                          </span>
                        </div>

                        <div>
                          <p className="font-mono text-2xs font-bold text-muted">{slot.courseCode}</p>
                          <h4 className="font-extrabold text-sm text-ink mt-0.5">{slot.courseTitle}</h4>
                        </div>

                        <div className="space-y-1.5 pt-2 border-t border-line/50 text-xs text-muted">
                          {selectedRole === "student" ? (
                            <p className="flex items-center gap-1.5">
                              <UserCheck size={13} className="text-brand-600 shrink-0" />
                              <span>
                                Teacher: <strong className="text-ink">{slot.instructorName}</strong>
                              </span>
                            </p>
                          ) : (
                            <p className="flex items-center gap-1.5">
                              <GraduationCap size={13} className="text-indigo-600 shrink-0" />
                              <span>
                                Section: <strong className="text-ink">{slot.section}</strong>
                              </span>
                            </p>
                          )}

                          <p className="flex items-center gap-1.5">
                            <MapPin size={13} className="text-brand-600 shrink-0" />
                            <span>
                              Classroom: <strong className="text-ink">{slot.room}</strong> ({slot.block}, {slot.floor})
                            </span>
                          </p>

                          {selectedRole === "student" && (
                            <p className="flex items-center gap-1.5">
                              <Users size={13} className="text-emerald-600 shrink-0" />
                              <span>
                                Class Capacity: <strong className="text-ink">{slot.capacity} students</strong>{" "}
                                <span className="text-2xs">({slot.enrolledStudents} enrolled)</span>
                              </span>
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

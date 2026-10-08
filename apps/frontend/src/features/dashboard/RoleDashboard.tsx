import { Card } from "../../components/ui/Card";
import type { AppRole } from "../auth/types";

const content: Record<AppRole, { title: string; description: string; modules: string[] }> = {
  student: {
    title: "Student dashboard",
    description: "Your academic workspace for attendance, timetable, resources, assessments, facilities, and notifications.",
    modules: ["Attendance", "Timetable", "Learning resources", "Assessments", "Facility bookings", "Notifications"]
  },
  teacher: {
    title: "Teacher dashboard",
    description: "Manage assigned classes, attendance, teaching schedule, learning resources, assessments, and communications.",
    modules: ["Assigned classes", "Attendance", "Teaching timetable", "Learning resources", "Assessments", "Notifications"]
  },
  admin: {
    title: "Admin dashboard",
    description: "Operate users, academic master data, timetables, facilities, reporting, and platform services.",
    modules: ["Identity & users", "Academic setup", "Scheduling", "Facilities", "Reporting & analytics", "Platform operations"]
  }
};

export function RoleDashboard({ role }: { role: AppRole }) {
  const dashboard = content[role];
  return (
    <div className="page-container">
      <div className="mb-6">
        <p className="text-sm font-semibold uppercase tracking-wide text-brand-700">{role}</p>
        <h1 className="mt-1 text-3xl font-bold tracking-tight">{dashboard.title}</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-muted">{dashboard.description}</p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {dashboard.modules.map((module) => (
          <Card key={module} title={module}>
            <p className="text-sm leading-6 text-muted">
              The shared frontend foundation is ready. Domain-specific views are implemented in the upcoming role UX sprints.
            </p>
          </Card>
        ))}
      </div>
    </div>
  );
}

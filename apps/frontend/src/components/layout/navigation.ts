import type { AppRole } from "../../features/auth/types";

export type NavItem = {
  label: string;
  path: string;
  roles: AppRole[];
};

export const navigation: NavItem[] = [
  { label: "Dashboard", path: "/app", roles: ["student", "teacher", "admin"] },

  { label: "My attendance", path: "/app/student/attendance", roles: ["student"] },
  { label: "My timetable", path: "/app/student/timetable", roles: ["student"] },
  { label: "Learning", path: "/app/student/learning", roles: ["student"] },
  { label: "Assessments", path: "/app/student/assessments", roles: ["student"] },
  { label: "Facilities", path: "/app/student/facilities", roles: ["student"] },

  { label: "Classes & attendance", path: "/app/teacher/attendance", roles: ["teacher"] },
  { label: "Teaching timetable", path: "/app/teacher/timetable", roles: ["teacher"] },
  { label: "Learning resources", path: "/app/teacher/learning", roles: ["teacher"] },
  { label: "Assessments", path: "/app/teacher/assessments", roles: ["teacher"] },
  { label: "Announcements", path: "/app/teacher/announcements", roles: ["teacher"] },
  { label: "Facility bookings", path: "/app/teacher/facilities", roles: ["teacher"] },

  { label: "Users & RBAC", path: "/app/admin/users", roles: ["admin"] },
  { label: "Academic setup", path: "/app/admin/academic", roles: ["admin"] },
  { label: "Attendance management", path: "/app/admin/attendance", roles: ["admin"] },
  { label: "Scheduling", path: "/app/admin/scheduling", roles: ["admin"] },
  { label: "Facilities", path: "/app/admin/facilities", roles: ["admin"] },
  { label: "Announcements", path: "/app/admin/notifications", roles: ["admin"] },
  { label: "Reporting", path: "/app/admin/reporting", roles: ["admin"] },
  { label: "Platform operations", path: "/app/admin/platform", roles: ["admin"] },

  { label: "Notifications", path: "/app/notifications", roles: ["student", "teacher", "admin"] },
  { label: "Profile", path: "/app/profile", roles: ["student", "teacher", "admin"] }
];

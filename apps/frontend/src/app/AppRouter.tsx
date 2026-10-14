import { lazy, Suspense } from "react";
import { FullPageLoader } from "../components/ui/FullPageLoader";
import { Navigate, Route, Routes } from "react-router-dom";
import { WorkspaceShell as AppShell } from "../components/layout/WorkspaceShell";
import { ProtectedRoute } from "../features/auth/ProtectedRoute";
const ForbiddenPage = lazy(() => import("../pages/ForbiddenPage").then(module => ({ default: module.ForbiddenPage })));
const EmailVerificationRequestPage = lazy(() => import("../pages/EmailVerificationRequestPage").then(module => ({ default: module.EmailVerificationRequestPage })));
const ForgotPasswordPage = lazy(() => import("../pages/ForgotPasswordPage").then(module => ({ default: module.ForgotPasswordPage })));
const ResetPasswordPage = lazy(() => import("../pages/ResetPasswordPage").then(module => ({ default: module.ResetPasswordPage })));
const VerifyEmailPage = lazy(() => import("../pages/VerifyEmailPage").then(module => ({ default: module.VerifyEmailPage })));
const LoginPage = lazy(() => import("../pages/LoginPage").then(module => ({ default: module.LoginPage })));
const NotFoundPage = lazy(() => import("../pages/NotFoundPage").then(module => ({ default: module.NotFoundPage })));
const NotificationsPage = lazy(() => import("../pages/NotificationsPage").then(module => ({ default: module.NotificationsPage })));
const ProfilePage = lazy(() => import("../pages/ProfilePage").then(module => ({ default: module.ProfilePage })));
const RegisterPage = lazy(() => import("../pages/RegisterPage").then(module => ({ default: module.RegisterPage })));
const RoleHomeRedirect = lazy(() => import("../pages/RoleHomeRedirect").then(module => ({ default: module.RoleHomeRedirect })));

const AdminAttendancePage = lazy(() => import("../pages/admin/AdminAttendancePage").then(module => ({ default: module.AdminAttendancePage })));
const AdminAcademicPage = lazy(() => import("../pages/admin/AdminAcademicPage").then(module => ({ default: module.AdminAcademicPage })));
const AdminDashboardPage = lazy(() => import("../pages/admin/AdminDashboardPage").then(module => ({ default: module.AdminDashboardPage })));
const AdminFacilitiesPage = lazy(() => import("../pages/admin/AdminFacilitiesPage").then(module => ({ default: module.AdminFacilitiesPage })));
const AdminNotificationsPage = lazy(() => import("../pages/admin/AdminNotificationsPage").then(module => ({ default: module.AdminNotificationsPage })));
const AdminPlatformPage = lazy(() => import("../pages/admin/AdminPlatformPage").then(module => ({ default: module.AdminPlatformPage })));
const AdminReportingPage = lazy(() => import("../pages/admin/AdminReportingPage").then(module => ({ default: module.AdminReportingPage })));
const AdminSchedulingPage = lazy(() => import("../pages/admin/AdminSchedulingPage").then(module => ({ default: module.AdminSchedulingPage })));
const AdminUsersPage = lazy(() => import("../pages/admin/AdminUsersPage").then(module => ({ default: module.AdminUsersPage })));

const StudentAssessmentAttemptPage = lazy(() => import("../pages/student/StudentAssessmentAttemptPage").then(module => ({ default: module.StudentAssessmentAttemptPage })));
const StudentAssessmentsPage = lazy(() => import("../pages/student/StudentAssessmentsPage").then(module => ({ default: module.StudentAssessmentsPage })));
const StudentAttendancePage = lazy(() => import("../pages/student/StudentAttendancePage").then(module => ({ default: module.StudentAttendancePage })));
const StudentDashboardPage = lazy(() => import("../pages/student/StudentDashboardPage").then(module => ({ default: module.StudentDashboardPage })));
const StudentFacilitiesPage = lazy(() => import("../pages/student/StudentFacilitiesPage").then(module => ({ default: module.StudentFacilitiesPage })));
const StudentLearningPage = lazy(() => import("../pages/student/StudentLearningPage").then(module => ({ default: module.StudentLearningPage })));
const StudentTimetablePage = lazy(() => import("../pages/student/StudentTimetablePage").then(module => ({ default: module.StudentTimetablePage })));

const TeacherAnnouncementsPage = lazy(() => import("../pages/teacher/TeacherAnnouncementsPage").then(module => ({ default: module.TeacherAnnouncementsPage })));
const TeacherAssessmentsPage = lazy(() => import("../pages/teacher/TeacherAssessmentsPage").then(module => ({ default: module.TeacherAssessmentsPage })));
const TeacherClassesAttendancePage = lazy(() => import("../pages/teacher/TeacherClassesAttendancePage").then(module => ({ default: module.TeacherClassesAttendancePage })));
const TeacherDashboardPage = lazy(() => import("../pages/teacher/TeacherDashboardPage").then(module => ({ default: module.TeacherDashboardPage })));
const TeacherFacilitiesPage = lazy(() => import("../pages/teacher/TeacherFacilitiesPage").then(module => ({ default: module.TeacherFacilitiesPage })));
const TeacherLearningPage = lazy(() => import("../pages/teacher/TeacherLearningPage").then(module => ({ default: module.TeacherLearningPage })));
const TeacherTimetablePage = lazy(() => import("../pages/teacher/TeacherTimetablePage").then(module => ({ default: module.TeacherTimetablePage })));

export function AppRouter() {
  return (
    <Suspense fallback={<FullPageLoader />}><Routes>
      <Route path="/" element={<Navigate to="/app" replace />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />
      <Route path="/verify-email" element={<VerifyEmailPage />} />
      <Route
        path="/verify-email/request"
        element={<EmailVerificationRequestPage />}
      />
      <Route path="/forbidden" element={<ForbiddenPage />} />

      <Route element={<ProtectedRoute />}>
        <Route path="/app" element={<AppShell />}>
          <Route index element={<RoleHomeRedirect />} />

          <Route element={<ProtectedRoute roles={["student"]} />}>
            <Route path="student" element={<StudentDashboardPage />} />
            <Route path="student/attendance" element={<StudentAttendancePage />} />
            <Route path="student/timetable" element={<StudentTimetablePage />} />
            <Route path="student/learning" element={<StudentLearningPage />} />
            <Route path="student/assessments" element={<StudentAssessmentsPage />} />
            <Route
              path="student/assessments/:assignmentId"
              element={<StudentAssessmentAttemptPage />}
            />
            <Route path="student/facilities" element={<StudentFacilitiesPage />} />
          </Route>

          <Route element={<ProtectedRoute roles={["teacher"]} />}>
            <Route path="teacher" element={<TeacherDashboardPage />} />
            <Route
              path="teacher/attendance"
              element={<TeacherClassesAttendancePage />}
            />
            <Route path="teacher/timetable" element={<TeacherTimetablePage />} />
            <Route path="teacher/learning" element={<TeacherLearningPage />} />
            <Route path="teacher/assessments" element={<TeacherAssessmentsPage />} />
            <Route
              path="teacher/announcements"
              element={<TeacherAnnouncementsPage />}
            />
            <Route path="teacher/facilities" element={<TeacherFacilitiesPage />} />
          </Route>

          <Route element={<ProtectedRoute roles={["admin"]} />}>
            <Route path="admin" element={<AdminDashboardPage />} />
            <Route path="admin/users" element={<AdminUsersPage />} />
            <Route path="admin/academic" element={<AdminAcademicPage />} />
            <Route path="admin/attendance" element={<AdminAttendancePage />} />
            <Route path="admin/scheduling" element={<AdminSchedulingPage />} />
            <Route path="admin/facilities" element={<AdminFacilitiesPage />} />
            <Route path="admin/notifications" element={<AdminNotificationsPage />} />
            <Route path="admin/reporting" element={<AdminReportingPage />} />
            <Route path="admin/platform" element={<AdminPlatformPage />} />
          </Route>

          <Route path="notifications" element={<NotificationsPage />} />
          <Route path="profile" element={<ProfilePage />} />
        </Route>
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes></Suspense>
  );
}

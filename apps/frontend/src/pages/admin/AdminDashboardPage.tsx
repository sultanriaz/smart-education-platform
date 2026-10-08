import { Link } from "react-router-dom";
import { Card } from "../../components/ui/Card";
import { InlineError } from "../../components/ui/InlineError";
import { DashboardWelcome } from "../../components/ui/DashboardWelcome";
import { SectionLoader } from "../../components/ui/SectionLoader";
import { StatCard } from "../../components/ui/StatCard";
import {
  useAdminBookings,
  useAdminUsers,
  usePlatformServices,
  useReportingOverview,
  useSupportTickets
} from "../../features/admin/hooks";

export function AdminDashboardPage() {
  const overview = useReportingOverview();
  const users = useAdminUsers();
  const bookings = useAdminBookings();
  const services = usePlatformServices();
  const tickets = useSupportTickets();

  if (
    overview.isLoading &&
    users.isLoading &&
    bookings.isLoading &&
    services.isLoading &&
    tickets.isLoading
  ) {
    return (
      <div className="page-container">
        <SectionLoader label="Loading administration dashboard…" />
      </div>
    );
  }

  const pendingBookings = (bookings.data ?? []).filter(
    (item) => item.status === "PENDING"
  ).length;
  const openTickets = (tickets.data ?? []).filter(
    (item) => !["CLOSED", "RESOLVED"].includes(item.status)
  ).length;
  const enabledServices = (services.data ?? []).filter((item) => item.enabled).length;
  const error =
    overview.error ?? users.error ?? bookings.error ?? services.error ?? tickets.error;

  return (
    <div className="page-container">
      <DashboardWelcome subtitle="A connected campus starts with a clear view. Keep your institution, people, and operations moving." action="Explore institution reports" to="/app/admin/reporting" />

      {error ? (
        <div className="mb-5">
          <InlineError message="Some administration data could not be loaded. Individual modules may still be available." />
        </div>
      ) : null}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Accounts in current page"
          value={users.data?.length ?? "—"}
          helper="Browse all accounts in user management."
        />
        <StatCard
          label="Active enrollments"
          value={overview.data?.activeEnrollments ?? "—"}
          helper="Institution reporting overview."
        />
        <StatCard
          label="Pending bookings"
          value={bookings.data ? pendingBookings : "—"}
          helper="Facility requests awaiting a decision."
        />
        <StatCard
          label="Open support tickets"
          value={tickets.data ? openTickets : "—"}
          helper="Platform support queue."
        />
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Attendance"
          value={
            overview.data?.attendancePercentage != null
              ? `${overview.data.attendancePercentage.toFixed(1)}%`
              : "—"
          }
          helper="Aggregated attendance percentage."
        />
        <StatCard
          label="Assessment average"
          value={
            overview.data?.assessmentAveragePercent != null
              ? `${overview.data.assessmentAveragePercent.toFixed(1)}%`
              : "—"
          }
          helper="Across graded attempts."
        />
        <StatCard
          label="Notification success"
          value={
            overview.data?.notificationSuccessRate != null
              ? `${overview.data.notificationSuccessRate.toFixed(1)}%`
              : "—"
          }
          helper="Delivery success rate."
        />
        <StatCard
          label="Enabled services"
          value={services.data ? enabledServices : "—"}
          helper="Registered Platform service endpoints."
        />
      </div>

      <Card className="mt-6" title="Administration modules">
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {([
            ["/app/admin/users", "Users & RBAC"],
            ["/app/admin/academic", "Academic setup"],
            ["/app/admin/scheduling", "Scheduling"],
            ["/app/admin/facilities", "Facilities"],
            ["/app/admin/notifications", "Announcements"],
            ["/app/admin/reporting", "Reporting"],
            ["/app/admin/platform", "Platform operations"]
          ] as const).map(([path, label]) => (
            <Link
              key={path}
              to={path}
              className="rounded-xl border border-line bg-panel px-4 py-4 text-sm font-semibold hover:bg-surface"
            >
              {label}
            </Link>
          ))}
        </div>
      </Card>
    </div>
  );
}

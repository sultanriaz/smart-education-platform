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
          <InlineError
            message="Some administration data could not be loaded. Individual modules may still be available."
            onRetry={() => {
              void overview.refetch();
              void users.refetch();
              void bookings.refetch();
              void services.refetch();
              void tickets.refetch();
            }}
            isRetrying={
              overview.isFetching ||
              users.isFetching ||
              bookings.isFetching ||
              services.isFetching ||
              tickets.isFetching
            }
          />
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
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
          {([
            ["/app/admin/users", "Users & RBAC", "Accounts, roles & permissions"],
            ["/app/admin/academic", "Academic Setup", "Curriculum, courses & sections"],
            ["/app/admin/attendance", "Attendance Mgmt", "Audited sessions & corrections"],
            ["/app/admin/finance", "Finance & Accounts", "Tuition, general ledger & fees"],
            ["/app/admin/payroll", "Payroll Mgmt", "Staff salaries, tax & disbursements"],
            ["/app/admin/scheduling", "Scheduling", "Timetable rules & occurrences"],
            ["/app/admin/facilities", "Facilities", "Campus spaces & reservations"],
            ["/app/admin/notifications", "Announcements", "Broadcast messages & logs"],
            ["/app/admin/reporting", "Reporting", "Institutional analytics & exports"],
            ["/app/admin/platform", "Platform Operations", "Audit trails & feature flags"]
          ] as const).map(([path, label, desc]) => (
            <Link
              key={path}
              to={path}
              className="rounded-xl border border-line bg-panel p-4 hover:border-brand-500 hover:bg-surface transition group"
            >
              <p className="text-sm font-semibold text-text group-hover:text-brand-600 transition">
                {label}
              </p>
              <p className="mt-1 text-xs text-muted leading-5">{desc}</p>
            </Link>
          ))}
        </div>
      </Card>
    </div>
  );
}

import { Badge } from "../components/ui/Badge";
import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "../lib/api-client";
import { Card } from "../components/ui/Card";
import { useAuth } from "../features/auth/useAuth";

export function ProfilePage() {
  const { user } = useAuth();
  const history = useQuery({
    queryKey: ["identity", "security-history", user?.id],
    enabled: Boolean(user?.id),
    queryFn: () => apiRequest<Array<{ id: string; action: string; outcome: string; created_at: string; ip_address: string | null }>>("/api/v1/identity/users/me/security-history?limit=25")
  });
  return (
    <div className="page-container">
      <h1 className="text-3xl font-bold tracking-tight">Profile</h1>
      <p className="mt-2 text-sm text-muted">
        Identity details come from the authenticated Identity Service session.
      </p>
      <Card className="mt-6" title="Account">
        <dl className="grid gap-5 sm:grid-cols-2">
          <div>
            <dt className="text-xs font-semibold uppercase tracking-wide text-muted">User ID</dt>
            <dd className="mt-1 break-all text-sm">{user?.id}</dd>
          </div>
          <div>
            <dt className="text-xs font-semibold uppercase tracking-wide text-muted">Email</dt>
            <dd className="mt-1 text-sm">{user?.email ?? "Not provided"}</dd>
          </div>
          <div className="sm:col-span-2">
            <dt className="text-xs font-semibold uppercase tracking-wide text-muted">Roles</dt>
            <dd className="mt-2 flex flex-wrap gap-2">
              {user?.roles.map((role) => <Badge key={role}>{role}</Badge>)}
            </dd>
          </div>
        </dl>
      </Card>
      <Card className="mt-6" title="Recent account security activity" description="Your own sign-in and security events only.">
        {history.isLoading ? <p role="status">Loading your account activity…</p> : history.isError ? (
          <p role="alert">Unable to retrieve security history.</p>
        ) : (history.data ?? []).length ? (
          <ul className="space-y-3" aria-label="Recent account activity">
            {(history.data ?? []).map((event) => (
              <li key={event.id} className="flex flex-wrap items-center justify-between gap-2 border-b border-line py-2 text-sm">
                <span>{event.action} <Badge>{event.outcome}</Badge></span>
                <time dateTime={event.created_at}>{new Date(event.created_at).toLocaleString()}</time>
              </li>
            ))}
          </ul>
        ) : <p className="text-sm text-muted">No security history is available.</p>}
      </Card>
    </div>
  );
}

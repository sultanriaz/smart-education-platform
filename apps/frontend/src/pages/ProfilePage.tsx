import { Badge } from "../components/ui/Badge";
import { Card } from "../components/ui/Card";
import { useAuth } from "../features/auth/useAuth";

export function ProfilePage() {
  const { user } = useAuth();
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
    </div>
  );
}

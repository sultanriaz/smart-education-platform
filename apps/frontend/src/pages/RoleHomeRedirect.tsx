import { Navigate } from "react-router-dom";
import { useAuth } from "../features/auth/useAuth";
import { primaryRole } from "../features/auth/permissions";

export function RoleHomeRedirect() {
  const { user } = useAuth();
  const role = user ? primaryRole(user.roles) : null;
  return <Navigate to={role ? `/app/${role}` : "/forbidden"} replace />;
}

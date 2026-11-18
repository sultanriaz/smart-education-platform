import { Navigate, Outlet, useLocation } from "react-router-dom";
import { FullPageLoader } from "../../components/ui/FullPageLoader";
import { useAuth } from "./useAuth";
import { hasAnyRole } from "./permissions";
import type { AppRole } from "./types";

export function ProtectedRoute({ roles = [] }: { roles?: AppRole[] }) {
  const { state, user } = useAuth();
  const location = useLocation();

  if (state === "booting") {
    return <FullPageLoader label="Checking your session…" />;
  }

  if (state === "anonymous" || !user) {
    const loginPath =
      roles.length === 1 && roles[0] === "teacher"
        ? "/login/faculty"
        : roles.length === 1 && roles[0] === "student"
        ? "/login/student"
        : "/login";
    return <Navigate to={loginPath} replace state={{ from: location.pathname }} />;
  }

  if (!hasAnyRole(user.roles, roles)) {
    return <Navigate to="/forbidden" replace />;
  }

  return <Outlet />;
}

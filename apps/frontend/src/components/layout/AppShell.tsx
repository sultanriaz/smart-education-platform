import { useMemo, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../../features/auth/useAuth";
import { hasAnyRole } from "../../features/auth/permissions";
import { runtimeConfig } from "../../lib/runtime-config";
import { Button } from "../ui/Button";
import { navigation } from "./navigation";

export function AppShell() {
  const { user, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  const items = useMemo(
    () => navigation.filter((item) => (user ? hasAnyRole(user.roles, item.roles) : false)),
    [user]
  );

  return (
    <div className="min-h-screen bg-surface">
      <a
        href="#main-content"
        className="sr-only z-[100] rounded bg-panel px-4 py-2 focus:not-sr-only focus:fixed focus:left-4 focus:top-4"
      >
        Skip to main content
      </a>

      <header className="sticky top-0 z-30 border-b border-line bg-panel/95 backdrop-blur">
        <div className="flex h-16 items-center gap-3 px-4 sm:px-6">
          <button
            className="rounded-lg border border-line px-3 py-2 text-sm lg:hidden"
            onClick={() => setMobileOpen((value) => !value)}
            aria-expanded={mobileOpen}
            aria-controls="primary-navigation"
          >
            Menu
          </button>

          <div className="min-w-0">
            <p className="truncate text-sm font-bold text-brand-700">{runtimeConfig.appName}</p>
            <p className="truncate text-xs text-muted">Unified academic workspace</p>
          </div>

          <div className="ml-auto flex items-center gap-3">
            <div className="hidden text-right sm:block">
              <p className="max-w-48 truncate text-sm font-semibold">
                {user?.fullName ?? user?.email ?? "Signed in"}
              </p>
              <p className="text-xs capitalize text-muted">{user?.roles.join(" · ")}</p>
            </div>
            <Button variant="secondary" onClick={() => void logout()}>
              Sign out
            </Button>
          </div>
        </div>
      </header>

      <div className="lg:grid lg:grid-cols-[17rem_minmax(0,1fr)]">
        <aside
          id="primary-navigation"
          className={[
            "border-r border-line bg-panel p-4 lg:sticky lg:top-16 lg:block lg:h-[calc(100vh-4rem)] lg:overflow-y-auto",
            mobileOpen ? "block" : "hidden"
          ].join(" ")}
        >
          <nav aria-label="Primary navigation" className="space-y-1">
            {items.map((item) => (
              <NavLink
                key={`${item.path}-${item.label}`}
                to={item.path}
                end={item.path === "/app"}
                onClick={() => setMobileOpen(false)}
                className={({ isActive }) =>
                  [
                    "block rounded-xl px-3 py-2.5 text-sm font-medium transition",
                    isActive ? "bg-brand-50 text-brand-700" : "text-ink hover:bg-surface"
                  ].join(" ")
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </aside>

        <main id="main-content" className="min-w-0">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

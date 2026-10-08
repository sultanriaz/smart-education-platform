import { useEffect, useMemo, useRef, useState } from "react";
import { Link, NavLink, Outlet, useLocation } from "react-router-dom";
import { ArrowUpRight, Bell, BookOpen, CalendarDays, ChevronDown, ClipboardCheck, GraduationCap, LayoutDashboard, LifeBuoy, LogOut, Menu, Moon, Search, Settings2, ShieldCheck, Sun, Users, X } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useAuth } from "../../features/auth/useAuth";
import { hasAnyRole, primaryRole } from "../../features/auth/permissions";
import { useUnreadCount } from "../../features/student/hooks";
import { navigation } from "./navigation";

const icons: Record<string, LucideIcon> = { Dashboard: LayoutDashboard, Learning: BookOpen, Assessments: ClipboardCheck, Notifications: Bell, Profile: Settings2 };
function iconFor(label: string): LucideIcon {
  if (/timetable|Scheduling/.test(label)) return CalendarDays;
  if (/attendance/.test(label)) return ClipboardCheck;
  if (/Users/.test(label)) return Users;
  if (/Academic/.test(label)) return GraduationCap;
  if (/operations/.test(label)) return ShieldCheck;
  return icons[label] ?? BookOpen;
}

export function WorkspaceShell() {
  const { user, logout } = useAuth();
  const unread = useUnreadCount();
  const location = useLocation();
  const drawer = useRef<HTMLDialogElement>(null);
  const searchDialog = useRef<HTMLDialogElement>(null);
  const searchInput = useRef<HTMLInputElement>(null);
  const [search, setSearch] = useState("");
  const [collapsed, setCollapsed] = useState(false);
  const [theme, setTheme] = useState(() => document.documentElement.dataset.theme ?? "light");
  const role = user ? primaryRole(user.roles) : null;
  const items = useMemo(() => navigation.filter(item => user && hasAnyRole(user.roles, item.roles)).map(item => item.path === "/app" ? { ...item, path: `/app/${role}` } : item), [user, role]);
  const title = items.find(item => item.path === location.pathname)?.label ?? "Workspace";
  const name = user?.fullName ?? "Your workspace";
  const initials = name.split(" ").map(word => word[0]).slice(0, 2).join("").toUpperCase();

  function toggleTheme() {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    document.documentElement.dataset.theme = next;
    localStorage.setItem("sep-theme", next);
  }

  useEffect(() => {
    const openSearch = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key === "k") {
        event.preventDefault();
        searchDialog.current?.showModal();
        searchInput.current?.focus();
      }
    };
    window.addEventListener("keydown", openSearch);
    return () => window.removeEventListener("keydown", openSearch);
  }, []);

  function closeMenus() {
    drawer.current?.close();
    searchDialog.current?.close();
  }

  const nav = (
    <>
      <Link to={`/app/${role}`} className="workspace-brand" onClick={closeMenus}>
        <span className="brand-mark"><GraduationCap size={23} /></span>
        <span className="brand-copy">EduSphere<span>SMART EDUCATION</span></span>
      </Link>
      <div className="workspace-label">YOUR WORKSPACE <span className="role-pill">{role}</span></div>
      <nav aria-label="Primary navigation" className="workspace-nav">
        {items.map(item => {
          const Icon = iconFor(item.label);
          return <NavLink key={item.path} to={item.path} end onClick={closeMenus} title={collapsed ? item.label : undefined} className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}><Icon size={18} /><span>{item.label}</span>{item.label === "Notifications" && Boolean(unread.data) && <small>{unread.data}</small>}</NavLink>;
        })}
      </nav>
      <div className="workspace-help"><LifeBuoy size={20} /><strong>A little help goes a long way.</strong><p>Find your profile and account details in one place.</p><Link to="/app/profile" onClick={closeMenus}>Account settings <ArrowUpRight size={15} /></Link></div>
      <div className="workspace-footer"><span className="avatar">{initials}</span><div><strong>{name}</strong><span>{user?.email}</span></div><button onClick={() => void logout()} className="icon-button" aria-label="Sign out" title="Sign out"><LogOut size={17} /></button></div>
    </>
  );

  return (
    <div className={`workspace ${collapsed ? "sidebar-collapsed" : ""}`}>
      <a href="#main-content" className="skip-link">Skip to main content</a>
      <aside className="workspace-sidebar">{nav}</aside>
      <div className="workspace-body">
        <header className="workspace-topbar">
          <button className="icon-button mobile-menu" aria-label="Open navigation" onClick={() => drawer.current?.showModal()}><Menu size={20} /></button>
          <button className="icon-button desktop-menu" aria-label={collapsed ? "Expand navigation" : "Collapse navigation"} aria-expanded={!collapsed} onClick={() => setCollapsed(!collapsed)}><Menu size={18} /></button>
          <div className="breadcrumb"><span>Workspace</span><span>/</span><strong>{title}</strong></div>
          <div className="topbar-actions">
            <button className="search-trigger" aria-label="Search pages" onClick={() => { searchDialog.current?.showModal(); searchInput.current?.focus(); }}><Search size={16} /><span>Find a page…</span><kbd>Ctrl K</kbd></button>
            <button className="icon-button" aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`} onClick={toggleTheme}>{theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}</button>
            <Link to="/app/notifications" className="icon-button notification-button" aria-label={`Notifications${unread.data ? `, ${unread.data} unread` : ""}`}><Bell size={18} />{Boolean(unread.data) && <span className="notification-dot" />}</Link>
            <details className="profile-menu"><summary aria-label="Account menu"><span className="avatar small">{initials}</span><ChevronDown size={14} /></summary><div><strong>{name}</strong><Link to="/app/profile">Manage profile</Link><button onClick={() => void logout()}>Sign out</button></div></details>
          </div>
        </header>
        <main id="main-content" tabIndex={-1}><div key={location.pathname} className="route-enter"><Outlet /></div></main>
        <footer className="content-footer"><span>EduSphere · Smart Education Platform</span><span>COMSATS · Sahiwal Campus</span></footer>
      </div>
      <dialog ref={drawer} className="navigation-dialog" aria-label="Navigation"><button className="icon-button dialog-close" aria-label="Close navigation" onClick={() => drawer.current?.close()}><X size={20} /></button>{nav}</dialog>
      <dialog ref={searchDialog} className="search-dialog" aria-labelledby="search-title"><div className="flex items-center justify-between gap-3"><h2 id="search-title">Find your next page</h2><button className="icon-button" aria-label="Close search" onClick={() => searchDialog.current?.close()}><X size={20} /></button></div><label className="search-field"><Search size={18} /><input ref={searchInput} value={search} onChange={event => setSearch(event.target.value)} placeholder="Search your workspace…" aria-label="Search workspace pages" /></label><nav aria-label="Search results">{items.filter(item => item.label.toLowerCase().includes(search.toLowerCase())).map(item => <Link key={item.path} to={item.path} onClick={closeMenus}>{item.label}<ArrowUpRight size={16} /></Link>)}</nav><p className="text-xs text-muted mt-4">Search pages available to your role. Press Escape to close.</p></dialog>
    </div>
  );
}

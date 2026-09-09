import { NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../features/auth/AuthContext";

const primaryItems = [
  ["/", "Today"],
  ["/weight", "Weight"],
  ["/meals", "Meals"],
  ["/exercise", "Exercise"],
] as const;
const moreItems = [
  ["/goals", "Goals"],
  ["/analytics", "Analytics"],
  ["/reminders", "Reminders"],
  ["/profile", "Profile"],
] as const;

function AppLink({ to, children }: { to: string; children: string }) {
  return <NavLink end={to === "/"} to={to} className={({ isActive }) => `nav-link${isActive ? " is-active" : ""}`}>{children}</NavLink>;
}

export function AppShell() {
  const { user, logout } = useAuth();
  return <div className="app-shell">
    <aside className="app-sidebar" aria-label="Primary navigation">
      <NavLink className="brand" to="/"><span className="brand-mark" aria-hidden="true">+</span><span>Daily Well</span></NavLink>
      <p className="sidebar-label">Your tracking</p>
      <nav>{[...primaryItems, ...moreItems].map(([to, label]) => <AppLink key={to} to={to}>{label}</AppLink>)}</nav>
      <div className="sidebar-account"><span className="muted-label">Signed in as</span><strong>{user?.email}</strong><button className="button button-quiet" type="button" onClick={() => void logout()}>Sign out</button></div>
    </aside>
    <div className="app-content">
      <header className="mobile-header"><NavLink className="brand" to="/"><span className="brand-mark" aria-hidden="true">+</span><span>Daily Well</span></NavLink><span className="mobile-user">{user?.email}</span></header>
      <Outlet />
    </div>
    <nav className="mobile-nav" aria-label="Primary navigation">
      {primaryItems.map(([to, label]) => <AppLink key={to} to={to}>{label}</AppLink>)}
      <details className="mobile-more"><summary>More</summary><div className="mobile-more-menu">{moreItems.map(([to, label]) => <AppLink key={to} to={to}>{label}</AppLink>)}<button className="button button-quiet" aria-label="Sign out from mobile menu" type="button" onClick={() => void logout()}>Sign out</button></div></details>
    </nav>
  </div>;
}

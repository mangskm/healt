import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "./AuthContext";

export function RequireAuth() {
  const { state } = useAuth();
  const location = useLocation();
  if (state === "loading") return <main className="auth-loading" aria-live="polite">Checking your session…</main>;
  if (state === "anonymous") return <Navigate to="/login" replace state={{ from: location }} />;
  return <Outlet />;
}

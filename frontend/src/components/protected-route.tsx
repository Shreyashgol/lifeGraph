import { Navigate, Outlet } from "react-router-dom";

import { AppShell } from "@/components/app-shell";
import { useAuth } from "@/contexts/auth-context";

/** Gate: renders the app shell for authenticated users, else redirects to /login. */
export function ProtectedRoute() {
  const { isAuthenticated, ready } = useAuth();

  if (!ready) return null;
  if (!isAuthenticated) return <Navigate to="/login" replace />;

  return (
    <AppShell>
      <Outlet />
    </AppShell>
  );
}

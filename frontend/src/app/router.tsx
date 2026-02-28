import { BrowserRouter, Routes, Route, Navigate } from "react-router";
import { useAuthStore } from "@/features/auth/hooks/use-auth-store";
import { AuthLayout } from "@/shared/layouts/auth-layout";
import { DashboardLayout } from "@/shared/layouts/dashboard-layout";


function LoginPage() {
  return <h1 className="text-2xl font-bold">Login</h1>;
}

function RegisterPage() {
  return <h1 className="text-2xl font-bold">Register</h1>;
}

function DashboardPage() {
  return <h1 className="text-2xl font-bold">Dashboard</h1>;
}

function HistoryPage() {
  return <h1 className="text-2xl font-bold">Historial</h1>;
}

function SettingsPage() {
  return <h1 className="text-2xl font-bold">Configuracion</h1>;
}

// --- Rutas protegidas y publicas ---

/**
 * Si el usuario NO esta autenticado, redirige al login.
 * Envuelve las rutas que requieren JWT (dashboard, historial, etc).
 */
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

/**
 * Si el usuario YA esta autenticado y visita /login o /register,
 * lo redirige al dashboard (no tiene sentido ver el login si ya entro).
 */
function PublicRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return children;
}

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Rutas publicas: login, register (con AuthLayout centrado) */}
        <Route
          element={
            <PublicRoute>
              <AuthLayout />
            </PublicRoute>
          }
        >
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
        </Route>

        {/* Rutas protegidas: dashboard, historial, settings (con Sidebar) */}
        <Route
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/" element={<DashboardPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>

        {/* Cualquier otra ruta redirige al dashboard */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

import { BrowserRouter, Routes, Route, Navigate } from "react-router";
import { useAuthStore } from "@/features/auth/hooks/use-auth-store";
import { AuthLayout } from "@/shared/layouts/auth-layout";
import { DashboardLayout } from "@/shared/layouts/dashboard-layout";

// --- Paginas de auth ---
import { LoginPage } from "@/features/auth/pages/login-page";
import { RegisterPage } from "@/features/auth/pages/register-page";
import { VerifyEmailPage } from "@/features/auth/pages/verify-email-page";
import { ForgotPasswordPage } from "@/features/auth/pages/forgot-password-page";
import { ResetPasswordPage } from "@/features/auth/pages/reset-password-page";

// --- Paginas placeholder (Sprint F3/F4/F5) ---

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
          <Route path="/verify-email" element={<VerifyEmailPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
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

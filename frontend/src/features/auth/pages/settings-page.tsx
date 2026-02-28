import { Moon, Sun, User, Lock } from "lucide-react";
import { Card } from "@/shared/components/card";
import { useAuthStore } from "../hooks/use-auth-store";
import { ChangePasswordForm } from "../components/change-password-form";
import { useTheme } from "@/shared/hooks/use-theme";

export function SettingsPage() {
  const user = useAuthStore((state) => state.user);
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Configuracion</h1>
        <p className="mt-1 text-sm text-slate-500">
          Administra tu cuenta y preferencias
        </p>
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
        {/* Cuenta */}
        <Card>
          <div className="mb-6 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-100">
              <User className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Cuenta</h2>
              <p className="text-sm text-slate-500">
                Informacion de tu cuenta
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-500">
                Email
              </label>
              <p className="mt-1 text-sm font-medium text-slate-900">
                {user?.email ?? "—"}
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-500">
                Rol
              </label>
              <p className="mt-1 text-sm font-medium capitalize text-slate-900">
                {user?.role ?? "—"}
              </p>
            </div>
          </div>
        </Card>

        {/* Tema */}
        <Card>
          <div className="mb-6 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-100">
              {theme === "dark" ? (
                <Moon className="h-5 w-5 text-slate-600" />
              ) : (
                <Sun className="h-5 w-5 text-slate-600" />
              )}
            </div>
            <div>
              <h2 className="text-lg font-semibold text-slate-900">
                Apariencia
              </h2>
              <p className="text-sm text-slate-500">Personaliza la interfaz</p>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-900">Modo oscuro</p>
              <p className="text-sm text-slate-500">
                {theme === "dark" ? "Activado" : "Desactivado"}
              </p>
            </div>
            <button
              onClick={toggleTheme}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                theme === "dark" ? "bg-blue-600" : "bg-slate-300"
              }`}
            >
              <span
                className={`inline-block h-4 w-4 rounded-full bg-white transition-transform ${
                  theme === "dark" ? "translate-x-6" : "translate-x-1"
                }`}
              />
            </button>
          </div>
        </Card>

        {/* Cambiar contraseña (ocupa todo el ancho en lg) */}
        <div className="lg:col-span-2">
          <Card>
            <div className="mb-6 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-rose-100">
                <Lock className="h-5 w-5 text-rose-600" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-slate-900">
                  Cambiar contraseña
                </h2>
                <p className="text-sm text-slate-500">
                  Actualiza tu contraseña de acceso
                </p>
              </div>
            </div>

            <div className="max-w-md">
              <ChangePasswordForm />
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

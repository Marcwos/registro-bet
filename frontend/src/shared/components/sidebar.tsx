import { TrendingUp, LayoutDashboard, History, Settings } from "lucide-react";
import { NavLink } from "react-router";
import { useAuthStore } from "@/features/auth/hooks/use-auth-store";

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/history", label: "Historial", icon: History },
  { to: "/settings", label: "Configuracion", icon: Settings },
];

/**
 * Sidebar de navegacion fijo a la izquierda.
 * - Logo + nombre de la app
 * - Links de navegacion con icono (el activo se resalta)
 * - Info del usuario + boton de cerrar sesion
 */
export function Sidebar() {
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);

  return (
    <aside className="fixed left-0 top-0 flex h-screen w-64 flex-col border-r border-slate-200 bg-white">
      {/* Logo */}
      <div className="flex items-center gap-3 border-b border-slate-200 px-6 py-5">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-600">
          <TrendingUp className="h-5 w-5 text-white" />
        </div>
        <span className="text-lg font-bold text-blue-600">RegistroBet</span>
      </div>

      {/* Navegacion */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                isActive
                  ? "bg-slate-100 text-blue-600"
                  : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
              }`
            }
          >
            <item.icon className="h-5 w-5" />
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Usuario */}
      <div className="border-t border-slate-200 px-4 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-200 text-sm font-medium text-slate-600">
            {user?.email?.charAt(0).toUpperCase() ?? "U"}
          </div>
          <div className="flex-1 truncate">
            <p className="truncate text-sm font-medium text-slate-900">
              {user?.email ?? "Usuario"}
            </p>
          </div>
        </div>
        <button
          onClick={logout}
          className="mt-3 w-full rounded-lg px-3 py-2 text-left text-sm text-slate-500 transition-colors hover:bg-slate-50 hover:text-slate-900"
        >
          Cerrar sesion
        </button>
      </div>
    </aside>
  );
}

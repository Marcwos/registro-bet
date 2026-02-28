import { Outlet } from "react-router";
import { Menu, TrendingUp } from "lucide-react";
import { Sidebar } from "@/shared/components/sidebar";
import { useSidebar } from "@/shared/hooks/use-sidebar";

/**
 * Layout para paginas protegidas (dashboard, historial, settings).
 * Sidebar fijo a la izquierda (desktop) + hamburger header (mobile).
 * <Outlet /> es donde React Router renderiza la pagina hija.
 */
export function DashboardLayout() {
  const open = useSidebar((s) => s.open);

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />

      <div className="flex flex-1 flex-col lg:ml-64">
        {/* Mobile header */}
        <header className="sticky top-0 z-30 flex items-center gap-3 border-b border-slate-200 bg-white px-4 py-3 lg:hidden">
          <button
            onClick={open}
            className="rounded-lg p-2 text-slate-600 transition-colors hover:bg-slate-100"
            aria-label="Abrir menu"
          >
            <Menu className="h-5 w-5" />
          </button>
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-blue-600">
              <TrendingUp className="h-4 w-4 text-white" />
            </div>
            <span className="text-base font-bold text-blue-600">RegistroBet</span>
          </div>
        </header>

        <main className="flex-1 p-4 md:p-6 lg:p-10">
          <div className="mx-auto max-w-7xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}

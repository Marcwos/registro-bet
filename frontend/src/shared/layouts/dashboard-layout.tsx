import { Outlet } from "react-router";
import { Sidebar } from "@/shared/components/sidebar";

/**
 * Layout para paginas protegidas (dashboard, historial, settings).
 * Sidebar fijo a la izquierda + contenido principal con margen.
 * <Outlet /> es donde React Router renderiza la pagina hija.
 */
export function DashboardLayout() {
  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />

      <main className="ml-64 flex-1 p-10">
        <div className="mx-auto max-w-7xl">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

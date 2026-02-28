import { Outlet } from "react-router";

/**
 * Layout para paginas publicas (login, register, verificar email).
 * Centra el contenido vertical y horizontalmente.
 * <Outlet /> es donde React Router renderiza la pagina hija.
 */
export function AuthLayout() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-md">
        <Outlet />
      </div>
    </div>
  );
}

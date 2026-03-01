import { Outlet } from "react-router";
import { motion } from "motion/react";

/**
 * Layout para paginas publicas (login, register, verificar email).
 * Centra el contenido vertical y horizontalmente.
 * <Outlet /> es donde React Router renderiza la pagina hija.
 */
export function AuthLayout() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4 dark:bg-slate-900">
      <motion.div
        className="w-full max-w-md"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <Outlet />
      </motion.div>
    </div>
  );
}

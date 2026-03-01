import { TrendingUp } from "lucide-react";
import { Link } from "react-router";

interface AuthHeaderProps {
  title: string;
  subtitle: string;
}

/**
 * Cabecera reutilizable para paginas de auth (login, register, verify, etc).
 * Muestra el logo, titulo y subtitulo.
 */
export function AuthHeader({ title, subtitle }: AuthHeaderProps) {
  return (
    <div className="mb-8 text-center">
      <Link to="/login" className="mb-6 inline-flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-900">
          <TrendingUp className="h-5 w-5 text-white" />
        </div>
        <span className="text-xl font-bold text-slate-900 dark:text-slate-100">RegistroBet</span>
      </Link>
      <h1 className="mt-4 text-2xl font-bold text-slate-900 dark:text-slate-100">{title}</h1>
      <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">{subtitle}</p>
    </div>
  );
}

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

/**
 * Tarjeta base reutilizable. Borde sutil, esquinas redondeadas, sombra ligera.
 * Se usa como contenedor en el dashboard, formularios, etc.
 */
export function Card({ children, className = "" }: CardProps) {
  return (
    <div
      className={`rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800 ${className}`}
    >
      {children}
    </div>
  );
}

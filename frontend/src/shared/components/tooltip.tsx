import { useEffect, useRef, useState } from "react";
import { Info } from "lucide-react";

interface TooltipProps {
  /** Texto explicativo que se muestra al hacer hover/tap */
  content: string;
}

/**
 * Tooltip informativo con icono (i).
 * - Desktop: aparece al hacer hover sobre el icono.
 * - Mobile: aparece al tocar el icono, se cierra al tocar fuera.
 */
export function Tooltip({ content }: TooltipProps) {
  const [isOpen, setIsOpen] = useState(false);
  const tooltipRef = useRef<HTMLSpanElement>(null);

  // Cerrar al tocar fuera (mobile)
  useEffect(() => {
    if (!isOpen) return;

    function handleClickOutside(e: MouseEvent | TouchEvent) {
      if (tooltipRef.current && !tooltipRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("touchstart", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("touchstart", handleClickOutside);
    };
  }, [isOpen]);

  return (
    <span ref={tooltipRef} className="group relative inline-flex shrink-0">
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        className="cursor-help text-slate-400 transition-colors hover:text-slate-500 dark:text-slate-500 dark:hover:text-slate-400"
        aria-label="Más información"
      >
        <Info className="h-3.5 w-3.5" />
      </button>

      {/* Burbuja — visible con hover (desktop) o estado abierto (mobile) */}
      <div
        className={`pointer-events-none absolute bottom-full left-1/2 z-50 mb-2 w-52 -translate-x-1/2 rounded-lg bg-slate-800 px-3 py-2 text-xs leading-relaxed text-slate-100 shadow-lg transition-opacity duration-150 dark:bg-slate-700 ${
          isOpen
            ? "pointer-events-auto opacity-100"
            : "opacity-0 group-hover:pointer-events-auto group-hover:opacity-100"
        }`}
        role="tooltip"
      >
        {content}
        {/* Flecha */}
        <div className="absolute left-1/2 top-full -translate-x-1/2 border-4 border-transparent border-t-slate-800 dark:border-t-slate-700" />
      </div>
    </span>
  );
}

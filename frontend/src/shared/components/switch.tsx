import { useId, type InputHTMLAttributes } from "react";
import { Tooltip } from "./tooltip";

interface SwitchProps extends Omit<InputHTMLAttributes<HTMLInputElement>, "type" | "role"> {
  label: string;
  description?: string;
  /** Texto informativo mostrado en un tooltip con ícono (i) */
  tooltip?: string;
}

/**
 * Toggle switch reutilizable con label y descripción opcional.
 * Estilizado como un pill toggle (iOS-style) con Tailwind.
 */
export function Switch({ label, description, tooltip, id: externalId, className = "", disabled, ...props }: SwitchProps) {
  const generatedId = useId();
  const switchId = externalId ?? generatedId;

  return (
    <label
      htmlFor={switchId}
      className={`group flex cursor-pointer items-center gap-3 select-none ${disabled ? "cursor-not-allowed opacity-50" : ""} ${className}`}
    >
      <div className="relative">
        <input
          id={switchId}
          type="checkbox"
          role="switch"
          disabled={disabled}
          className="peer sr-only"
          {...props}
        />
        {/* Track */}
        <div className="h-6 w-11 rounded-full bg-slate-300 transition-colors peer-checked:bg-blue-600 peer-focus-visible:ring-2 peer-focus-visible:ring-blue-500 peer-focus-visible:ring-offset-2 dark:bg-slate-600 dark:peer-checked:bg-blue-500 dark:peer-focus-visible:ring-offset-slate-800" />
        {/* Thumb */}
        <div className="absolute top-0.5 left-0.5 h-5 w-5 rounded-full bg-white shadow-sm transition-transform peer-checked:translate-x-5" />
      </div>
      <div className="min-w-0 flex-1">
        <span className="inline-flex items-center gap-1 text-sm font-medium text-slate-700 dark:text-slate-300">
          {label}
          {tooltip && <Tooltip content={tooltip} />}
        </span>
        {description && (
          <p className="text-xs text-slate-500 dark:text-slate-400">{description}</p>
        )}
      </div>
    </label>
  );
}

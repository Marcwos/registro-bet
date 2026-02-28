import { forwardRef, type InputHTMLAttributes } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

/**
 * Input reutilizable con label y mensaje de error.
 * Usa forwardRef para que react-hook-form pueda conectar su ref al input del DOM.
 */
export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className = "", ...props }, ref) => {
    return (
      <div className="space-y-1.5">
        {label && (
          <label className="block text-sm font-medium text-slate-700">
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={`w-full rounded-lg border px-4 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            error ? "border-rose-500 focus:ring-rose-500" : "border-slate-300"
          } ${className}`}
          {...props}
        />
        {error && <p className="text-sm text-rose-600">{error}</p>}
      </div>
    );
  },
);

Input.displayName = "Input";

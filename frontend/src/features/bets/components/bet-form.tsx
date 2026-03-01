import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod/v4";
import { Input } from "@/shared/components/input";
import { Button } from "@/shared/components/button";
import type { Bet, BetStatus } from "../types";

// ─── Opciones de estado para el selector ────────────────
const statusOptions = [
  { code: "pending", label: "Pendiente", active: "bg-slate-600 text-white ring-2 ring-offset-2 ring-slate-400 dark:ring-offset-slate-800", idle: "border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900/50 dark:text-slate-300 dark:hover:bg-slate-800" },
  { code: "won", label: "Ganada", active: "bg-emerald-600 text-white ring-2 ring-offset-2 ring-emerald-400 dark:ring-offset-slate-800", idle: "border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900/50 dark:text-slate-300 dark:hover:bg-slate-800" },
  { code: "lost", label: "Perdida", active: "bg-rose-600 text-white ring-2 ring-offset-2 ring-rose-400 dark:ring-offset-slate-800", idle: "border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900/50 dark:text-slate-300 dark:hover:bg-slate-800" },
  { code: "void", label: "Nula", active: "bg-gray-500 text-white ring-2 ring-offset-2 ring-gray-400 dark:ring-offset-slate-800", idle: "border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900/50 dark:text-slate-300 dark:hover:bg-slate-800" },
];

// ─── Schema de validacion ───────────────────────────────
const betSchema = z.object({
  stake_amount: z
    .string()
    .min(1, "El monto es requerido")
    .refine((v) => !isNaN(Number(v)) && Number(v) > 0, "Debe ser mayor a 0"),
  odds: z
    .string()
    .min(1, "La cuota es requerida")
    .refine((v) => !isNaN(Number(v)) && Number(v) > 1, "La cuota debe ser mayor a 1"),
  profit_expected: z
    .string()
    .min(1, "La ganancia es requerida")
    .refine((v) => !isNaN(Number(v)) && Number(v) > 0, "Debe ser mayor a 0"),
});

type BetFormData = z.infer<typeof betSchema>;

interface BetFormProps {
  /** Si se pasa, el formulario edita; si no, crea */
  bet?: Bet;
  /** Catálogo de estados — si se pasa junto a bet, muestra selector de estado */
  statuses?: BetStatus[];
  onSubmit: (data: {
    stake_amount: number;
    odds: number;
    profit_expected: number;
    status_code?: string;
  }) => void;
  isLoading: boolean;
  error?: string;
}

export function BetForm({ bet, statuses, onSubmit, isLoading, error }: BetFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<BetFormData>({
    resolver: zodResolver(betSchema),
    defaultValues: {
      stake_amount: bet ? bet.stake_amount : "",
      odds: bet ? bet.odds : "",
      profit_expected: bet ? bet.profit_expected : "",
    },
  });

  // Estado seleccionado (solo en modo edicion) — se inicializa con key del padre
  const currentStatusCode = bet && statuses
    ? (statuses.find((s) => s.id === bet.status_id)?.code ?? "pending")
    : null;
  const [selectedStatus, setSelectedStatus] = useState<string | null>(currentStatusCode);

  const handleFormSubmit = (data: BetFormData) => {
    onSubmit({
      stake_amount: Number(data.stake_amount),
      odds: Number(data.odds),
      profit_expected: Number(data.profit_expected),
      ...(selectedStatus && selectedStatus !== currentStatusCode
        ? { status_code: selectedStatus }
        : {}),
    });
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
      {error && (
        <div className="rounded-lg bg-rose-50 px-4 py-3 text-sm text-rose-600 dark:bg-rose-900/20 dark:text-rose-400">
          {error}
        </div>
      )}

      {/* Monto y Cuota en fila */}
      <div className="grid grid-cols-2 gap-4">
        <Input
          label="Monto apostado"
          type="number"
          step="0.01"
          min="0.01"
          placeholder="0.00"
          error={errors.stake_amount?.message}
          {...register("stake_amount")}
        />
        <Input
          label="Cuota (odds)"
          type="number"
          step="0.01"
          min="1.01"
          placeholder="1.85"
          error={errors.odds?.message}
          {...register("odds")}
        />
      </div>

      {/* Ganancia esperada (ingresada por el usuario) */}
      <Input
        label="Ganancia esperada"
        type="number"
        step="0.01"
        min="0.01"
        placeholder="00.00"
        error={errors.profit_expected?.message}
        {...register("profit_expected")}
      />

      {/* Selector de estado (solo en modo edicion) */}
      {bet && statuses && (
        <div className="space-y-2">
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Estado</label>
          <div className="grid grid-cols-4 gap-2">
            {statusOptions.map((opt) => (
              <button
                key={opt.code}
                type="button"
                onClick={() => setSelectedStatus(opt.code)}
                className={`rounded-lg px-2 py-2 text-xs font-medium transition-all sm:text-sm ${
                  selectedStatus === opt.code ? opt.active : opt.idle
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      )}

      <Button type="submit" className="w-full" disabled={isLoading}>
        {isLoading ? "Guardando..." : bet ? "Guardar cambios" : "Registrar apuesta"}
      </Button>
    </form>
  );
}

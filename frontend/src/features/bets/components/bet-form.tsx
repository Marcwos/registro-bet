import { useState, useEffect, useCallback } from "react";
import { useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod/v4";
import { Zap } from "lucide-react";
import { Input } from "@/shared/components/input";
import { Switch } from "@/shared/components/switch";
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
  title: z.string().optional(),
  stake_amount: z
    .string()
    .min(1, "El monto es requerido")
    .refine((v) => !isNaN(Number(v)) && Number(v) > 0, "Debe ser mayor a 0"),
  odds: z
    .string()
    .min(1, "La cuota es requerida")
    .refine((v) => !isNaN(Number(v)) && Number(v) > 1, "La cuota debe ser mayor a 1"),
  profit_expected: z.string(),
  is_freebet: z.boolean(),
  is_boosted: z.boolean(),
}).superRefine((data, ctx) => {
  if (!data.is_boosted) return;

  const val = Number(data.profit_expected);
  if (data.profit_expected.length === 0 || isNaN(val) || val <= 0) {
    ctx.addIssue({
      code: "custom",
      message: "Ingresa el retorno indicado por tu casa de apuestas",
      path: ["profit_expected"],
    });
    return;
  }

  // El retorno con bonificación siempre debe superar al retorno normal
  const stake = Number(data.stake_amount);
  const odds = Number(data.odds);
  if (!isNaN(stake) && stake > 0 && !isNaN(odds) && odds > 1) {
    const normalReturn = stake * odds;
    if (val <= normalReturn) {
      ctx.addIssue({
        code: "custom",
        message: `La bonificación debe ser mayor al retorno normal ($${normalReturn.toFixed(2)})`,
        path: ["profit_expected"],
      });
    }
  }
});

type BetFormData = z.infer<typeof betSchema>;

interface BetFormProps {
  /** Si se pasa, el formulario edita; si no, crea */
  bet?: Bet;
  /** Catálogo de estados — si se pasa junto a bet, muestra selector de estado */
  statuses?: BetStatus[];
  onSubmit: (data: {
    title?: string;
    stake_amount: number;
    odds: number;
    profit_expected: number;
    status_code?: string;
    is_freebet?: boolean;
    is_boosted?: boolean;
  }) => void;
  isLoading: boolean;
  error?: string;
}

export function BetForm({ bet, statuses, onSubmit, isLoading, error }: BetFormProps) {
  const {
    register,
    handleSubmit,
    control,
    setValue,
    formState: { errors },
  } = useForm<BetFormData>({
    resolver: zodResolver(betSchema),
    defaultValues: {
      title: bet ? bet.title : "",
      stake_amount: bet ? bet.stake_amount : "",
      odds: bet ? bet.odds : "",
      profit_expected: bet ? bet.profit_expected : "",
      is_freebet: bet ? bet.is_freebet : false,
      is_boosted: bet ? bet.is_boosted : false,
    },
  });

  // Observar campos para auto-cálculo en tiempo real
  const stakeValue = useWatch({ control, name: "stake_amount" });
  const oddsValue = useWatch({ control, name: "odds" });
  const isFreebet = useWatch({ control, name: "is_freebet" });
  const isBoosted = useWatch({ control, name: "is_boosted" });
  const profitValue = useWatch({ control, name: "profit_expected" });

  // Flag para saber si el usuario hizo override manual en modo Bono
  const [userOverrideProfit, setUserOverrideProfit] = useState(false);

  // ─── Advertencia en tiempo real para Bonificación ───
  const boostWarning = (() => {
    if (!isBoosted) return null;
    const s = Number(stakeValue);
    const o = Number(oddsValue);
    const p = Number(profitValue);
    if (isNaN(s) || s <= 0 || isNaN(o) || o <= 1 || isNaN(p) || p <= 0) return null;
    const normalReturn = s * o;
    if (p <= normalReturn) {
      return `La bonificación debe ser mayor al retorno normal ($${normalReturn.toFixed(2)})`;
    }
    return null;
  })();

  // ─── Auto-cálculo: Monto × Cuota (retorno total) ───
  const calculateProfit = useCallback((stake: string, odds: string): string => {
    const s = Number(stake);
    const o = Number(odds);
    if (!isNaN(s) && s > 0 && !isNaN(o) && o > 1) {
      return (s * o).toFixed(2);
    }
    return "";
  }, []);

  useEffect(() => {
    // Si Bonificación activa → no auto-calcular, el usuario escribe manualmente
    if (isBoosted) return;

    // Si Bono activo y el usuario ya editó manualmente → respetar su valor
    if (isFreebet && userOverrideProfit) return;

    // Auto-calcular
    const profit = calculateProfit(stakeValue, oddsValue);
    setValue("profit_expected", profit, { shouldValidate: profit.length > 0 });
  }, [stakeValue, oddsValue, isFreebet, isBoosted, userOverrideProfit, calculateProfit, setValue]);

  // ─── Handlers de switches (mutuamente excluyentes) ──
  const handleFreebetToggle = (checked: boolean) => {
    setValue("is_freebet", checked);
    if (checked) {
      // Desactivar bonificación
      setValue("is_boosted", false);
      setUserOverrideProfit(false);
      // Recalcular con valor actual
      const profit = calculateProfit(stakeValue, oddsValue);
      setValue("profit_expected", profit, { shouldValidate: profit.length > 0 });
    } else {
      setUserOverrideProfit(false);
      // Volver a readonly auto-cálculo
      const profit = calculateProfit(stakeValue, oddsValue);
      setValue("profit_expected", profit, { shouldValidate: profit.length > 0 });
    }
  };

  const handleBoostedToggle = (checked: boolean) => {
    setValue("is_boosted", checked);
    if (checked) {
      // Desactivar bono
      setValue("is_freebet", false);
      setUserOverrideProfit(false);
      // Limpiar ganancia → el usuario debe escribirla
      setValue("profit_expected", "", { shouldValidate: false });
    } else {
      // Volver a auto-cálculo
      const profit = calculateProfit(stakeValue, oddsValue);
      setValue("profit_expected", profit, { shouldValidate: profit.length > 0 });
    }
  };

  // Estado seleccionado (solo en modo edicion) — se inicializa con key del padre
  const currentStatusCode = bet && statuses
    ? (statuses.find((s) => s.id === bet.status_id)?.code ?? "pending")
    : null;
  const [selectedStatus, setSelectedStatus] = useState<string | null>(currentStatusCode);

  // ─── Determinar estado visual del campo ganancia ────
  const profitIsReadonly = !isFreebet && !isBoosted;

  const handleFormSubmit = (data: BetFormData) => {
    onSubmit({
      ...(data.title?.trim() ? { title: data.title.trim() } : {}),
      stake_amount: Number(data.stake_amount),
      odds: Number(data.odds),
      profit_expected: Number(data.profit_expected),
      ...(data.is_freebet ? { is_freebet: true } : {}),
      ...(data.is_boosted ? { is_boosted: true } : {}),
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

      {/* Pick / Título */}
      <Input
        label="Pick"
        type="text"
        placeholder="Ej: Gana Equipo, +2.5 goles…"
        {...register("title")}
      />

      {/* Monto y Cuota en fila */}
      <div className="grid grid-cols-2 gap-4">
        <Input
          label="Monto apostado"
          type="number"
          inputMode="decimal"
          step="0.01"
          min="0.01"
          placeholder="0.00"
          error={errors.stake_amount?.message}
          {...register("stake_amount")}
        />
        <Input
          label="Cuota (odds)"
          type="number"
          inputMode="decimal"
          step="0.01"
          min="1.01"
          placeholder="1.85"
          error={errors.odds?.message}
          {...register("odds")}
        />
      </div>

      {/* ─── Switches: Bono / Bonificación ─────────────── */}
      <div className="rounded-lg border border-slate-200 bg-slate-50/50 p-3 dark:border-slate-700 dark:bg-slate-800/50">
        <div className="flex flex-col gap-3 sm:flex-row sm:gap-6">
          <Switch
            label="Bono"
            tooltip="Freebet — si pierdes no se descuenta dinero real de tu balance"
            checked={isFreebet}
            onChange={(e) => handleFreebetToggle(e.target.checked)}
            disabled={isBoosted}
          />
          <Switch
            label="Bonificación"
            tooltip="Boost — tu casa de apuestas te ofrece una ganancia especial"
            checked={isBoosted}
            onChange={(e) => handleBoostedToggle(e.target.checked)}
            disabled={isFreebet}
          />
        </div>
      </div>

      {/* Retorno esperado */}
      <div className="space-y-1.5">
        <label className="block text-xs font-semibold text-slate-600 md:text-sm md:font-medium dark:text-slate-400">
          Retorno esperado
        </label>
        <div className="relative">
          <input
            type="number"
            inputMode="decimal"
            step="0.01"
            min="0.01"
            placeholder={isBoosted ? "Ingresa el retorno de tu casa" : "0.00"}
            readOnly={profitIsReadonly}
            tabIndex={profitIsReadonly ? -1 : undefined}
            aria-invalid={!!errors.profit_expected}
            {...register("profit_expected", {
              onChange: () => {
                if (isFreebet) setUserOverrideProfit(true);
              },
            })}
            className={`w-full rounded-lg border px-4 py-2.5 text-lg font-semibold transition-colors focus:outline-none focus:ring-2 ${
              profitIsReadonly
                ? "cursor-not-allowed border-transparent bg-slate-100 text-emerald-600 dark:bg-slate-700/50 dark:text-emerald-400"
                : "border-slate-300 bg-white text-slate-800 placeholder:text-slate-400 focus:border-blue-500 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100 dark:placeholder:text-slate-500 dark:focus:border-blue-400 dark:focus:ring-blue-400"
            } ${isBoosted ? "pr-10" : ""}`}
          />
          {isBoosted && (
            <span className="pointer-events-none absolute top-1/2 right-3 -translate-y-1/2 text-blue-500 dark:text-blue-400">
              <Zap className="h-4.5 w-4.5" />
            </span>
          )}
        </div>
        {errors.profit_expected && (
          <p className="text-sm text-rose-600 dark:text-rose-400">{errors.profit_expected.message}</p>
        )}
        {!errors.profit_expected && boostWarning && (
          <p className="text-sm text-rose-600 dark:text-rose-400">{boostWarning}</p>
        )}
      </div>

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

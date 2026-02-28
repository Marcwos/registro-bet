import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod/v4";
import { Input } from "@/shared/components/input";
import { Select } from "@/shared/components/select";
import { Button } from "@/shared/components/button";
import { useSports, useCategories } from "../hooks/use-catalogs";
import type { Bet } from "../types";

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
  description: z.string(),
  sport_id: z.string(),
  category_id: z.string(),
});

type BetFormData = z.infer<typeof betSchema>;

interface BetFormProps {
  /** Si se pasa, el formulario edita; si no, crea */
  bet?: Bet;
  onSubmit: (data: {
    stake_amount: number;
    odds: number;
    profit_expected: number;
    description?: string;
    sport_id?: string | null;
    category_id?: string | null;
  }) => void;
  isLoading: boolean;
  error?: string;
}

export function BetForm({ bet, onSubmit, isLoading, error }: BetFormProps) {
  const { data: sports = [] } = useSports();
  const { data: categories = [] } = useCategories();

  const {
    register,
    handleSubmit,
    watch,
    reset,
    formState: { errors },
  } = useForm<BetFormData>({
    resolver: zodResolver(betSchema),
    defaultValues: {
      stake_amount: bet ? bet.stake_amount : "",
      odds: bet ? bet.odds : "",
      description: bet?.description ?? "",
      sport_id: bet?.sport_id ?? "",
      category_id: bet?.category_id ?? "",
    },
  });

  // Resetear cuando cambie la apuesta (crear vs editar)
  useEffect(() => {
    if (bet) {
      reset({
        stake_amount: bet.stake_amount,
        odds: bet.odds,
        description: bet.description ?? "",
        sport_id: bet.sport_id ?? "",
        category_id: bet.category_id ?? "",
      });
    } else {
      reset({
        stake_amount: "",
        odds: "",
        description: "",
        sport_id: "",
        category_id: "",
      });
    }
  }, [bet, reset]);

  // Calcular ganancia esperada en tiempo real
  const stakeAmount = watch("stake_amount");
  const odds = watch("odds");
  const stakeNum = Number(stakeAmount);
  const oddsNum = Number(odds);
  const profitExpected =
    stakeNum > 0 && oddsNum > 1
      ? (stakeNum * (oddsNum - 1)).toFixed(2)
      : "0.00";

  const handleFormSubmit = (data: BetFormData) => {
    onSubmit({
      stake_amount: Number(data.stake_amount),
      odds: Number(data.odds),
      profit_expected: Number(profitExpected),
      description: data.description || undefined,
      sport_id: data.sport_id || null,
      category_id: data.category_id || null,
    });
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
      {error && (
        <div className="rounded-lg bg-rose-50 px-4 py-3 text-sm text-rose-600">
          {error}
        </div>
      )}

      {/* Monto y Cuota en fila */}
      <div className="grid grid-cols-2 gap-4">
        <Input
          label="Monto apostado"
          type="number"
          step="0.01"
          placeholder="100.00"
          error={errors.stake_amount?.message}
          {...register("stake_amount")}
        />
        <Input
          label="Cuota (odds)"
          type="number"
          step="0.01"
          placeholder="1.85"
          error={errors.odds?.message}
          {...register("odds")}
        />
      </div>

      {/* Ganancia esperada (calculada, solo lectura) */}
      <div className="space-y-1.5">
        <label className="block text-sm font-medium text-slate-700">
          Ganancia esperada
        </label>
        <div className="flex items-center rounded-lg border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-medium text-emerald-600">
          $ {profitExpected}
        </div>
      </div>

      {/* Deporte y Categoria */}
      <div className="grid grid-cols-2 gap-4">
        <Select
          label="Deporte"
          placeholder="Opcional"
          options={sports
            .filter((s) => s.is_active)
            .map((s) => ({ value: s.id, label: s.name }))}
          {...register("sport_id")}
        />
        <Select
          label="Categoria"
          placeholder="Opcional"
          options={categories.map((c) => ({ value: c.id, label: c.name }))}
          {...register("category_id")}
        />
      </div>

      {/* Descripcion */}
      <div className="space-y-1.5">
        <label className="block text-sm font-medium text-slate-700">
          Descripcion
        </label>
        <textarea
          rows={2}
          placeholder="Notas sobre la apuesta (opcional)"
          className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          {...register("description")}
        />
      </div>

      <Button type="submit" className="w-full" disabled={isLoading}>
        {isLoading ? "Guardando..." : bet ? "Guardar cambios" : "Registrar apuesta"}
      </Button>
    </form>
  );
}

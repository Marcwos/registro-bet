import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod/v4";
import { Input } from "@/shared/components/input";
import { Button } from "@/shared/components/button";
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
  profit_expected: z
    .string()
    .min(1, "La ganancia es requerida")
    .refine((v) => !isNaN(Number(v)) && Number(v) > 0, "Debe ser mayor a 0"),
});

type BetFormData = z.infer<typeof betSchema>;

interface BetFormProps {
  /** Si se pasa, el formulario edita; si no, crea */
  bet?: Bet;
  onSubmit: (data: {
    stake_amount: number;
    odds: number;
    profit_expected: number;
  }) => void;
  isLoading: boolean;
  error?: string;
}

export function BetForm({ bet, onSubmit, isLoading, error }: BetFormProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<BetFormData>({
    resolver: zodResolver(betSchema),
    defaultValues: {
      stake_amount: bet ? bet.stake_amount : "",
      odds: bet ? bet.odds : "",
      profit_expected: bet ? bet.profit_expected : "",
    },
  });

  // Resetear cuando cambie la apuesta (crear vs editar)
  useEffect(() => {
    if (bet) {
      reset({
        stake_amount: bet.stake_amount,
        odds: bet.odds,
        profit_expected: bet.profit_expected,
      });
    } else {
      reset({
        stake_amount: "",
        odds: "",
        profit_expected: "",
      });
    }
  }, [bet, reset]);

  const handleFormSubmit = (data: BetFormData) => {
    onSubmit({
      stake_amount: Number(data.stake_amount),
      odds: Number(data.odds),
      profit_expected: Number(data.profit_expected),
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

      <Button type="submit" className="w-full" disabled={isLoading}>
        {isLoading ? "Guardando..." : bet ? "Guardar cambios" : "Registrar apuesta"}
      </Button>
    </form>
  );
}

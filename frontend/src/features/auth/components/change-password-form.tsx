import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod/v4";
import { zodResolver } from "@hookform/resolvers/zod";
import { Lock, Eye, EyeOff, Loader2, CheckCircle } from "lucide-react";
import { Button } from "@/shared/components/button";
import { useChangePassword } from "../hooks/use-change-password";
import { getApiErrorMessage } from "@/shared/lib/api-error";

const changePasswordSchema = z
  .object({
    current_password: z.string().min(1, "La contraseña actual es obligatoria"),
    new_password: z
      .string()
      .min(8, "La nueva contraseña debe tener al menos 8 caracteres"),
    confirm_password: z.string().min(1, "Confirma la nueva contraseña"),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: "Las contraseñas no coinciden",
    path: ["confirm_password"],
  });

type ChangePasswordFormData = z.infer<typeof changePasswordSchema>;

export function ChangePasswordForm() {
  const [showCurrent, setShowCurrent] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const mutation = useChangePassword();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ChangePasswordFormData>({
    resolver: zodResolver(changePasswordSchema),
  });

  function onSubmit(data: ChangePasswordFormData) {
    mutation.mutate({
      current_password: data.current_password,
      new_password: data.new_password,
    });
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
      {/* Exito */}
      {mutation.isSuccess && (
        <div className="flex items-center gap-2 rounded-lg bg-emerald-50 p-3 text-sm text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-400">
          <CheckCircle className="h-4 w-4" />
          Contraseña cambiada exitosamente. Cerrando sesion...
        </div>
      )}

      {/* Error del backend */}
      {mutation.isError && (
        <div className="rounded-lg bg-rose-50 p-3 text-sm text-rose-600 dark:bg-rose-900/20 dark:text-rose-400">
          {getApiErrorMessage(mutation.error)}
        </div>
      )}

      {/* Contraseña actual */}
      <div className="space-y-1.5">
        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
          Contraseña actual
        </label>
        <div className="relative">
          <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            {...register("current_password")}
            type={showCurrent ? "text" : "password"}
            placeholder="Tu contraseña actual"
            className={`w-full rounded-lg border py-2.5 pl-10 pr-10 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-slate-900/50 dark:text-slate-100 dark:placeholder:text-slate-500 ${
              errors.current_password
                ? "border-rose-500 focus:ring-rose-500"
                : "border-slate-300 dark:border-slate-700"
            }`}
          />
          <button
            type="button"
            onClick={() => setShowCurrent(!showCurrent)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
          >
            {showCurrent ? (
              <EyeOff className="h-4 w-4" />
            ) : (
              <Eye className="h-4 w-4" />
            )}
          </button>
        </div>
        {errors.current_password && (
          <p className="text-sm text-rose-600 dark:text-rose-400">
            {errors.current_password.message}
          </p>
        )}
      </div>

      {/* Nueva contraseña */}
      <div className="space-y-1.5">
        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
          Nueva contraseña
        </label>
        <div className="relative">
          <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            {...register("new_password")}
            type={showNew ? "text" : "password"}
            placeholder="Minimo 8 caracteres"
            className={`w-full rounded-lg border py-2.5 pl-10 pr-10 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-slate-900/50 dark:text-slate-100 dark:placeholder:text-slate-500 ${
              errors.new_password
                ? "border-rose-500 focus:ring-rose-500"
                : "border-slate-300 dark:border-slate-700"
            }`}
          />
          <button
            type="button"
            onClick={() => setShowNew(!showNew)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
          >
            {showNew ? (
              <EyeOff className="h-4 w-4" />
            ) : (
              <Eye className="h-4 w-4" />
            )}
          </button>
        </div>
        {errors.new_password && (
          <p className="text-sm text-rose-600 dark:text-rose-400">{errors.new_password.message}</p>
        )}
      </div>

      {/* Confirmar nueva contraseña */}
      <div className="space-y-1.5">
        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
          Confirmar nueva contraseña
        </label>
        <div className="relative">
          <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            {...register("confirm_password")}
            type={showConfirm ? "text" : "password"}
            placeholder="Repite la nueva contraseña"
            className={`w-full rounded-lg border py-2.5 pl-10 pr-10 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-slate-900/50 dark:text-slate-100 dark:placeholder:text-slate-500 ${
              errors.confirm_password
                ? "border-rose-500 focus:ring-rose-500"
                : "border-slate-300 dark:border-slate-700"
            }`}
          />
          <button
            type="button"
            onClick={() => setShowConfirm(!showConfirm)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
          >
            {showConfirm ? (
              <EyeOff className="h-4 w-4" />
            ) : (
              <Eye className="h-4 w-4" />
            )}
          </button>
        </div>
        {errors.confirm_password && (
          <p className="text-sm text-rose-600 dark:text-rose-400">
            {errors.confirm_password.message}
          </p>
        )}
      </div>

      {/* Info sobre sesiones */}
      <p className="text-xs text-slate-400 dark:text-slate-500">
        Al cambiar tu contraseña, se cerraran todas tus sesiones activas.
      </p>

      {/* Submit */}
      <Button type="submit" disabled={mutation.isPending || mutation.isSuccess}>
        {mutation.isPending ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Cambiando...
          </>
        ) : (
          "Cambiar contraseña"
        )}
      </Button>
    </form>
  );
}

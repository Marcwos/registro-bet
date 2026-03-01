import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod/v4";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useSearchParams, useNavigate } from "react-router";
import { Lock, Eye, EyeOff, Loader2, CheckCircle } from "lucide-react";
import { useResetPassword } from "../hooks/use-recover-password";
import { AuthHeader } from "../components/auth-header";
import { Card } from "@/shared/components/card";
import { Button } from "@/shared/components/button";
import { getApiErrorMessage } from "@/shared/lib/api-error";

const resetSchema = z
  .object({
    code: z
      .string()
      .length(6, "El codigo debe tener 6 digitos")
      .regex(/^\d+$/, "Solo digitos"),
    new_password: z
      .string()
      .min(8, "La contrasena debe tener al menos 8 caracteres"),
    confirmPassword: z.string().min(1, "Confirma tu contrasena"),
  })
  .refine((data) => data.new_password === data.confirmPassword, {
    message: "Las contrasenas no coinciden",
    path: ["confirmPassword"],
  });

type ResetFormData = z.infer<typeof resetSchema>;

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const email = searchParams.get("email") ?? "";
  const navigate = useNavigate();

  const [showPassword, setShowPassword] = useState(false);
  const [success, setSuccess] = useState(false);
  const resetMutation = useResetPassword();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ResetFormData>({
    resolver: zodResolver(resetSchema),
  });

  function onSubmit(data: ResetFormData) {
    resetMutation.mutate(
      { email, code: data.code, new_password: data.new_password },
      {
        onSuccess: () => setSuccess(true),
      },
    );
  }

  if (success) {
    return (
      <>
        <AuthHeader
          title="Contrasena actualizada"
          subtitle="Tu contrasena ha sido cambiada exitosamente"
        />
        <Card className="text-center">
          <CheckCircle className="mx-auto h-12 w-12 text-emerald-500" />
          <p className="mt-4 text-sm text-slate-600 dark:text-slate-400">
            Ya puedes iniciar sesion con tu nueva contrasena.
          </p>
          <Button
            onClick={() => navigate("/login")}
            className="mt-6 w-full"
          >
            Ir al login
          </Button>
        </Card>
      </>
    );
  }

  return (
    <>
      <AuthHeader
        title="Nueva contrasena"
        subtitle={
          email
            ? `Ingresa el codigo que enviamos a ${email}`
            : "Ingresa el codigo y tu nueva contrasena"
        }
      />

      <Card>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          {resetMutation.isError && (
            <div className="rounded-lg bg-rose-50 p-3 text-sm text-rose-600 dark:bg-rose-900/20 dark:text-rose-400">
              {getApiErrorMessage(resetMutation.error)}
            </div>
          )}

          {/* Codigo */}
          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
              Codigo de recuperacion
            </label>
            <input
              {...register("code")}
              type="text"
              inputMode="numeric"
              maxLength={6}
              placeholder="123456"
              className={`w-full rounded-lg border px-4 py-2.5 text-center text-lg font-semibold tracking-widest text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-slate-900/50 dark:text-slate-100 dark:placeholder:text-slate-500 ${
                errors.code
                  ? "border-rose-500 focus:ring-rose-500"
                  : "border-slate-300 dark:border-slate-700"
              }`}
            />
            {errors.code && (
              <p className="text-sm text-rose-600 dark:text-rose-400">{errors.code.message}</p>
            )}
          </div>

          {/* Nueva contrasena */}
          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
              Nueva contrasena
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                {...register("new_password")}
                type={showPassword ? "text" : "password"}
                placeholder="Minimo 8 caracteres"
                className={`w-full rounded-lg border py-2.5 pl-10 pr-10 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-slate-900/50 dark:text-slate-100 dark:placeholder:text-slate-500 ${
                  errors.new_password
                    ? "border-rose-500 focus:ring-rose-500"
                    : "border-slate-300 dark:border-slate-700"
                }`}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              >
                {showPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </button>
            </div>
            {errors.new_password && (
              <p className="text-sm text-rose-600 dark:text-rose-400">
                {errors.new_password.message}
              </p>
            )}
          </div>

          {/* Confirmar contrasena */}
          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
              Confirmar contrasena
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                {...register("confirmPassword")}
                type={showPassword ? "text" : "password"}
                placeholder="Repite tu contrasena"
                className={`w-full rounded-lg border py-2.5 pl-10 pr-4 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-slate-900/50 dark:text-slate-100 dark:placeholder:text-slate-500 ${
                  errors.confirmPassword
                    ? "border-rose-500 focus:ring-rose-500"
                    : "border-slate-300 dark:border-slate-700"
                }`}
              />
            </div>
            {errors.confirmPassword && (
              <p className="text-sm text-rose-600 dark:text-rose-400">
                {errors.confirmPassword.message}
              </p>
            )}
          </div>

          <Button
            type="submit"
            disabled={resetMutation.isPending}
            className="w-full"
          >
            {resetMutation.isPending ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Cambiando contrasena...
              </>
            ) : (
              "Cambiar contrasena"
            )}
          </Button>
        </form>
      </Card>

      <p className="mt-6 text-center text-sm text-slate-500 dark:text-slate-400">
        <Link
          to="/login"
          className="font-medium text-blue-600 hover:text-blue-700"
        >
          Volver al login
        </Link>
      </p>
    </>
  );
}

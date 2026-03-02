import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod/v4";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useNavigate } from "react-router";
import { Mail, Lock, Eye, EyeOff, Loader2 } from "lucide-react";
import { useLogin } from "../hooks/use-login";
import { AuthHeader } from "../components/auth-header";
import { Card } from "@/shared/components/card";
import { Button } from "@/shared/components/button";
import { getApiErrorMessage } from "@/shared/lib/api-error";
import axios from "axios";

/**
 * Esquema de validacion con Zod.
 * Define las reglas que deben cumplir los campos ANTES de enviar al backend.
 */
const loginSchema = z.object({
  email: z.email("Ingresa un email valido"),
  password: z.string().min(1, "La contrasena es obligatoria"),
  remember_me: z.boolean(),
});

type LoginFormData = z.infer<typeof loginSchema>;

export function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const loginMutation = useLogin();
  const navigate = useNavigate();

  /**
   * react-hook-form maneja:
   * - register: conecta cada input al formulario
   * - handleSubmit: valida con Zod antes de llamar onSubmit
   * - formState.errors: errores de validacion por campo
   */
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      remember_me: false,
    },
  });

  function onSubmit(data: LoginFormData) {
    loginMutation.mutate(data, {
      onError: (error) => {
        // Si el email no esta verificado, redirigir a verificacion
        if (
          axios.isAxiosError(error) &&
          error.response?.status === 403 &&
          error.response.data?.user_id
        ) {
          const { user_id, email } = error.response.data;
          navigate(`/verify-email?userId=${user_id}&email=${encodeURIComponent(email)}`);
        }
      },
    });
  }

  return (
    <>
      <AuthHeader
        title="Iniciar sesion"
        subtitle="Ingresa tus credenciales para acceder"
      />

      <Card>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          {/* Error global del backend (credenciales invalidas, email no verificado, etc) */}
          {loginMutation.isError && (
            <div className="rounded-lg bg-rose-50 p-3 text-sm text-rose-600 dark:bg-rose-900/20 dark:text-rose-400">
              {getApiErrorMessage(loginMutation.error)}
            </div>
          )}

          {/* Email */}
          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
              Email
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                {...register("email")}
                type="email"
                placeholder="nombre@correo.com"
                className={`w-full rounded-lg border py-2.5 pl-10 pr-4 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-slate-900/50 dark:text-slate-100 dark:placeholder:text-slate-500 ${
                  errors.email
                    ? "border-rose-500 focus:ring-rose-500"
                    : "border-slate-300 dark:border-slate-700"
                }`}
              />
            </div>
            {errors.email && (
              <p className="text-sm text-rose-600 dark:text-rose-400">{errors.email.message}</p>
            )}
          </div>

          {/* Password */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
                Contrasena
              </label>
              <Link
                to="/forgot-password"
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                Olvidaste tu contrasena?
              </Link>
            </div>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                {...register("password")}
                type={showPassword ? "text" : "password"}
                placeholder="Tu contrasena"
                className={`w-full rounded-lg border py-2.5 pl-10 pr-10 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-slate-900/50 dark:text-slate-100 dark:placeholder:text-slate-500 ${
                  errors.password
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
            {errors.password && (
              <p className="text-sm text-rose-600 dark:text-rose-400">
                {errors.password.message}
              </p>
            )}
          </div>

          {/* Recordarme */}
          <div className="flex items-center gap-2">
            <input
              {...register("remember_me")}
              type="checkbox"
              id="remember_me"
              className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500 dark:border-slate-600"
            />
            <label
              htmlFor="remember_me"
              className="text-sm text-slate-600 dark:text-slate-400 select-none"
            >
              Recordarme
            </label>
          </div>

          {/* Submit */}
          <Button
            type="submit"
            disabled={loginMutation.isPending}
            className="w-full"
          >
            {loginMutation.isPending ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Ingresando...
              </>
            ) : (
              "Iniciar sesion"
            )}
          </Button>
        </form>
      </Card>

      {/* Footer */}
      <p className="mt-6 text-center text-sm text-slate-500 dark:text-slate-400">
        No tienes cuenta?{" "}
        <Link
          to="/register"
          className="font-medium text-blue-600 hover:text-blue-700"
        >
          Crear una cuenta
        </Link>
      </p>
    </>
  );
}

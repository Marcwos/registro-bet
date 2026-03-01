import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod/v4";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useNavigate } from "react-router";
import { Mail, Lock, Eye, EyeOff, Loader2 } from "lucide-react";
import { useRegister } from "../hooks/use-register";
import { AuthHeader } from "../components/auth-header";
import { Card } from "@/shared/components/card";
import { Button } from "@/shared/components/button";
import { getApiErrorMessage } from "@/shared/lib/api-error";

const registerSchema = z
  .object({
    email: z.email("Ingresa un email valido"),
    password: z
      .string()
      .min(8, "La contrasena debe tener al menos 8 caracteres"),
    confirmPassword: z.string().min(1, "Confirma tu contrasena"),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Las contrasenas no coinciden",
    path: ["confirmPassword"],
  });

type RegisterFormData = z.infer<typeof registerSchema>;

export function RegisterPage() {
  const [showPassword, setShowPassword] = useState(false);
  const registerMutation = useRegister();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  function onSubmit(data: RegisterFormData) {
    registerMutation.mutate(
      { email: data.email, password: data.password },
      {
        onSuccess: (response) => {
          // Redirige a verificacion con el user_id para poder enviar el codigo
          navigate(`/verify-email?userId=${response.id}&email=${response.email}`);
        },
      },
    );
  }

  return (
    <>
      <AuthHeader
        title="Crear cuenta"
        subtitle="Registrate para empezar a trackear tus apuestas"
      />

      <Card>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          {registerMutation.isError && (
            <div className="rounded-lg bg-rose-50 p-3 text-sm text-rose-600 dark:bg-rose-900/20 dark:text-rose-400">
              {getApiErrorMessage(registerMutation.error)}
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
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
              Contrasena
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                {...register("password")}
                type={showPassword ? "text" : "password"}
                placeholder="Minimo 8 caracteres"
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

          {/* Confirm Password */}
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

          {/* Submit */}
          <Button
            type="submit"
            disabled={registerMutation.isPending}
            className="w-full"
          >
            {registerMutation.isPending ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Creando cuenta...
              </>
            ) : (
              "Crear cuenta"
            )}
          </Button>
        </form>
      </Card>

      <p className="mt-6 text-center text-sm text-slate-500 dark:text-slate-400">
        Ya tienes cuenta?{" "}
        <Link
          to="/login"
          className="font-medium text-blue-600 hover:text-blue-700"
        >
          Iniciar sesion
        </Link>
      </p>
    </>
  );
}

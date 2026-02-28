import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod/v4";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link } from "react-router";
import { Mail, Loader2, CheckCircle } from "lucide-react";
import { useRecoverPassword } from "../hooks/use-recover-password";
import { AuthHeader } from "../components/auth-header";
import { Card } from "@/shared/components/card";
import { Button } from "@/shared/components/button";
import { getApiErrorMessage } from "@/shared/lib/api-error";

const forgotSchema = z.object({
  email: z.email("Ingresa un email valido"),
});

type ForgotFormData = z.infer<typeof forgotSchema>;

export function ForgotPasswordPage() {
  const [sent, setSent] = useState(false);
  const [email, setEmail] = useState("");
  const recoverMutation = useRecoverPassword();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotFormData>({
    resolver: zodResolver(forgotSchema),
  });

  function onSubmit(data: ForgotFormData) {
    setEmail(data.email);
    recoverMutation.mutate(data, {
      onSuccess: () => setSent(true),
    });
  }

  // Pantalla de confirmacion
  if (sent) {
    return (
      <>
        <AuthHeader
          title="Revisa tu email"
          subtitle={`Si ${email} esta registrado, enviamos un codigo de recuperacion`}
        />
        <Card className="text-center">
          <CheckCircle className="mx-auto h-12 w-12 text-emerald-500" />
          <p className="mt-4 text-sm text-slate-600">
            Revisa tu bandeja de entrada y usa el codigo para resetear tu
            contrasena.
          </p>
          <Link
            to={`/reset-password?email=${encodeURIComponent(email)}`}
            className="mt-6 inline-block"
          >
            <Button className="w-full">Tengo el codigo</Button>
          </Link>
        </Card>
        <p className="mt-6 text-center text-sm text-slate-500">
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

  return (
    <>
      <AuthHeader
        title="Recuperar contrasena"
        subtitle="Ingresa tu email y te enviaremos un codigo de recuperacion"
      />

      <Card>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          {recoverMutation.isError && (
            <div className="rounded-lg bg-rose-50 p-3 text-sm text-rose-600">
              {getApiErrorMessage(recoverMutation.error)}
            </div>
          )}

          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-slate-700">
              Email
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                {...register("email")}
                type="email"
                placeholder="nombre@correo.com"
                className={`w-full rounded-lg border py-2.5 pl-10 pr-4 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.email
                    ? "border-rose-500 focus:ring-rose-500"
                    : "border-slate-300"
                }`}
              />
            </div>
            {errors.email && (
              <p className="text-sm text-rose-600">{errors.email.message}</p>
            )}
          </div>

          <Button
            type="submit"
            disabled={recoverMutation.isPending}
            className="w-full"
          >
            {recoverMutation.isPending ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Enviando...
              </>
            ) : (
              "Enviar codigo"
            )}
          </Button>
        </form>
      </Card>

      <p className="mt-6 text-center text-sm text-slate-500">
        Recuerdas tu contrasena?{" "}
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

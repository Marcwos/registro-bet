import { useEffect, useRef, useState } from "react";
import { useSearchParams, Link, useNavigate } from "react-router";
import { CheckCircle, Loader2, RotateCw } from "lucide-react";
import {
  useSendVerification,
  useVerifyEmail,
} from "../hooks/use-verify-email";
import { AuthHeader } from "../components/auth-header";
import { Card } from "@/shared/components/card";
import { Button } from "@/shared/components/button";
import { getApiErrorMessage } from "@/shared/lib/api-error";

const CODE_LENGTH = 6;

export function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const userId = searchParams.get("userId") ?? "";
  const email = searchParams.get("email") ?? "";
  const navigate = useNavigate();

  const [code, setCode] = useState<string[]>(Array(CODE_LENGTH).fill(""));
  const [verified, setVerified] = useState(false);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);
  const hasSentRef = useRef(false);

  const verifyMutation = useVerifyEmail();
  const sendMutation = useSendVerification();

  // Enviar codigo automaticamente al cargar la pagina
  useEffect(() => {
    if (userId && !hasSentRef.current) {
      hasSentRef.current = true;
      sendMutation.mutate({ user_id: userId });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  // Maneja input de cada digito
  function handleChange(index: number, value: string) {
    // Solo acepta digitos
    if (value && !/^\d$/.test(value)) return;

    const newCode = [...code];
    newCode[index] = value;
    setCode(newCode);

    // Auto-avanza al siguiente input
    if (value && index < CODE_LENGTH - 1) {
      inputRefs.current[index + 1]?.focus();
    }

    // Si se completo el codigo, verificar automaticamente
    if (newCode.every((d) => d !== "")) {
      verifyMutation.mutate(
        { user_id: userId, code: newCode.join("") },
        {
          onSuccess: () => setVerified(true),
        },
      );
    }
  }

  // Maneja tecla Backspace para retroceder
  function handleKeyDown(index: number, e: React.KeyboardEvent) {
    if (e.key === "Backspace" && !code[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  }

  // Maneja pegar codigo completo
  function handlePaste(e: React.ClipboardEvent) {
    e.preventDefault();
    const pasted = e.clipboardData.getData("text").replace(/\D/g, "");
    if (pasted.length !== CODE_LENGTH) return;

    const newCode = pasted.split("");
    setCode(newCode);
    inputRefs.current[CODE_LENGTH - 1]?.focus();

    verifyMutation.mutate(
      { user_id: userId, code: pasted },
      {
        onSuccess: () => setVerified(true),
      },
    );
  }

  function handleResend() {
    sendMutation.mutate({ user_id: userId });
  }

  // Pantalla de exito
  if (verified) {
    return (
      <>
        <AuthHeader
          title="Email verificado"
          subtitle="Tu cuenta ha sido verificada exitosamente"
        />
        <Card className="text-center">
          <CheckCircle className="mx-auto h-12 w-12 text-emerald-500" />
          <p className="mt-4 text-sm text-slate-600 dark:text-slate-400">
            Ya puedes iniciar sesion con tu cuenta.
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
        title="Verifica tu email"
        subtitle={
          email
            ? `Enviamos un codigo de 6 digitos a ${email}`
            : "Ingresa el codigo de verificacion que enviamos a tu email"
        }
      />

      <Card>
        <div className="space-y-5">
          {/* Error */}
          {verifyMutation.isError && (
            <div className="rounded-lg bg-rose-50 p-3 text-sm text-rose-600 dark:bg-rose-900/20 dark:text-rose-400">
              {getApiErrorMessage(verifyMutation.error)}
            </div>
          )}

          {/* Inputs de codigo (6 digitos) */}
          <div className="flex justify-center gap-3">
            {code.map((digit, i) => (
              <input
                key={i}
                ref={(el) => {
                  inputRefs.current[i] = el;
                }}
                type="text"
                inputMode="numeric"
                maxLength={1}
                value={digit}
                onChange={(e) => handleChange(i, e.target.value)}
                onKeyDown={(e) => handleKeyDown(i, e)}
                onPaste={i === 0 ? handlePaste : undefined}
                className="h-12 w-12 rounded-lg border border-slate-300 text-center text-lg font-semibold text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-900/50 dark:text-slate-100"
                disabled={verifyMutation.isPending}
              />
            ))}
          </div>

          {/* Verificar manualmente */}
          <Button
            onClick={() =>
              verifyMutation.mutate(
                { user_id: userId, code: code.join("") },
                { onSuccess: () => setVerified(true) },
              )
            }
            disabled={
              verifyMutation.isPending || code.some((d) => d === "")
            }
            className="w-full"
          >
            {verifyMutation.isPending ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Verificando...
              </>
            ) : (
              "Verificar"
            )}
          </Button>

          {/* Reenviar codigo */}
          <div className="text-center">
            <button
              type="button"
              onClick={handleResend}
              disabled={sendMutation.isPending}
              className="inline-flex items-center gap-1.5 text-sm text-blue-600 hover:text-blue-700 disabled:opacity-50"
            >
              {sendMutation.isPending ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <RotateCw className="h-3.5 w-3.5" />
              )}
              Reenviar codigo
            </button>
            {sendMutation.isSuccess && (
              <p className="mt-2 text-sm text-emerald-600 dark:text-emerald-400">
                Codigo reenviado exitosamente
              </p>
            )}
            {sendMutation.isError && (
              <p className="mt-2 text-sm text-rose-600 dark:text-rose-400">
                {getApiErrorMessage(sendMutation.error)}
              </p>
            )}
          </div>
        </div>
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

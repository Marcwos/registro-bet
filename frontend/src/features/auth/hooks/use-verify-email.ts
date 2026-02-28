import { useMutation } from "@tanstack/react-query";
import { sendVerificationEmail, verifyEmail } from "../api";

/**
 * Hook para enviar el codigo de verificacion por email.
 */
export function useSendVerification() {
  return useMutation({
    mutationFn: sendVerificationEmail,
  });
}

/**
 * Hook para verificar el email con el codigo de 6 digitos.
 */
export function useVerifyEmail() {
  return useMutation({
    mutationFn: verifyEmail,
  });
}

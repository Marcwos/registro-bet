import { useMutation } from "@tanstack/react-query";
import { recoverPassword, resetPassword } from "../api";

/**
 * Hook para solicitar codigo de recuperacion de contrasena.
 */
export function useRecoverPassword() {
  return useMutation({
    mutationFn: recoverPassword,
  });
}

/**
 * Hook para resetear la contrasena con codigo + nueva contrasena.
 */
export function useResetPassword() {
  return useMutation({
    mutationFn: resetPassword,
  });
}

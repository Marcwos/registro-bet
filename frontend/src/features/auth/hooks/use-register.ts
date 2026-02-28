import { useMutation } from "@tanstack/react-query";
import { registerUser } from "../api";

/**
 * Hook para registro.
 * Llama al backend y retorna la data del usuario creado.
 * La pagina de registro se encarga de redirigir a verificacion.
 */
export function useRegister() {
  return useMutation({
    mutationFn: registerUser,
  });
}

import { useMutation } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { changePassword } from "../api";
import { useAuthStore } from "./use-auth-store";
import { getApiErrorMessage } from "@/shared/lib/api-error";
import type { ChangePasswordRequest } from "../types";

/** Cambia la contraseña y fuerza logout (el backend revoca todas las sesiones) */
export function useChangePassword() {
  const logout = useAuthStore((state) => state.logout);

  return useMutation({
    mutationFn: (data: ChangePasswordRequest) => changePassword(data),
    onSuccess: () => {
      toast.success("Contraseña cambiada exitosamente");
      // El backend revoca todas las sesiones al cambiar la contraseña,
      // asi que limpiamos tokens locales tras un breve delay para mostrar feedback
      setTimeout(() => logout(), 2000);
    },
    onError: (error) => {
      toast.error(getApiErrorMessage(error));
    },
  });
}

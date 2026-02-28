import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router";
import { useAuthStore } from "./use-auth-store";
import { loginUser, logoutUser } from "../api";

/**
 * Hook para login.
 * Llama al backend, guarda tokens en el store, y redirige al dashboard.
 */
export function useLogin() {
  const login = useAuthStore((state) => state.login);
  const navigate = useNavigate();

  return useMutation({
    mutationFn: loginUser,
    onSuccess: (data) => {
      login(
        { id: data.user_id, email: data.email, role: data.role },
        data.access_token,
        data.refresh_token,
      );
      navigate("/", { replace: true });
    },
  });
}

/**
 * Hook para logout.
 * Revoca el refresh token en el backend y limpia el estado local.
 */
export function useLogout() {
  const logout = useAuthStore((state) => state.logout);
  const navigate = useNavigate();

  return useMutation({
    mutationFn: () => {
      const refreshToken = localStorage.getItem("refresh_token");
      if (!refreshToken) return Promise.resolve();
      return logoutUser(refreshToken);
    },
    onSettled: () => {
      // Siempre limpiar, aunque el backend falle
      logout();
      navigate("/login", { replace: true });
    },
  });
}

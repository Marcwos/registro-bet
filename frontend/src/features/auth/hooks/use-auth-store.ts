import axios from "axios";
import { create } from "zustand";
import { env } from "@/config/env";
import type { User } from "../types";

/**
 * Store global de autenticacion (Zustand).
 *
 * Maneja el estado del usuario logueado y los tokens JWT.
 * Cualquier componente puede leer `isAuthenticated` o `user`
 * y se re-renderiza automaticamente cuando cambian.
 */
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;

  /** Guarda tokens y datos del usuario tras login exitoso */
  login: (user: User, accessToken: string, refreshToken: string) => void;

  /** Limpia tokens y estado, manda al login */
  logout: () => void;

  /** Recupera sesion desde localStorage al cargar la app */
  hydrate: () => void;
}

/**
 * Extrae los datos del usuario desde el payload de un access token JWT.
 * El payload usa "sub" como user_id, "email" y "role".
 */
function getUserFromToken(payload: Record<string, string>): User {
  return {
    id: payload.sub,
    email: payload.email,
    role: payload.role,
  };
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,

  login: (user, accessToken, refreshToken) => {
    localStorage.setItem("access_token", accessToken);
    localStorage.setItem("refresh_token", refreshToken);
    set({ user, isAuthenticated: true });
  },

  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    set({ user: null, isAuthenticated: false });
  },

  hydrate: () => {
    const token = localStorage.getItem("access_token");
    const refreshToken = localStorage.getItem("refresh_token");

    // Sin tokens, no hay sesion que recuperar
    if (!token && !refreshToken) return;

    try {
      if (token) {
        // JWT = header.payload.signature — decodificamos el payload
        const payload = JSON.parse(atob(token.split(".")[1]));

        // Si el access token aun es valido, restauramos la sesion directamente
        if (payload.exp * 1000 > Date.now()) {
          set({
            user: getUserFromToken(payload),
            isAuthenticated: true,
          });
          return;
        }
      }

      // Access token expirado o ausente: intentar renovar con refresh token
      if (!refreshToken) {
        localStorage.removeItem("access_token");
        return;
      }

      // Llamada asincrona al endpoint de refresh (fire-and-forget dentro del sync hydrate)
      axios
        .post(`${env.API_URL}/users/refresh/`, {
          refresh_token: refreshToken,
        })
        .then(({ data }) => {
          localStorage.setItem("access_token", data.access_token);
          localStorage.setItem("refresh_token", data.refresh_token);

          const payload = JSON.parse(
            atob(data.access_token.split(".")[1]),
          );
          set({
            user: getUserFromToken(payload),
            isAuthenticated: true,
          });
        })
        .catch(() => {
          // Refresh tambien fallo — sesion completamente invalida
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          set({ user: null, isAuthenticated: false });
        });
    } catch {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    }
  },
}));

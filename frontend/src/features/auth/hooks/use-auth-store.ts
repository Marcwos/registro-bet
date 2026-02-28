import { create } from "zustand";
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
    if (!token) return;

    try {
      // JWT = header.payload.signature — decodificamos el payload
      const payload = JSON.parse(atob(token.split(".")[1]));

      // Verifica que no este expirado (exp viene en segundos, Date.now en ms)
      if (payload.exp * 1000 < Date.now()) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        return;
      }

      set({
        user: {
          id: payload.user_id,
          email: payload.email,
          role: payload.role,
        },
        isAuthenticated: true,
      });
    } catch {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    }
  },
}));

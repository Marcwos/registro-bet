import axios from "axios";
import { env } from "@/config/env";

/**
 * Instancia de Axios configurada para la API.
 * - baseURL apunta al backend Django
 * - Interceptor de request: inyecta el JWT en cada peticion
 * - Interceptor de response: intenta refresh automatico si el token expira (401)
 */
export const httpClient = axios.create({
  baseURL: env.API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// --- Interceptor de REQUEST ---
// Antes de cada peticion, agrega el header Authorization con el token
httpClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// --- Interceptor de RESPONSE ---
// Si el backend responde 401 (token expirado), intenta renovar con refresh token
httpClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Solo intenta refresh si es 401 y no es un reintento
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem("refresh_token");
      if (!refreshToken) {
        clearTokensAndRedirect();
        return Promise.reject(error);
      }

      try {
        // Usa axios puro (no httpClient) para evitar loop infinito de interceptores
        const { data } = await axios.post(`${env.API_URL}/users/refresh/`, {
          refresh_token: refreshToken,
        });

        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("refresh_token", data.refresh_token);

        // Reintenta la peticion original con el nuevo token
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return httpClient(originalRequest);
      } catch {
        clearTokensAndRedirect();
        return Promise.reject(error);
      }
    }

    return Promise.reject(error);
  },
);

function clearTokensAndRedirect() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  window.location.href = "/login";
}

/**
 * Variables de entorno centralizadas.
 * En Vite, solo las variables con prefijo VITE_ son accesibles en el navegador.
 */
export const env = {
  API_URL: import.meta.env.VITE_API_URL || "http://localhost:8000/api",
} as const;

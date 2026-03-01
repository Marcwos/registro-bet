import { QueryClient } from "@tanstack/react-query";

/**
 * QueryClient es el "cerebro" de TanStack Query.
 * Maneja cache de datos del servidor, refetch automatico, y reintentos.
 */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1, // Reintenta 1 vez si falla una peticion
      staleTime: 5 * 60 * 1000, // Datos "frescos" por 5 min (no refetch innecesario)
      refetchOnWindowFocus: false, // No refetch al volver a la pestana
    },
  },
});

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useEffect } from "react";
import { Toaster } from "react-hot-toast";
import { useAuthStore } from "@/features/auth/hooks/use-auth-store";
import { useTheme } from "@/shared/hooks/use-theme";

/**
 * QueryClient es el "cerebro" de TanStack Query.
 * Maneja cache de datos del servidor, refetch automatico, y reintentos.
 */
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1, // Reintenta 1 vez si falla una peticion
      staleTime: 5 * 60 * 1000, // Datos "frescos" por 5 min (no refetch innecesario)
      refetchOnWindowFocus: false, // No refetch al volver a la pestana
    },
  },
});

/**
 * Envuelve toda la app con los providers necesarios:
 * - QueryClientProvider: para que TanStack Query funcione en cualquier componente
 * - Hydrate: recupera la sesion de localStorage al cargar la app
 */
export function AppProviders({ children }: { children: React.ReactNode }) {
  const hydrate = useAuthStore((state) => state.hydrate);

  // Aplica el tema (dark/light) globalmente al cargar la app
  useTheme();

  useEffect(() => {
    hydrate();
  }, [hydrate]);

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            borderRadius: "12px",
            padding: "12px 16px",
            fontSize: "14px",
          },
          success: { iconTheme: { primary: "#059669", secondary: "#fff" } },
          error: { iconTheme: { primary: "#e11d48", secondary: "#fff" } },
        }}
      />
    </QueryClientProvider>
  );
}

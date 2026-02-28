import { AppProviders } from "./providers";
import { AppRouter } from "./router";

/**
 * Componente raiz de la aplicacion.
 * Envuelve el router con los providers globales (TanStack Query, Auth).
 */
export default function App() {
  return (
    <AppProviders>
      <AppRouter />
    </AppProviders>
  );
}

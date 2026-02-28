import { useQuery } from "@tanstack/react-query";
import { fetchStatuses, fetchSports, fetchCategories } from "../api";

/** Lista todos los estados de apuesta (pending, won, lost, void) */
export function useStatuses() {
  return useQuery({
    queryKey: ["catalogs", "statuses"],
    queryFn: fetchStatuses,
    staleTime: Infinity, // Los catalogos no cambian frecuentemente
  });
}

/** Lista todos los deportes activos */
export function useSports() {
  return useQuery({
    queryKey: ["catalogs", "sports"],
    queryFn: fetchSports,
    staleTime: Infinity,
  });
}

/** Lista todas las categorias de apuesta */
export function useCategories() {
  return useQuery({
    queryKey: ["catalogs", "categories"],
    queryFn: fetchCategories,
    staleTime: Infinity,
  });
}

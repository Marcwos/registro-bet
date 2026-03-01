import { useQuery } from "@tanstack/react-query";
import { fetchBets, fetchBetHistory, fetchDailyBalance, fetchTotalBalance } from "../api";

/** Lista todas las apuestas del usuario autenticado */
export function useBets() {
  return useQuery({
    queryKey: ["bets"],
    queryFn: fetchBets,
    staleTime: 0, // Siempre refetch al montar
  });
}

/** Balance del dia (o de una fecha especifica) */
export function useDailyBalance(date?: string) {
  return useQuery({
    queryKey: ["balance", "daily", date],
    queryFn: () => fetchDailyBalance(date),
    staleTime: 0, // Siempre refetch al montar — el balance cambia con cada apuesta
  });
}

/** Balance total historico */
export function useTotalBalance() {
  return useQuery({
    queryKey: ["balance", "total"],
    queryFn: fetchTotalBalance,
  });
}

/** Historial de apuestas por rango de fechas */
export function useBetHistory(startDate: string, endDate: string) {
  return useQuery({
    queryKey: ["bets", "history", startDate, endDate],
    queryFn: () => fetchBetHistory(startDate, endDate),
    enabled: !!startDate && !!endDate,
  });
}

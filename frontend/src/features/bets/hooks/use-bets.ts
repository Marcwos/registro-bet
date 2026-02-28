import { useQuery } from "@tanstack/react-query";
import { fetchBets, fetchDailyBalance, fetchTotalBalance } from "../api";

/** Lista todas las apuestas del usuario autenticado */
export function useBets() {
  return useQuery({
    queryKey: ["bets"],
    queryFn: fetchBets,
  });
}

/** Balance del dia (o de una fecha especifica) */
export function useDailyBalance(date?: string) {
  return useQuery({
    queryKey: ["balance", "daily", date],
    queryFn: () => fetchDailyBalance(date),
  });
}

/** Balance total historico */
export function useTotalBalance() {
  return useQuery({
    queryKey: ["balance", "total"],
    queryFn: fetchTotalBalance,
  });
}

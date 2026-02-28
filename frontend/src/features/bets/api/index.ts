import { httpClient } from "@/shared/lib/http-client";
import type {
  Bet,
  BetCategory,
  BetStatus,
  ChangeBetStatusRequest,
  CreateBetRequest,
  DailyBalance,
  Sport,
  TotalBalance,
  UpdateBetRequest,
} from "../types";

// ─── Bets CRUD ──────────────────────────────────────────

export async function fetchBets(): Promise<Bet[]> {
  const response = await httpClient.get<Bet[]>("/bets/");
  return response.data;
}

export async function createBet(data: CreateBetRequest): Promise<Bet> {
  const response = await httpClient.post<Bet>("/bets/", data);
  return response.data;
}

export async function updateBet(id: string, data: UpdateBetRequest): Promise<Bet> {
  const response = await httpClient.patch<Bet>(`/bets/${id}/`, data);
  return response.data;
}

export async function deleteBet(id: string): Promise<void> {
  await httpClient.delete(`/bets/${id}/`);
}

export async function changeBetStatus(id: string, data: ChangeBetStatusRequest): Promise<Bet> {
  const response = await httpClient.patch<Bet>(`/bets/${id}/status/`, data);
  return response.data;
}

// ─── Catalogos ──────────────────────────────────────────

export async function fetchStatuses(): Promise<BetStatus[]> {
  const response = await httpClient.get<BetStatus[]>("/bets/statuses/");
  return response.data;
}

export async function fetchSports(): Promise<Sport[]> {
  const response = await httpClient.get<Sport[]>("/bets/sports/");
  return response.data;
}

export async function fetchCategories(): Promise<BetCategory[]> {
  const response = await httpClient.get<BetCategory[]>("/bets/categories/");
  return response.data;
}

// ─── Balance / Estadisticas ─────────────────────────────

export async function fetchDailyBalance(date?: string): Promise<DailyBalance> {
  const params = date ? { date } : {};
  const response = await httpClient.get<DailyBalance>("/bets/balance/daily/", { params });
  return response.data;
}

export async function fetchTotalBalance(): Promise<TotalBalance> {
  const response = await httpClient.get<TotalBalance>("/bets/balance/total/");
  return response.data;
}

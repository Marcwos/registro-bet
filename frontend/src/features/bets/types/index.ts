// ─── Bet ────────────────────────────────────────────────
export interface Bet {
  id: string;
  user_id: string;
  title: string;
  stake_amount: string; // Decimals come as strings from DRF
  odds: string;
  profit_expected: string;
  profit_final: string | null;
  status_id: string;
  sport_id: string | null;
  category_id: string | null;
  description: string;
  placed_at: string;
  settled_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateBetRequest {
  stake_amount: number;
  odds: number;
  profit_expected: number;
  profit_final?: number | null;
  placed_at?: string;
  sport_id?: string | null;
  category_id?: string | null;
  description?: string;
}

export interface UpdateBetRequest {
  stake_amount?: number;
  odds?: number;
  profit_expected?: number;
  profit_final?: number | null;
  placed_at?: string;
  description?: string;
  confirm?: boolean;
}

export interface ChangeBetStatusRequest {
  status_code: string;
  profit_final?: number | null;
}

// ─── Catalogos ──────────────────────────────────────────
export interface BetStatus {
  id: string;
  name: string;
  code: string;
  is_final: boolean;
}

export interface Sport {
  id: string;
  name: string;
  is_active: boolean;
}

export interface BetCategory {
  id: string;
  name: string;
  description: string;
}

// ─── Balance / Estadisticas ─────────────────────────────
export interface DailyBalance {
  target_date: string;
  total_staked: string;
  total_won: string;
  total_lost: string;
  net_profit: string;
  bet_count: number;
  won_count: number;
  lost_count: number;
  void_count: number;
  pending_count: number;
}

export interface TotalBalance {
  total_staked: string;
  total_won: string;
  total_lost: string;
  net_profit: string;
  bet_count: number;
  won_count: number;
  lost_count: number;
  void_count: number;
  pending_count: number;
}

import { useState, useMemo } from "react";
import {
  Calendar,
  TrendingUp,
  TrendingDown,
  DollarSign,
  BarChart3,
  Search,
} from "lucide-react";
import { StatCard } from "../components/stat-card";
import { BetTable } from "../components/bet-table";
import { BetForm } from "../components/bet-form";
import { ChangeStatusModal } from "../components/change-status-modal";
import { ConfirmDeleteModal } from "../components/confirm-delete-modal";
import { Modal } from "@/shared/components/modal";
import { Button } from "@/shared/components/button";
import { useBetHistory } from "../hooks/use-bets";
import { useStatuses } from "../hooks/use-catalogs";
import {
  useUpdateBet,
  useDeleteBet,
  useChangeBetStatus,
} from "../hooks/use-bet-mutations";
import { getApiErrorMessage } from "@/shared/lib/api-error";
import type { Bet } from "../types";

// ─── Helpers ────────────────────────────────────────────

function formatDate(date: Date): string {
  return date.toISOString().slice(0, 10);
}

function getDefaultRange(): { start: string; end: string } {
  const end = new Date();
  const start = new Date();
  start.setDate(start.getDate() - 30);
  return { start: formatDate(start), end: formatDate(end) };
}

function formatMoney(value: number): string {
  const sign = value >= 0 ? "+" : "";
  return `${sign}$${Math.abs(value).toFixed(2)}`;
}

function getTrend(value: number): "positive" | "negative" | "neutral" {
  return value > 0 ? "positive" : value < 0 ? "negative" : "neutral";
}

/** Agrupa apuestas por su fecha placed_at (YYYY-MM-DD) ordenadas desc */
function groupByDate(bets: Bet[]): { date: string; bets: Bet[] }[] {
  const map = new Map<string, Bet[]>();

  for (const bet of bets) {
    const day = bet.placed_at.slice(0, 10);
    const group = map.get(day);
    if (group) {
      group.push(bet);
    } else {
      map.set(day, [bet]);
    }
  }

  return Array.from(map.entries())
    .sort(([a], [b]) => b.localeCompare(a))
    .map(([date, bets]) => ({ date, bets }));
}

function formatDisplayDate(iso: string): string {
  const [year, month, day] = iso.split("-");
  return `${day}/${month}/${year}`;
}

// ─── Component ──────────────────────────────────────────

export function HistoryPage() {
  const defaults = getDefaultRange();

  // ─── Date range state ─────────────────────────────────
  const [startDate, setStartDate] = useState(defaults.start);
  const [endDate, setEndDate] = useState(defaults.end);
  const [appliedStart, setAppliedStart] = useState(defaults.start);
  const [appliedEnd, setAppliedEnd] = useState(defaults.end);

  // ─── Queries ──────────────────────────────────────────
  const { data, isLoading, isError } = useBetHistory(appliedStart, appliedEnd);
  const { data: statuses = [] } = useStatuses();

  // ─── Mutations ────────────────────────────────────────
  const updateBet = useUpdateBet();
  const deleteBet = useDeleteBet();
  const changeBetStatus = useChangeBetStatus();

  // ─── Modal state ──────────────────────────────────────
  const [editBet, setEditBet] = useState<Bet | null>(null);
  const [statusBet, setStatusBet] = useState<Bet | null>(null);
  const [deletingBet, setDeletingBet] = useState<Bet | null>(null);
  const [editError, setEditError] = useState("");

  // ─── Derived data ─────────────────────────────────────
  const summary = data?.summary;
  const bets = useMemo(() => data?.bets ?? [], [data?.bets]);
  const grouped = useMemo(() => groupByDate(bets), [bets]);

  const netProfit = Number(summary?.net_profit ?? 0);
  const totalStaked = Number(summary?.total_staked ?? 0);
  const totalWon = Number(summary?.total_won ?? 0);
  const totalLost = Number(summary?.total_lost ?? 0);

  // ─── Handlers ─────────────────────────────────────────
  const handleSearch = () => {
    setAppliedStart(startDate);
    setAppliedEnd(endDate);
  };

  const handleEdit = (data: Parameters<typeof updateBet.mutate>[0]["data"] & { status_code?: string }) => {
    if (!editBet) return;
    setEditError("");
    const { status_code, ...betData } = data;

    const currentCode = statuses.find((s) => s.id === editBet.status_id)?.code;
    const isFinal = statuses.find((s) => s.id === editBet.status_id)?.is_final ?? false;

    updateBet.mutate(
      { id: editBet.id, data: { ...betData, confirm: isFinal } },
      {
        onSuccess: () => {
          if (status_code && status_code !== currentCode) {
            changeBetStatus.mutate(
              { id: editBet.id, data: { status_code } },
              { onSuccess: () => setEditBet(null) },
            );
          } else {
            setEditBet(null);
          }
        },
        onError: (err) => setEditError(getApiErrorMessage(err)),
      },
    );
  };

  const handleChangeStatus = (statusCode: string, profitFinal?: number | null) => {
    if (!statusBet) return;
    changeBetStatus.mutate(
      {
        id: statusBet.id,
        data: { status_code: statusCode, profit_final: profitFinal },
      },
      { onSuccess: () => setStatusBet(null) },
    );
  };

  const handleDelete = () => {
    if (!deletingBet) return;
    deleteBet.mutate(deletingBet.id, {
      onSuccess: () => setDeletingBet(null),
    });
  };

  return (
    <div className="min-w-0 space-y-4 md:space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-900 md:text-2xl">Historial</h1>
        <p className="mt-0.5 text-xs text-slate-500 md:mt-1 md:text-sm">
          Filtra y revisa tus apuestas por rango de fechas
        </p>
      </div>

      {/* Date range picker */}
      <div className="rounded-2xl border border-slate-200 bg-white p-3 shadow-sm md:p-6">
        <div className="flex flex-wrap items-end gap-3 md:gap-4">
          <div className="flex-1 min-w-[130px]">
            <label className="mb-1 block text-xs font-medium text-slate-700 md:mb-1.5 md:text-sm">
              Fecha inicio
            </label>
            <div className="relative">
              <Calendar className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full rounded-lg border border-slate-300 py-2 pl-10 pr-3 text-sm text-slate-900 outline-none transition-colors focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
              />
            </div>
          </div>

          <div className="flex-1 min-w-[130px]">
            <label className="mb-1 block text-xs font-medium text-slate-700 md:mb-1.5 md:text-sm">
              Fecha fin
            </label>
            <div className="relative">
              <Calendar className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full rounded-lg border border-slate-300 py-2 pl-10 pr-3 text-sm text-slate-900 outline-none transition-colors focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
              />
            </div>
          </div>

          <Button onClick={handleSearch}>
            <Search className="mr-2 h-4 w-4" />
            Buscar
          </Button>
        </div>
      </div>

      {/* Loading */}
      {isLoading && (
        <div className="py-12 text-center text-sm text-slate-400">
          Cargando historial...
        </div>
      )}

      {/* Error */}
      {isError && (
        <div className="rounded-2xl border border-rose-200 bg-rose-50 p-6 text-center text-sm text-rose-600">
          Ocurrio un error al cargar el historial. Intenta de nuevo.
        </div>
      )}

      {/* Results */}
      {data && !isLoading && (
        <>
          {/* Stat cards */}
          <div className="grid grid-cols-2 gap-3 md:gap-6 lg:grid-cols-4">
            <StatCard
              label="Ganancia neta"
              value={formatMoney(netProfit)}
              icon={TrendingUp}
              trend={getTrend(netProfit)}
            />
            <StatCard
              label="Total apostado"
              value={`$${totalStaked.toFixed(2)}`}
              icon={DollarSign}
              trend="neutral"
            />
            <StatCard
              label="Total ganado"
              value={formatMoney(totalWon)}
              icon={TrendingUp}
              trend={getTrend(totalWon)}
            />
            <StatCard
              label="Total perdido"
              value={formatMoney(-totalLost)}
              icon={TrendingDown}
              trend={totalLost > 0 ? "negative" : "neutral"}
            />
          </div>

          {/* Count badges */}
          <div className="flex flex-wrap gap-2 md:gap-3">
            <CountBadge
              label="Total"
              count={summary?.bet_count ?? 0}
              className="bg-slate-100 text-slate-700"
            />
            <CountBadge
              label="Ganadas"
              count={summary?.won_count ?? 0}
              className="bg-emerald-50 text-emerald-700"
            />
            <CountBadge
              label="Perdidas"
              count={summary?.lost_count ?? 0}
              className="bg-rose-50 text-rose-700"
            />
            <CountBadge
              label="Nulas"
              count={summary?.void_count ?? 0}
              className="bg-gray-100 text-gray-600"
            />
            <CountBadge
              label="Pendientes"
              count={summary?.pending_count ?? 0}
              className="bg-blue-50 text-blue-700"
            />
          </div>

          {/* Bets grouped by date */}
          {bets.length === 0 ? (
            <div className="rounded-2xl border border-slate-200 bg-white py-16 text-center shadow-sm">
              <BarChart3 className="mx-auto h-10 w-10 text-slate-300" />
              <p className="mt-3 text-sm text-slate-500">
                No hay apuestas en este rango de fechas.
              </p>
              <p className="mt-1 text-xs text-slate-400">
                Prueba con un rango diferente.
              </p>
            </div>
          ) : (
            <div className="space-y-4 md:space-y-6">
              {grouped.map(({ date, bets: dayBets }) => (
                <div
                  key={date}
                  className="rounded-2xl border border-slate-200 bg-white shadow-sm"
                >
                  <div className="border-b border-slate-200 px-4 py-3 md:px-6 md:py-4">
                    <h2 className="text-base font-semibold text-slate-900 md:text-lg">
                      {formatDisplayDate(date)}
                    </h2>
                    <p className="text-xs text-slate-500 md:text-sm">
                      {dayBets.length} apuesta{dayBets.length !== 1 && "s"}
                    </p>
                  </div>
                  <BetTable
                    bets={dayBets}
                    statuses={statuses}
                    onChangeStatus={(bet) => setStatusBet(bet)}
                    onEdit={(bet) => setEditBet(bet)}
                    onDelete={(bet) => setDeletingBet(bet)}
                  />
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* ─── Modales ─────────────────────────────────── */}

      {/* Editar apuesta */}
      <Modal
        isOpen={!!editBet}
        onClose={() => setEditBet(null)}
        title="Editar apuesta"
      >
        <BetForm
          key={editBet?.id}
          bet={editBet ?? undefined}
          statuses={statuses}
          onSubmit={handleEdit}
          isLoading={updateBet.isPending || changeBetStatus.isPending}
          error={editError}
        />
      </Modal>

      {/* Cambiar estado */}
      <ChangeStatusModal
        isOpen={!!statusBet}
        onClose={() => setStatusBet(null)}
        bet={statusBet}
        onConfirm={handleChangeStatus}
        isLoading={changeBetStatus.isPending}
      />

      {/* Confirmar eliminacion */}
      <ConfirmDeleteModal
        isOpen={!!deletingBet}
        onClose={() => setDeletingBet(null)}
        bet={deletingBet}
        onConfirm={handleDelete}
        isLoading={deleteBet.isPending}
      />
    </div>
  );
}

// ─── Small helper component ─────────────────────────────

function CountBadge({
  label,
  count,
  className,
}: {
  label: string;
  count: number;
  className: string;
}) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium md:gap-1.5 md:px-3 md:py-1 md:text-sm ${className}`}
    >
      {label}
      <span className="font-bold">{count}</span>
    </span>
  );
}

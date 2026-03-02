import { useState, useMemo, useCallback } from "react";
import { AnimatePresence, motion } from "motion/react";
import {
  Calendar,
  TrendingUp,
  TrendingDown,
  DollarSign,
  BarChart3,
  Search,
  ChevronDown,
  SlidersHorizontal,
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
import type { Bet, BetStatus } from "../types";

// ─── Helpers ────────────────────────────────────────────

function formatDate(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function getDefaultRange(): { start: string; end: string } {
  const end = new Date();
  const start = new Date();
  start.setDate(start.getDate() - 15);
  return { start: formatDate(start), end: formatDate(end) };
}

function formatMoney(value: number): string {
  const sign = value >= 0 ? "+" : "";
  return `${sign}$${Math.abs(value).toFixed(2)}`;
}

function getTrend(value: number): "positive" | "negative" | "neutral" {
  return value > 0 ? "positive" : value < 0 ? "negative" : "neutral";
}

/** Agrupa apuestas por su fecha placed_at en hora local (YYYY-MM-DD) ordenadas desc */
function groupByDate(bets: Bet[]): { date: string; bets: Bet[] }[] {
  const map = new Map<string, Bet[]>();

  for (const bet of bets) {
    const d = new Date(bet.placed_at);
    const day = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
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

/** Formato corto para encabezados del accordion: "28 Feb 2026" */
function formatShortDate(iso: string): string {
  const [y, m, d] = iso.split("-").map(Number);
  const date = new Date(y, m - 1, d);
  return date.toLocaleDateString("es", { day: "numeric", month: "short", year: "numeric" });
}

/** Calcula la ganancia neta de un día: ganadas aportan (profit - stake), perdidas restan stake */
function calcDayBalance(dayBets: Bet[], statuses: BetStatus[]): number {
  let balance = 0;
  for (const bet of dayBets) {
    const code = statuses.find((s) => s.id === bet.status_id)?.code ?? "pending";
    const stake = Number(bet.stake_amount);
    if (code === "won") {
      // Ganancia neta = lo que se gana menos lo que se apostó
      balance += Number(bet.profit_expected) - stake;
    } else if (code === "lost") {
      balance -= stake;
    }
    // pending y void no afectan la ganancia neta
  }
  return balance;
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

  // ─── UI state (accordion + filters) ───────────────────
  const [manualOpenDates, setManualOpenDates] = useState<Set<string> | null>(null);
  const [filtersOpen, setFiltersOpen] = useState(false);

  // ─── Derived data ─────────────────────────────────────
  const summary = data?.summary;
  const bets = useMemo(() => data?.bets ?? [], [data?.bets]);
  const grouped = useMemo(() => groupByDate(bets), [bets]);

  // Si el usuario no ha tocado el accordion, abrir el día más reciente
  const openDates = useMemo<Set<string>>(() => {
    if (manualOpenDates !== null) return manualOpenDates;
    if (grouped.length > 0) return new Set([grouped[0].date]);
    return new Set();
  }, [manualOpenDates, grouped]);

  const netProfit = Number(summary?.net_profit ?? 0);
  const totalStaked = Number(summary?.total_staked ?? 0);
  const totalWon = Number(summary?.total_won ?? 0);
  const totalLost = Number(summary?.total_lost ?? 0);

  // ─── Handlers ─────────────────────────────────────────
  const handleSearch = () => {
    setAppliedStart(startDate);
    setAppliedEnd(endDate);
    setFiltersOpen(false);
    setManualOpenDates(null); // Se reabrirá el primer día cuando lleguen datos
  };

  const toggleDate = useCallback((date: string) => {
    setManualOpenDates((prev) => {
      const base = prev ?? (grouped.length > 0 ? new Set([grouped[0].date]) : new Set<string>());
      const next = new Set(base);
      if (next.has(date)) next.delete(date);
      else next.add(date);
      return next;
    });
  }, [grouped]);

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
    <div className="min-w-0 overflow-x-hidden space-y-4 md:space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-900 md:text-2xl dark:text-slate-100">Historial</h1>
        <p className="mt-0.5 text-xs text-slate-500 md:mt-1 md:text-sm dark:text-slate-400">
          Filtra y revisa tus apuestas por rango de fechas
        </p>
      </div>

      {/* Date range picker */}
      <div className="rounded-2xl border border-slate-200 bg-white p-3 shadow-sm md:p-6 dark:border-slate-700 dark:bg-slate-800">
        {/* Mobile toggle */}
        <button
          type="button"
          onClick={() => setFiltersOpen(!filtersOpen)}
          className="flex w-full items-center justify-between md:hidden"
        >
          <span className="flex items-center gap-2 text-sm font-medium text-slate-700 dark:text-slate-300">
            <SlidersHorizontal className="h-4 w-4" />
            Filtros
          </span>
          <ChevronDown
            className={`h-4 w-4 text-slate-400 transition-transform duration-200 ${filtersOpen ? "rotate-180" : ""}`}
          />
        </button>

        {/* Inputs — siempre visibles en desktop, colapsables en mobile */}
        <div className={`${filtersOpen ? "mt-3" : "hidden"} md:!block md:mt-0`}>
          <div className="flex flex-wrap items-end gap-3 md:gap-4">
            <div className="flex-1 min-w-[130px]">
              <label className="mb-1 block text-xs font-medium text-slate-700 md:mb-1.5 md:text-sm dark:text-slate-300">
                Fecha inicio
              </label>
              <div className="relative">
                <Calendar className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-full rounded-lg border border-slate-300 py-2 pl-10 pr-3 text-sm text-slate-900 outline-none transition-colors focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 dark:border-slate-700 dark:bg-slate-900/50 dark:text-slate-100"
                />
              </div>
            </div>

            <div className="flex-1 min-w-[130px]">
              <label className="mb-1 block text-xs font-medium text-slate-700 md:mb-1.5 md:text-sm dark:text-slate-300">
                Fecha fin
              </label>
              <div className="relative">
                <Calendar className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="w-full rounded-lg border border-slate-300 py-2 pl-10 pr-3 text-sm text-slate-900 outline-none transition-colors focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 dark:border-slate-700 dark:bg-slate-900/50 dark:text-slate-100"
                />
              </div>
            </div>

            <Button onClick={handleSearch}>
              <Search className="mr-2 h-4 w-4" />
              Buscar
            </Button>
          </div>
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
        <div className="rounded-2xl border border-rose-200 bg-rose-50 p-6 text-center text-sm text-rose-600 dark:border-rose-500/20 dark:bg-rose-900/20 dark:text-rose-400">
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
              tooltip="Tu balance final en este rango de fechas. Es la diferencia entre lo que ganaste y lo que perdiste."
            />
            <StatCard
              label="Total apostado"
              value={`$${totalStaked.toFixed(2)}`}
              icon={DollarSign}
              trend="neutral"
              tooltip="Todo el dinero que pusiste en juego durante este periodo, sumando todas tus apuestas."
            />
            <StatCard
              label="Total ganado"
              value={formatMoney(totalWon)}
              icon={TrendingUp}
              trend={getTrend(totalWon)}
              tooltip="La ganancia limpia que obtuviste únicamente de las apuestas ganadoras."
            />
            <StatCard
              label="Total perdido"
              value={formatMoney(-totalLost)}
              icon={TrendingDown}
              trend={totalLost > 0 ? "negative" : "neutral"}
              tooltip="El dinero que arriesgaste y no recuperaste en las apuestas perdedoras."
            />
          </div>

          {/* Count badges */}
          <div className="flex gap-2 overflow-x-auto pb-1 md:flex-wrap md:gap-3 md:overflow-visible md:pb-0">
            <CountBadge
              label="Total"
              count={summary?.bet_count ?? 0}
              className="bg-slate-100 text-slate-700 dark:bg-slate-700/50 dark:text-slate-300"
            />
            <CountBadge
              label="Ganadas"
              count={summary?.won_count ?? 0}
              className="bg-emerald-50 text-emerald-700 dark:bg-slate-700/50 dark:text-slate-300"
            />
            <CountBadge
              label="Perdidas"
              count={summary?.lost_count ?? 0}
              className="bg-rose-50 text-rose-700 dark:bg-slate-700/50 dark:text-slate-300"
            />
            <CountBadge
              label="Nulas"
              count={summary?.void_count ?? 0}
              className="bg-gray-100 text-gray-600 dark:bg-slate-700/50 dark:text-slate-300"
            />
            <CountBadge
              label="Pendientes"
              count={summary?.pending_count ?? 0}
              className="bg-blue-50 text-blue-700 dark:bg-slate-700/50 dark:text-slate-300"
            />
          </div>

          {/* Bets grouped by date — accordion */}
          {bets.length === 0 ? (
            <div className="rounded-2xl border border-slate-200 bg-white py-16 text-center shadow-sm dark:border-slate-700 dark:bg-slate-800">
              <BarChart3 className="mx-auto h-10 w-10 text-slate-300" />
              <p className="mt-3 text-sm text-slate-500">
                No hay apuestas en este rango de fechas.
              </p>
              <p className="mt-1 text-xs text-slate-400">
                Prueba con un rango diferente.
              </p>
            </div>
          ) : (
            <div className="space-y-3 md:space-y-4">
              {grouped.map(({ date, bets: dayBets }) => {
                const isOpen = openDates.has(date);
                const dayBalance = calcDayBalance(dayBets, statuses);
                const balanceColor =
                  dayBalance > 0
                    ? "text-emerald-600 dark:text-emerald-400"
                    : dayBalance < 0
                      ? "text-rose-600 dark:text-rose-400"
                      : "text-slate-400";

                return (
                  <div
                    key={date}
                    className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800"
                  >
                    {/* Accordion header */}
                    <button
                      type="button"
                      onClick={() => toggleDate(date)}
                      className="flex w-full items-center justify-between px-4 py-3 text-left transition-colors hover:bg-slate-50 md:px-6 md:py-4 dark:hover:bg-slate-700/50"
                    >
                      <div className="min-w-0">
                        <h2 className="text-sm font-semibold text-slate-900 md:text-base dark:text-slate-100">
                          {formatShortDate(date)}
                        </h2>
                        <p className="text-xs text-slate-500">
                          {dayBets.length} apuesta{dayBets.length !== 1 && "s"}
                        </p>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        <span className={`text-sm font-bold md:text-base ${balanceColor}`}>
                          {formatMoney(dayBalance)}
                        </span>
                        <ChevronDown
                          className={`h-4 w-4 text-slate-400 transition-transform duration-200 ${isOpen ? "rotate-180" : ""}`}
                        />
                      </div>
                    </button>

                    {/* Accordion content */}
                    <AnimatePresence initial={false}>
                      {isOpen && (
                        <motion.div
                          key="content"
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: "auto", opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          transition={{ duration: 0.2, ease: "easeInOut" }}
                          className="overflow-hidden border-t border-slate-200 dark:border-slate-700"
                        >
                          <BetTable
                            bets={dayBets}
                            statuses={statuses}
                            onChangeStatus={(bet) => setStatusBet(bet)}
                            onEdit={(bet) => setEditBet(bet)}
                            onDelete={(bet) => setDeletingBet(bet)}
                          />
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                );
              })}
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
      className={`inline-flex shrink-0 items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium md:gap-1.5 md:px-3 md:py-1 md:text-sm ${className}`}
    >
      {label}
      <span className="font-bold">{count}</span>
    </span>
  );
}

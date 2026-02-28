import { useState } from "react";
import { DollarSign, TrendingUp, TrendingDown } from "lucide-react";
import { StatCard } from "../components/stat-card";
import { BetForm } from "../components/bet-form";
import { BetTable } from "../components/bet-table";
import { ChangeStatusModal } from "../components/change-status-modal";
import { ConfirmDeleteModal } from "../components/confirm-delete-modal";
import { Modal } from "@/shared/components/modal";
import { useBets, useDailyBalance, useTotalBalance } from "../hooks/use-bets";
import { useStatuses } from "../hooks/use-catalogs";
import {
  useCreateBet,
  useUpdateBet,
  useDeleteBet,
  useChangeBetStatus,
} from "../hooks/use-bet-mutations";
import { getApiErrorMessage } from "@/shared/lib/api-error";
import type { Bet } from "../types";

export function DashboardPage() {
  // ─── Queries ──────────────────────────────────────────
  const { data: bets = [], isLoading: loadingBets } = useBets();
  const { data: dailyBalance } = useDailyBalance();
  const { data: totalBalance } = useTotalBalance();
  const { data: statuses = [] } = useStatuses();

  // ─── Mutations ────────────────────────────────────────
  const createBet = useCreateBet();
  const updateBet = useUpdateBet();
  const deleteBet = useDeleteBet();
  const changeBetStatus = useChangeBetStatus();

  // ─── Modal state ──────────────────────────────────────
  const [editBet, setEditBet] = useState<Bet | null>(null);
  const [statusBet, setStatusBet] = useState<Bet | null>(null);
  const [deletingBet, setDeletingBet] = useState<Bet | null>(null);
  const [createError, setCreateError] = useState("");
  const [editError, setEditError] = useState("");

  // ─── Handlers ─────────────────────────────────────────
  const handleCreate = (data: Parameters<typeof createBet.mutate>[0]) => {
    setCreateError("");
    createBet.mutate(data, {
      onError: (err) => setCreateError(getApiErrorMessage(err)),
    });
  };

  const handleEdit = (data: Parameters<typeof createBet.mutate>[0]) => {
    if (!editBet) return;
    setEditError("");
    updateBet.mutate(
      { id: editBet.id, data },
      {
        onSuccess: () => setEditBet(null),
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
      {
        onSuccess: () => setStatusBet(null),
      },
    );
  };

  const handleDelete = () => {
    if (!deletingBet) return;
    deleteBet.mutate(deletingBet.id, {
      onSuccess: () => setDeletingBet(null),
    });
  };

  // ─── Stats helpers ────────────────────────────────────
  const netProfit = Number(totalBalance?.net_profit ?? 0);
  const dailyNet = Number(dailyBalance?.net_profit ?? 0);
  const totalStaked = Number(totalBalance?.total_staked ?? 0);

  const formatMoney = (value: number) => {
    const sign = value >= 0 ? "+" : "";
    return `${sign}$${Math.abs(value).toFixed(2)}`;
  };

  const getTrend = (value: number): "positive" | "negative" | "neutral" =>
    value > 0 ? "positive" : value < 0 ? "negative" : "neutral";

  // ─── Filtrar apuestas del dia ─────────────────────────
  const today = new Date().toISOString().slice(0, 10);
  const todayBets = bets.filter(
    (bet) => bet.placed_at.slice(0, 10) === today,
  );

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
        <p className="mt-1 text-sm text-slate-500">
          Resumen de tus apuestas y rendimiento
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <StatCard
          label="Ganancia neta total"
          value={formatMoney(netProfit)}
          icon={TrendingUp}
          trend={getTrend(netProfit)}
        />
        <StatCard
          label="Resultado de hoy"
          value={formatMoney(dailyNet)}
          icon={TrendingDown}
          trend={getTrend(dailyNet)}
        />
        <StatCard
          label="Total apostado"
          value={`$${totalStaked.toFixed(2)}`}
          icon={DollarSign}
          trend="neutral"
        />
      </div>

      {/* Grid: Formulario + Tabla */}
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        {/* Formulario (1/3) */}
        <div className="lg:col-span-1">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-slate-900">
              Nueva apuesta
            </h2>
            <BetForm
              onSubmit={handleCreate}
              isLoading={createBet.isPending}
              error={createError}
            />
          </div>
        </div>

        {/* Tabla de hoy (2/3) */}
        <div className="lg:col-span-2">
          <div className="rounded-2xl border border-slate-200 bg-white shadow-sm">
            <div className="border-b border-slate-200 px-6 py-4">
              <h2 className="text-lg font-semibold text-slate-900">
                Apuestas de hoy
              </h2>
              <p className="text-sm text-slate-500">
                {todayBets.length} apuesta{todayBets.length !== 1 && "s"}
              </p>
            </div>

            {loadingBets ? (
              <div className="py-12 text-center text-sm text-slate-400">
                Cargando apuestas...
              </div>
            ) : (
              <BetTable
                bets={todayBets}
                statuses={statuses}
                onChangeStatus={(bet) => setStatusBet(bet)}
                onEdit={(bet) => setEditBet(bet)}
                onDelete={(bet) => setDeletingBet(bet)}
              />
            )}
          </div>
        </div>
      </div>

      {/* ─── Modales ─────────────────────────────────── */}

      {/* Editar apuesta */}
      <Modal
        isOpen={!!editBet}
        onClose={() => setEditBet(null)}
        title="Editar apuesta"
      >
        <BetForm
          bet={editBet ?? undefined}
          onSubmit={handleEdit}
          isLoading={updateBet.isPending}
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

import { useState } from "react";
import { DollarSign, TrendingDown, TrendingUp, Wallet } from "lucide-react";
import { StatCard } from "../components/stat-card";
import { BetForm } from "../components/bet-form";
import { BetTable } from "../components/bet-table";
import { ChangeStatusModal } from "../components/change-status-modal";
import { ConfirmDeleteModal } from "../components/confirm-delete-modal";
import { Modal } from "@/shared/components/modal";
import { useBets, useDailyBalance } from "../hooks/use-bets";
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
  const [formKey, setFormKey] = useState(0);

  // ─── Handlers ─────────────────────────────────────────
  const handleCreate = (data: Parameters<typeof createBet.mutate>[0]) => {
    setCreateError("");
    createBet.mutate(data, {
      onSuccess: () => setFormKey((k) => k + 1),
      onError: (err) => setCreateError(getApiErrorMessage(err)),
    });
  };

  const handleEdit = (data: Parameters<typeof createBet.mutate>[0] & { status_code?: string }) => {
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
  const netProfit = Number(dailyBalance?.net_profit ?? 0);
  const dailyReturn = Number(dailyBalance?.total_return ?? 0);
  const totalStaked = Number(dailyBalance?.total_staked ?? 0);

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
    <div className="min-w-0 space-y-4 md:space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-900 md:text-2xl">Dashboard</h1>
        <p className="mt-0.5 text-xs text-slate-500 md:mt-1 md:text-sm">
          Resumen de tus apuestas y rendimiento
        </p>
      </div>

      {/* Stats Cards — 2-col grid en mobile, 3-col en md+ */}
      <div className="grid grid-cols-2 gap-3 md:grid-cols-3 md:gap-6">
        <StatCard
          label="Ganancia neta total"
          value={formatMoney(netProfit)}
          icon={netProfit >= 0 ? TrendingUp : TrendingDown}
          trend={getTrend(netProfit)}
          index={0}
          className="col-span-2 md:col-span-1"
        />
        <StatCard
          label="Retorno total"
          value={formatMoney(dailyReturn)}
          icon={Wallet}
          trend={getTrend(dailyReturn)}
          index={1}
        />
        <StatCard
          label="Total apostado"
          value={`$${totalStaked.toFixed(2)}`}
          icon={DollarSign}
          trend="neutral"
          index={2}
        />
      </div>

      {/* Grid: Formulario + Tabla */}
      <div className="grid grid-cols-1 gap-4 md:gap-8 lg:grid-cols-3">
        {/* Formulario (1/3) */}
        <div className="lg:col-span-1">
          <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm md:p-6">
            <h2 className="mb-3 text-base font-semibold text-slate-900 md:mb-4 md:text-lg">
              Nueva apuesta
            </h2>
            <BetForm
              key={formKey}
              onSubmit={handleCreate}
              isLoading={createBet.isPending}
              error={createError}
            />
          </div>
        </div>

        {/* Tabla de hoy (2/3) */}
        <div className="lg:col-span-2">
          <div className="rounded-2xl border border-slate-200 bg-white shadow-sm">
            <div className="border-b border-slate-200 px-4 py-3 md:px-6 md:py-4">
              <h2 className="text-base font-semibold text-slate-900 md:text-lg">
                Apuestas de hoy
              </h2>
              <p className="text-xs text-slate-500 md:text-sm">
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

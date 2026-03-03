import { Gift, MoreHorizontal, Pencil, Trash2, Zap } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { StatusBadge } from "./status-badge";
import type { Bet, BetStatus } from "../types";

interface BetTableProps {
  bets: Bet[];
  statuses: BetStatus[];
  onChangeStatus: (bet: Bet) => void;
  onEdit: (bet: Bet) => void;
  onDelete: (bet: Bet) => void;
}

export function BetTable({ bets, statuses, onChangeStatus, onEdit, onDelete }: BetTableProps) {
  if (bets.length === 0) {
    return (
      <div className="py-12 text-center">
        <p className="text-sm text-slate-500">No hay apuestas registradas hoy.</p>
        <p className="mt-1 text-xs text-slate-400">
          Usa el formulario para registrar tu primera apuesta.
        </p>
      </div>
    );
  }

  return (
    <>
      {/* ─── Mobile: lista de tarjetas ─────────────────── */}
      <div className="divide-y divide-slate-100 md:hidden dark:divide-slate-700">
        {bets.map((bet) => (
          <BetCard
            key={bet.id}
            bet={bet}
            statuses={statuses}
            onChangeStatus={onChangeStatus}
            onEdit={onEdit}
            onDelete={onDelete}
          />
        ))}
      </div>

      {/* ─── Desktop: tabla clasica ────────────────────── */}
      <div className="hidden md:block">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-700">
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">
                  Titulo
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500">
                  Monto
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500">
                  Cuota
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500">
                  Ganancia
                </th>
                <th className="px-4 py-3 text-center text-xs font-medium uppercase tracking-wider text-slate-500">
                  Estado
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500">
                  <span className="sr-only">Acciones</span>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
              {bets.map((bet) => (
                <BetRow
                  key={bet.id}
                  bet={bet}
                  statuses={statuses}
                  onChangeStatus={onChangeStatus}
                  onEdit={onEdit}
                  onDelete={onDelete}
                />
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}

// ─── Helpers comunes de ganancia ─────────────────────────

function useBetProfit(bet: Bet, statuses: BetStatus[]) {
  const statusCode = statuses.find((s) => s.id === bet.status_id)?.code ?? "pending";
  const isFinal = statuses.find((s) => s.id === bet.status_id)?.is_final ?? false;
  const profitExpected = Number(bet.profit_expected);

  let profitText: string;
  let profitClass: string;
  let tooltipText: string | null = null;

  if (statusCode === "lost") {
    profitText = bet.is_freebet ? "$0.00" : "$0.00";
    profitClass = bet.is_freebet
      ? "text-slate-400 dark:text-slate-500"
      : "text-rose-600 dark:text-rose-400";
    tooltipText = bet.is_freebet
      ? "Freebet — sin p\u00e9rdida real"
      : `+$${profitExpected.toFixed(2)}`;
  } else if (statusCode === "void") {
    profitText = `$${Number(bet.stake_amount).toFixed(2)}`;
    profitClass = "text-slate-400";
  } else {
    profitText = `+$${profitExpected.toFixed(2)}`;
    profitClass = "text-emerald-600 dark:text-emerald-400";
  }

  return { statusCode, isFinal, profitText, profitClass, tooltipText };
}

// ─── Menu de acciones reutilizable ──────────────────────

function BetActionMenu({
  onEdit,
  onDelete,
}: {
  onEdit: () => void;
  onDelete: () => void;
}) {
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!menuOpen) return;
    const handleClick = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [menuOpen]);

  return (
    <div className="relative inline-block" ref={menuRef}>
      <button
        onClick={() => setMenuOpen(!menuOpen)}
        className="rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-700 dark:hover:text-slate-300"
      >
        <MoreHorizontal className="h-4 w-4" />
      </button>

      {menuOpen && (
        <div className="absolute right-0 z-10 mt-1 w-44 rounded-lg border border-slate-200 bg-white py-1 shadow-lg dark:border-slate-700 dark:bg-slate-800">
          <button
            onClick={() => { onEdit(); setMenuOpen(false); }}
            className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-slate-700 hover:bg-slate-50 dark:text-slate-300 dark:hover:bg-slate-700"
          >
            <Pencil className="h-4 w-4" />
            Editar
          </button>
          <button
            onClick={() => { onDelete(); setMenuOpen(false); }}
            className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-rose-600 hover:bg-rose-50 dark:text-rose-400 dark:hover:bg-rose-900/20"
          >
            <Trash2 className="h-4 w-4" />
            Eliminar
          </button>
        </div>
      )}
    </div>
  );
}

// ─── Tarjeta mobile ─────────────────────────────────────

interface BetCardProps {
  bet: Bet;
  statuses: BetStatus[];
  onChangeStatus: (bet: Bet) => void;
  onEdit: (bet: Bet) => void;
  onDelete: (bet: Bet) => void;
}

function BetCard({ bet, statuses, onChangeStatus, onEdit, onDelete }: BetCardProps) {
  const { statusCode, isFinal, profitText, profitClass } = useBetProfit(bet, statuses);

  return (
    <div className="flex items-start gap-3 px-4 py-3">
      <div className="min-w-0 flex-1">
        {/* Fila superior: titulo + monto/cuota */}
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-1.5">
              <p className="truncate text-sm font-medium text-slate-900 dark:text-slate-100">
                {bet.title}
              </p>
              {bet.is_freebet && (
                <span className="inline-flex items-center gap-0.5 rounded-full bg-blue-100 px-1.5 py-0.5 text-[10px] font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-400" title="Freebet">
                  <Gift className="h-2.5 w-2.5" /> Bono
                </span>
              )}
              {bet.is_boosted && (
                <span className="inline-flex items-center gap-0.5 rounded-full bg-amber-100 px-1.5 py-0.5 text-[10px] font-medium text-amber-700 dark:bg-amber-900/30 dark:text-amber-400" title="Bonificaci\u00f3n">
                  <Zap className="h-2.5 w-2.5" /> Boost
                </span>
              )}
            </div>
            {bet.description && (
              <p className="mt-0.5 text-xs text-slate-400 line-clamp-1">
                {bet.description}
              </p>
            )}
          </div>
          <p className="shrink-0 text-right text-xs text-slate-500 dark:text-slate-400">
            ${Number(bet.stake_amount).toFixed(2)}
            <span className="text-slate-400 dark:text-slate-500">
              {" "}a {Number(bet.odds).toFixed(2)}
            </span>
          </p>
        </div>
        {/* Fila inferior: badge + ganancia */}
        <div className="mt-2 flex items-center justify-between">
          <StatusBadge
            code={statusCode}
            onClick={!isFinal ? () => onChangeStatus(bet) : undefined}
          />
          <span className={`text-sm font-semibold ${profitClass}`}>
            {profitText}
          </span>
        </div>
      </div>
      {/* Menu acciones */}
      <div className="shrink-0 -mr-1 -mt-0.5">
        <BetActionMenu
          onEdit={() => onEdit(bet)}
          onDelete={() => onDelete(bet)}
        />
      </div>
    </div>
  );
}

// ─── Fila desktop ───────────────────────────────────────

interface BetRowProps {
  bet: Bet;
  statuses: BetStatus[];
  onChangeStatus: (bet: Bet) => void;
  onEdit: (bet: Bet) => void;
  onDelete: (bet: Bet) => void;
}

function BetRow({ bet, statuses, onChangeStatus, onEdit, onDelete }: BetRowProps) {
  const { statusCode, isFinal, profitText, profitClass, tooltipText } = useBetProfit(bet, statuses);

  const [showTooltip, setShowTooltip] = useState(false);
  const tooltipTimeout = useRef<ReturnType<typeof setTimeout>>(null);

  const handleTooltipEnter = () => {
    if (tooltipTimeout.current) clearTimeout(tooltipTimeout.current);
    setShowTooltip(true);
  };
  const handleTooltipLeave = () => {
    tooltipTimeout.current = setTimeout(() => setShowTooltip(false), 150);
  };

  return (
    <tr className="transition-colors hover:bg-slate-50 dark:hover:bg-slate-700/50">
      <td className="px-4 py-3">
        <div className="min-w-0">
          <div className="flex items-center gap-1.5">
            <p className="truncate text-sm font-medium text-slate-900 dark:text-slate-100">{bet.title}</p>
            {bet.is_freebet && (
              <span className="inline-flex shrink-0 items-center gap-0.5 rounded-full bg-blue-100 px-1.5 py-0.5 text-[10px] font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-400" title="Freebet">
                <Gift className="h-2.5 w-2.5" /> Bono
              </span>
            )}
            {bet.is_boosted && (
              <span className="inline-flex shrink-0 items-center gap-0.5 rounded-full bg-amber-100 px-1.5 py-0.5 text-[10px] font-medium text-amber-700 dark:bg-amber-900/30 dark:text-amber-400" title="Bonificaci\u00f3n">
                <Zap className="h-2.5 w-2.5" /> Boost
              </span>
            )}
          </div>
          {bet.description && (
            <p className="mt-0.5 text-xs text-slate-400 line-clamp-1">
              {bet.description}
            </p>
          )}
        </div>
      </td>
      <td className="px-4 py-3 text-right text-sm text-slate-700 dark:text-slate-300">
        ${Number(bet.stake_amount).toFixed(2)}
      </td>
      <td className="px-4 py-3 text-right text-sm text-slate-700 dark:text-slate-300">
        {Number(bet.odds).toFixed(2)}
      </td>
      <td className={`px-4 py-3 text-right text-sm font-medium ${profitClass}`}>
        {tooltipText ? (
          <span
            className="relative cursor-pointer"
            onMouseEnter={handleTooltipEnter}
            onMouseLeave={handleTooltipLeave}
          >
            {profitText}
            {showTooltip && (
              <span className="absolute bottom-full right-0 mb-2 whitespace-nowrap rounded-lg bg-slate-800 px-3 py-1.5 text-xs font-medium text-white shadow-lg after:absolute after:top-full after:right-3 after:border-4 after:border-transparent after:border-t-slate-800">
                Pudiste ganar {tooltipText}
              </span>
            )}
          </span>
        ) : (
          profitText
        )}
      </td>
      <td className="px-4 py-3 text-center">
        <StatusBadge code={statusCode} onClick={!isFinal ? () => onChangeStatus(bet) : undefined} />
      </td>
      <td className="px-4 py-3 text-right">
        <BetActionMenu
          onEdit={() => onEdit(bet)}
          onDelete={() => onDelete(bet)}
        />
      </td>
    </tr>
  );
}

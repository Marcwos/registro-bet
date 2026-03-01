import { MoreHorizontal, Pencil, Trash2 } from "lucide-react";
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
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-slate-200 dark:border-slate-700">
            <th className="px-2 py-2 text-left text-xs font-medium uppercase tracking-wider text-slate-500 md:px-4 md:py-3">
              Titulo
            </th>
            <th className="px-2 py-2 text-right text-xs font-medium uppercase tracking-wider text-slate-500 md:px-4 md:py-3">
              Monto
            </th>
            <th className="px-2 py-2 text-right text-xs font-medium uppercase tracking-wider text-slate-500 md:px-4 md:py-3">
              Cuota
            </th>
            <th className="px-2 py-2 text-right text-xs font-medium uppercase tracking-wider text-slate-500 md:px-4 md:py-3">
              Ganancia
            </th>
            <th className="hidden px-2 py-2 text-center text-xs font-medium uppercase tracking-wider text-slate-500 md:table-cell md:px-4 md:py-3">
              Estado
            </th>
            <th className="px-2 py-2 text-right text-xs font-medium uppercase tracking-wider text-slate-500 md:px-4 md:py-3">
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
  );
}

// ─── Fila individual ────────────────────────────────────

interface BetRowProps {
  bet: Bet;
  statuses: BetStatus[];
  onChangeStatus: (bet: Bet) => void;
  onEdit: (bet: Bet) => void;
  onDelete: (bet: Bet) => void;
}

function BetRow({ bet, statuses, onChangeStatus, onEdit, onDelete }: BetRowProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Cerrar menu al hacer click fuera
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

  // Buscar el codigo del status
  const statusCode =
    statuses.find((s) => s.id === bet.status_id)?.code ?? "pending";
  const isFinal = statuses.find((s) => s.id === bet.status_id)?.is_final ?? false;

  // ─── Ganancia segun estado ──────────────────────────────
  const [showTooltip, setShowTooltip] = useState(false);
  const tooltipTimeout = useRef<ReturnType<typeof setTimeout>>(null);

  const profitExpected = Number(bet.profit_expected);

  // Determinar texto, color y tooltip segun estado
  let profitText: string;
  let profitClass: string;
  let tooltipText: string | null = null;

  if (statusCode === "lost") {
    profitText = "$0.00";
    profitClass = "text-rose-600 dark:text-rose-400";
    tooltipText = `+$${profitExpected.toFixed(2)}`;
  } else if (statusCode === "void") {
    profitText = `$${Number(bet.stake_amount).toFixed(2)}`;
    profitClass = "text-slate-400";
  } else {
    // pending o won: mostrar ganancia esperada en verde
    profitText = `+$${profitExpected.toFixed(2)}`;
    profitClass = "text-emerald-600 dark:text-emerald-400";
  }

  const handleTooltipEnter = () => {
    if (tooltipTimeout.current) clearTimeout(tooltipTimeout.current);
    setShowTooltip(true);
  };
  const handleTooltipLeave = () => {
    tooltipTimeout.current = setTimeout(() => setShowTooltip(false), 150);
  };

  return (
    <tr className="transition-colors hover:bg-slate-50 dark:hover:bg-slate-700/50">
      <td className="px-2 py-2 md:px-4 md:py-3">
        <div className="min-w-0">
          <p className="truncate text-xs font-medium text-slate-900 md:text-sm dark:text-slate-100">{bet.title}</p>
          {bet.description && (
            <p className="mt-0.5 text-xs text-slate-400 line-clamp-1">
              {bet.description}
            </p>
          )}
          {/* Estado visible solo en mobile, debajo del titulo */}
          <div className="mt-1 md:hidden">
            <StatusBadge code={statusCode} onClick={!isFinal ? () => onChangeStatus(bet) : undefined} />
          </div>
        </div>
      </td>
      <td className="px-2 py-2 text-right text-xs text-slate-700 md:px-4 md:py-3 md:text-sm dark:text-slate-300">
        ${Number(bet.stake_amount).toFixed(2)}
      </td>
      <td className="px-2 py-2 text-right text-xs text-slate-700 md:px-4 md:py-3 md:text-sm dark:text-slate-300">
        {Number(bet.odds).toFixed(2)}
      </td>
      <td className={`px-2 py-2 text-right text-xs font-medium md:px-4 md:py-3 md:text-sm ${profitClass}`}>
        {tooltipText ? (
          <span
            className="relative cursor-pointer"
            onMouseEnter={handleTooltipEnter}
            onMouseLeave={handleTooltipLeave}
            onTouchStart={handleTooltipEnter}
            onTouchEnd={handleTooltipLeave}
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
      <td className="hidden px-2 py-2 text-center md:table-cell md:px-4 md:py-3">
        <StatusBadge code={statusCode} onClick={!isFinal ? () => onChangeStatus(bet) : undefined} />
      </td>
      <td className="px-1 py-2 text-right md:px-4 md:py-3">
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
                onClick={() => { onEdit(bet); setMenuOpen(false); }}
                className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-slate-700 hover:bg-slate-50 dark:text-slate-300 dark:hover:bg-slate-700"
              >
                <Pencil className="h-4 w-4" />
                Editar
              </button>
              <button
                onClick={() => { onDelete(bet); setMenuOpen(false); }}
                className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-rose-600 hover:bg-rose-50 dark:text-rose-400 dark:hover:bg-rose-900/20"
              >
                <Trash2 className="h-4 w-4" />
                Eliminar
              </button>
            </div>
          )}
        </div>
      </td>
    </tr>
  );
}

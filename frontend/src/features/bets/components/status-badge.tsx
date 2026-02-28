const statusConfig: Record<string, { label: string; className: string }> = {
  pending: {
    label: "Pendiente",
    className: "bg-slate-100 text-slate-700",
  },
  won: {
    label: "Ganada",
    className: "bg-emerald-50 text-emerald-700",
  },
  lost: {
    label: "Perdida",
    className: "bg-rose-50 text-rose-700",
  },
  void: {
    label: "Nula",
    className: "bg-gray-100 text-gray-600",
  },
};

interface StatusBadgeProps {
  code: string;
  onClick?: () => void;
}

export function StatusBadge({ code, onClick }: StatusBadgeProps) {
  const config = statusConfig[code] ?? {
    label: code,
    className: "bg-slate-100 text-slate-700",
  };

  return (
    <span
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
      onClick={onClick}
      onKeyDown={onClick ? (e) => { if (e.key === "Enter" || e.key === " ") onClick(); } : undefined}
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${config.className} ${onClick ? "cursor-pointer ring-offset-1 transition-all hover:ring-2 hover:ring-slate-300" : ""}`}
    >
      {config.label}
    </span>
  );
}

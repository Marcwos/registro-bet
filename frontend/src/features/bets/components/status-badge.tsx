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
}

export function StatusBadge({ code }: StatusBadgeProps) {
  const config = statusConfig[code] ?? {
    label: code,
    className: "bg-slate-100 text-slate-700",
  };

  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${config.className}`}
    >
      {config.label}
    </span>
  );
}

import { motion } from "motion/react";
import type { LucideIcon } from "lucide-react";
import { Tooltip } from "@/shared/components/tooltip";

interface StatCardProps {
  label: string;
  value: string;
  icon: LucideIcon;
  trend?: "positive" | "negative" | "neutral";
  /** Stagger delay index (0, 1, 2…) */
  index?: number;
  /** Extra classes (e.g. col-span for grid placement) */
  className?: string;
  /** Texto informativo que aparece al hacer hover/tap en el icono (i) */
  tooltip?: string;
}

const trendStyles = {
  positive: "text-emerald-600 bg-emerald-50 dark:text-emerald-400 dark:bg-emerald-900/30",
  negative: "text-rose-600 bg-rose-50 dark:text-rose-400 dark:bg-rose-900/30",
  neutral: "text-slate-600 bg-slate-100 dark:text-slate-400 dark:bg-slate-700",
};

const trendBg = {
  positive: "bg-emerald-50/60 border-emerald-200 dark:bg-emerald-900/10 dark:border-emerald-500/20",
  negative: "bg-rose-50/60 border-rose-200 dark:bg-rose-900/10 dark:border-rose-500/20",
  neutral: "bg-white border-slate-200 dark:bg-slate-800 dark:border-slate-700",
};

export function StatCard({ label, value, icon: Icon, trend = "neutral", index = 0, className = "", tooltip }: StatCardProps) {
  return (
    <motion.div
      className={`rounded-2xl border p-3 shadow-sm md:p-6 ${trendBg[trend]} ${className}`}
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.08 }}
    >
      <div className="flex items-center justify-between gap-2">
        <div className="flex min-w-0 items-center gap-1">
          <p className="min-w-0 truncate text-xs font-medium text-slate-500 md:text-sm dark:text-slate-400">{label}</p>
          {tooltip && <Tooltip content={tooltip} />}
        </div>
        <div className={`shrink-0 rounded-lg p-1.5 md:p-2 ${trendStyles[trend]}`}>
          <Icon className="h-4 w-4 md:h-5 md:w-5" />
        </div>
      </div>
      <p className={`mt-1 truncate text-base font-bold md:mt-2 md:text-2xl ${trend === "positive" ? "text-emerald-600 dark:text-emerald-400" : trend === "negative" ? "text-rose-600 dark:text-rose-400" : "text-slate-900 dark:text-slate-100"}`}>
        {value}
      </p>
    </motion.div>
  );
}

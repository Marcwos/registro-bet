import { motion } from "motion/react";
import type { LucideIcon } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string;
  icon: LucideIcon;
  trend?: "positive" | "negative" | "neutral";
  /** Stagger delay index (0, 1, 2…) */
  index?: number;
  /** Extra classes (e.g. col-span for grid placement) */
  className?: string;
}

const trendStyles = {
  positive: "text-emerald-600 bg-emerald-50",
  negative: "text-rose-600 bg-rose-50",
  neutral: "text-slate-600 bg-slate-100",
};

export function StatCard({ label, value, icon: Icon, trend = "neutral", index = 0, className = "" }: StatCardProps) {
  return (
    <motion.div
      className={`rounded-2xl border border-slate-200 bg-white p-3 shadow-sm md:p-6 ${className}`}
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.08 }}
    >
      <div className="flex items-center justify-between gap-2">
        <p className="min-w-0 truncate text-xs font-medium text-slate-500 md:text-sm">{label}</p>
        <div className={`shrink-0 rounded-lg p-1.5 md:p-2 ${trendStyles[trend]}`}>
          <Icon className="h-4 w-4 md:h-5 md:w-5" />
        </div>
      </div>
      <p className={`mt-1 truncate text-base font-bold md:mt-2 md:text-2xl ${trend === "positive" ? "text-emerald-600" : trend === "negative" ? "text-rose-600" : "text-slate-900"}`}>
        {value}
      </p>
    </motion.div>
  );
}

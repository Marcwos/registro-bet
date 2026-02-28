import { motion } from "motion/react";
import type { LucideIcon } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string;
  icon: LucideIcon;
  trend?: "positive" | "negative" | "neutral";
  /** Stagger delay index (0, 1, 2…) */
  index?: number;
}

const trendStyles = {
  positive: "text-emerald-600 bg-emerald-50",
  negative: "text-rose-600 bg-rose-50",
  neutral: "text-slate-600 bg-slate-100",
};

export function StatCard({ label, value, icon: Icon, trend = "neutral", index = 0 }: StatCardProps) {
  return (
    <motion.div
      className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.08 }}
    >
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-slate-500">{label}</p>
        <div className={`rounded-lg p-2 ${trendStyles[trend]}`}>
          <Icon className="h-5 w-5" />
        </div>
      </div>
      <p className={`mt-2 text-2xl font-bold ${trend === "positive" ? "text-emerald-600" : trend === "negative" ? "text-rose-600" : "text-slate-900"}`}>
        {value}
      </p>
    </motion.div>
  );
}

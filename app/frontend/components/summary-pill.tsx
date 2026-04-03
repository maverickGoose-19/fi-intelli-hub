import { SummaryLabel } from "@/lib/types";

const labelMap: Record<SummaryLabel, { label: string; className: string }> = {
  official_update: {
    label: "Official Update",
    className: "bg-red-500/15 text-red-100 ring-red-500/30",
  },
  race_result: {
    label: "Race Result",
    className: "bg-white/10 text-white ring-white/20",
  },
  analysis: {
    label: "Analysis",
    className: "bg-amber-400/15 text-amber-100 ring-amber-300/30",
  },
  prediction: {
    label: "Prediction",
    className: "bg-red-900/40 text-red-100 ring-red-700/40",
  },
};

export function SummaryPill({ label }: { label: SummaryLabel }) {
  const config = labelMap[label];
  return (
    <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] ring-1 ${config.className}`}>
      {config.label}
    </span>
  );
}

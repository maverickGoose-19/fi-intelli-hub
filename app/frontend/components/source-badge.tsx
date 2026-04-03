import { Source } from "@/lib/types";

export function SourceBadge({ source }: { source: Source }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 px-3 py-2">
      <div className="text-sm font-medium text-white">{source.name}</div>
      <div className="mt-1 flex items-center gap-2 text-[11px] uppercase tracking-[0.18em] text-slate-400">
        <span>{source.kind}</span>
        <span className="h-1 w-1 rounded-full bg-slate-500" />
        <span>{source.reliability_tier}</span>
      </div>
    </div>
  );
}


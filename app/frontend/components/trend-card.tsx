import { Cluster } from "@/lib/types";

export function TrendCard({ cluster }: { cluster: Cluster }) {
  return (
    <div className="rounded-[24px] border border-white/10 bg-track-800/60 p-5">
      <div className="text-xs uppercase tracking-[0.2em] text-slate-400">{cluster.trend}</div>
      <div className="mt-3 text-lg font-semibold text-white">{cluster.title}</div>
      <p className="mt-2 text-sm leading-6 text-slate-300">{cluster.summary.body}</p>
    </div>
  );
}


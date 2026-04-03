import Link from "next/link";

import { FreshnessIndicator } from "@/components/freshness-indicator";
import { ProvenanceDrawer } from "@/components/provenance-drawer";
import { SummaryPill } from "@/components/summary-pill";
import { Cluster } from "@/lib/types";

export function ClusterCard({
  cluster,
  compact = false,
}: {
  cluster: Cluster;
  compact?: boolean;
}) {
  return (
    <article className="glow-card rounded-[28px] border border-white/10 bg-black/35 p-5 shadow-panel">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <SummaryPill label={cluster.label} />
        <FreshnessIndicator
          freshness={cluster.freshness}
          updatedAt={cluster.summary.updated_at}
        />
      </div>

      <h3 className="mt-5 text-xl font-semibold text-white">{cluster.summary.title}</h3>
      <p className="mt-3 text-sm leading-7 text-slate-300">
        {cluster.summary.body}
      </p>

      <div className="mt-5 flex flex-wrap gap-2">
        {cluster.entities.slice(0, 4).map((entity) => (
          <span
            key={entity.id}
            className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs uppercase tracking-[0.16em] text-slate-300"
          >
            {entity.name}
          </span>
        ))}
      </div>

      <div className="mt-6 flex flex-wrap items-center justify-between gap-3 border-t border-white/10 pt-4">
        <div className="text-xs uppercase tracking-[0.18em] text-slate-400">
          {cluster.source_count} sources · {cluster.document_count} documents · {Math.round(cluster.confidence * 100)}% confidence
        </div>
        <div className="flex flex-wrap gap-2">
          <ProvenanceDrawer cluster={cluster} />
          <Link
            className="rounded-full border border-red-500/30 bg-red-500/10 px-3 py-1 text-xs font-medium text-red-100 transition hover:border-red-300/60 hover:bg-red-500/20"
            href={`/clusters/${cluster.id}`}
          >
            Open cluster
          </Link>
        </div>
      </div>
    </article>
  );
}

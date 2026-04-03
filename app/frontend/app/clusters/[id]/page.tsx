import { notFound } from "next/navigation";

import { FreshnessIndicator } from "@/components/freshness-indicator";
import { SiteHeader } from "@/components/site-header";
import { SourceBadge } from "@/components/source-badge";
import { SummaryPill } from "@/components/summary-pill";
import { getCluster } from "@/lib/api";

export default async function ClusterDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const cluster = await getCluster(id);

  if (!cluster) {
    notFound();
  }

  return (
    <main className="pb-16">
      <SiteHeader />
      <div className="mx-auto max-w-6xl px-6 lg:px-10">
        <section className="rounded-[36px] border border-white/10 bg-white/[0.045] p-8 shadow-panel">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <SummaryPill label={cluster.label} />
            <FreshnessIndicator freshness={cluster.freshness} updatedAt={cluster.summary.updated_at} />
          </div>
          <h1 className="mt-6 text-5xl font-semibold tracking-tight text-white">{cluster.title}</h1>
          <p className="mt-6 max-w-4xl text-lg leading-8 text-slate-300">{cluster.summary.body}</p>
          <div className="mt-8 flex flex-wrap gap-3">
            {cluster.entities.map((entity) => (
              <span
                key={entity.id}
                className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs uppercase tracking-[0.16em] text-slate-300"
              >
                {entity.name}
              </span>
            ))}
          </div>
        </section>

        <section className="mt-8 grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
          <aside className="rounded-[32px] border border-white/10 bg-track-900/75 p-6 shadow-panel">
            <h2 className="text-xl font-semibold text-white">Provenance stack</h2>
            <div className="mt-5 grid gap-3">
              {cluster.sources.map((source) => (
                <SourceBadge key={source.id} source={source} />
              ))}
            </div>
            <div className="mt-6 rounded-[24px] border border-white/10 bg-white/5 p-5 text-sm text-slate-300">
              <div className="text-xs uppercase tracking-[0.18em] text-slate-400">Weekend context</div>
              <div className="mt-2 text-lg font-medium text-white">{cluster.weekend.name}</div>
              <div className="mt-2">{cluster.weekend.stage.replace("_", " ")} stage</div>
              <div className="mt-4">{cluster.source_count} sources · {cluster.document_count} documents · {Math.round(cluster.confidence * 100)}% confidence</div>
            </div>
          </aside>

          <div className="rounded-[32px] border border-white/10 bg-track-900/75 p-6 shadow-panel">
            <h2 className="text-xl font-semibold text-white">Supporting documents</h2>
            <div className="mt-5 space-y-4">
              {cluster.documents.map((document) => (
                <a
                  key={document.id}
                  className="block rounded-[24px] border border-white/10 bg-white/5 p-5 transition hover:border-cyan-300/35 hover:bg-white/10"
                  href={document.url}
                  rel="noreferrer"
                  target="_blank"
                >
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div>
                      <h3 className="text-lg font-semibold text-white">{document.title}</h3>
                      <p className="mt-3 text-sm uppercase tracking-[0.18em] text-slate-400">
                        {document.kind} · {document.stance} · {document.race_stage.replace("_", " ")}
                      </p>
                    </div>
                    <span className="text-xs text-slate-400">
                      {new Date(document.publish_time).toLocaleString()}
                    </span>
                  </div>
                </a>
              ))}
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}


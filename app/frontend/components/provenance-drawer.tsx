"use client";

import { useState } from "react";

import { Cluster } from "@/lib/types";
import { SourceBadge } from "@/components/source-badge";

export function ProvenanceDrawer({ cluster }: { cluster: Cluster }) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        className="rounded-full border border-white/15 px-3 py-1 text-xs font-medium text-slate-200 transition hover:border-red-400/50 hover:text-white"
        onClick={() => setOpen(true)}
        type="button"
      >
        Inspect provenance
      </button>
      {open ? (
        <div className="fixed inset-0 z-50 flex justify-end bg-slate-950/70 backdrop-blur-sm">
          <div className="h-full w-full max-w-xl overflow-y-auto border-l border-white/10 bg-track-900 px-6 py-8 shadow-panel">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.24em] text-red-200">Provenance</p>
                <h3 className="mt-3 text-2xl font-semibold text-white">{cluster.title}</h3>
              </div>
              <button
                className="rounded-full border border-white/10 px-3 py-1 text-sm text-slate-300"
                onClick={() => setOpen(false)}
                type="button"
              >
                Close
              </button>
            </div>

            <div className="mt-8 space-y-8">
              <section>
                <h4 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">
                  Sources
                </h4>
                <div className="mt-4 grid gap-3">
                  {cluster.sources.map((source) => (
                    <SourceBadge key={source.id} source={source} />
                  ))}
                </div>
              </section>

              <section>
                <h4 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">
                  Documents
                </h4>
                <div className="mt-4 space-y-3">
                  {cluster.documents.map((document) => (
                    <a
                      key={document.id}
                      className="block rounded-2xl border border-white/10 bg-white/5 p-4 transition hover:border-red-400/40 hover:bg-white/10"
                      href={document.url}
                      rel="noreferrer"
                      target="_blank"
                    >
                      <div className="text-sm font-medium text-white">{document.title}</div>
                      <div className="mt-2 text-xs uppercase tracking-[0.18em] text-slate-400">
                        {document.kind} · {document.stance} · {new Date(document.publish_time).toLocaleString()}
                      </div>
                    </a>
                  ))}
                </div>
              </section>
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}

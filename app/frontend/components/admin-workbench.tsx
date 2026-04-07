"use client";

import { useState } from "react";

import { Cluster, EditorialStatus, SummaryLabel } from "@/lib/types";
import { SummaryPill } from "@/components/summary-pill";

const labels: SummaryLabel[] = ["official_update", "race_result", "analysis", "prediction"];
const statuses: EditorialStatus[] = ["draft", "review_required", "approved"];

export function AdminWorkbench({ initialClusters }: { initialClusters: Cluster[] }) {
  const [clusters, setClusters] = useState(initialClusters);
  const [message, setMessage] = useState<string | null>(null);
  const [isPending, setIsPending] = useState(false);

  function updateLocalCluster(clusterId: string, updater: (cluster: Cluster) => Cluster) {
    setClusters((current) => current.map((cluster) => (cluster.id === clusterId ? updater(cluster) : cluster)));
  }

  function handleResummarize(clusterId: string) {
    setMessage(null);
    setIsPending(true);
    void (async () => {
      try {
        const response = await fetch(`/api/clusters/${clusterId}/resummarize`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        });
        if (response.ok) {
          const payload = (await response.json()) as { cluster: Cluster };
          updateLocalCluster(clusterId, () => payload.cluster);
          setMessage("Cluster resummarized from the API.");
          return;
        }
      } catch {
        // fallback below
      }

      updateLocalCluster(clusterId, (cluster) => ({
        ...cluster,
        summary: {
          ...cluster.summary,
          updated_at: new Date().toISOString(),
          body: `Manual editorial refresh: ${cluster.summary.body}`,
        },
      }));
      setMessage("Backend unavailable, so the resummarize action was simulated locally.");
    })().finally(() => setIsPending(false));
  }

  function handlePatch(clusterId: string, patch: { label: SummaryLabel; editorial_status: EditorialStatus }) {
    const cluster = clusters.find((item) => item.id === clusterId);
    if (!cluster) {
      return;
    }
    setMessage(null);
    setIsPending(true);
    void (async () => {
      try {
        const response = await fetch(`/api/summaries/${cluster.summary.id}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(patch),
        });
        if (response.ok) {
          const payload = (await response.json()) as { summary: Cluster["summary"] };
          updateLocalCluster(clusterId, (current) => ({
            ...current,
            label: patch.label,
            summary: payload.summary,
          }));
          setMessage("Editorial patch saved to the API.");
          return;
        }
      } catch {
        // fallback below
      }

      updateLocalCluster(clusterId, (current) => ({
        ...current,
        label: patch.label,
        summary: {
          ...current.summary,
          label: patch.label,
          editorial_status: patch.editorial_status,
          updated_at: new Date().toISOString(),
        },
      }));
      setMessage("Backend unavailable, so the editorial update was applied locally.");
    })().finally(() => setIsPending(false));
  }

  return (
    <div className="space-y-6">
      <div className="rounded-[28px] border border-white/10 bg-black/35 p-5 text-sm text-slate-300">
        Approvals keep fact surfaces distinct from prediction surfaces. Resummarize rebuilds the source-backed summary body without changing provenance.
      </div>
      {message ? (
        <div className="rounded-2xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-100">
          {message}
        </div>
      ) : null}
      <div className="grid gap-5">
        {clusters.map((cluster) => (
          <div key={cluster.id} className="rounded-[28px] border border-white/10 bg-black/45 p-6">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div className="max-w-2xl">
                <SummaryPill label={cluster.label} />
                <h3 className="mt-4 text-2xl font-semibold text-white">{cluster.summary.title}</h3>
                <p className="mt-3 text-sm leading-7 text-slate-300">{cluster.summary.body}</p>
              </div>
              <button
                className="rounded-full border border-red-500/30 bg-red-500/10 px-4 py-2 text-sm font-medium text-red-100"
                disabled={isPending}
                onClick={() => handleResummarize(cluster.id)}
                type="button"
              >
                Resummarize
              </button>
            </div>

            <div className="mt-6 grid gap-4 md:grid-cols-2">
              <label className="text-sm text-slate-300">
                Label
                <select
                  className="mt-2 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white"
                  defaultValue={cluster.label}
                  onChange={(event) =>
                    handlePatch(cluster.id, {
                      label: event.target.value as SummaryLabel,
                      editorial_status: cluster.summary.editorial_status,
                    })
                  }
                >
                  {labels.map((label) => (
                    <option key={label} value={label}>
                      {label}
                    </option>
                  ))}
                </select>
              </label>
              <label className="text-sm text-slate-300">
                Editorial status
                <select
                  className="mt-2 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white"
                  defaultValue={cluster.summary.editorial_status}
                  onChange={(event) =>
                    handlePatch(cluster.id, {
                      label: cluster.label,
                      editorial_status: event.target.value as EditorialStatus,
                    })
                  }
                >
                  {statuses.map((status) => (
                    <option key={status} value={status}>
                      {status}
                    </option>
                  ))}
                </select>
              </label>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

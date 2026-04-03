"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";

import { syncLatestOpenF1 } from "@/lib/api";

export function SyncButton({
  status,
  message,
}: {
  status: string;
  message: string;
}) {
  const router = useRouter();
  const [feedback, setFeedback] = useState<string | null>(message || null);
  const [isPending, startTransition] = useTransition();
  const [syncMode, setSyncMode] = useState<"full" | "quick" | null>(null);

  function handleSync(mode: "full" | "quick") {
    setSyncMode(mode);
    setFeedback(null);
    void syncLatestOpenF1(mode === "full")
      .then((payload) => {
        setFeedback(payload.sync.message || "OpenF1 sync complete. Refreshing the dashboard.");
        startTransition(() => {
          router.refresh();
        });
      })
      .catch((error: Error) => {
        setFeedback(error.message || "OpenF1 sync failed.");
      })
      .finally(() => setSyncMode(null));
  }

  const disabled = syncMode !== null || isPending;

  return (
    <div className="rounded-[24px] border border-white/10 bg-black/35 p-5">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Live control</p>
          <h3 className="mt-2 text-lg font-semibold text-white">Sync latest OpenF1 data</h3>
          <p className="mt-2 text-sm text-slate-300">
            Quick sync updates session and standings data only. Full sync also pulls articles and refreshes editorial.
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          <button
            className="rounded-full border border-white/15 bg-white/5 px-4 py-2 text-sm font-medium text-white transition hover:border-white/30 hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={disabled}
            onClick={() => handleSync("quick")}
            type="button"
          >
            {syncMode === "quick" ? "Quick syncing..." : "Quick sync"}
          </button>
          <button
            className="rounded-full border border-red-500/30 bg-red-500/10 px-4 py-2 text-sm font-medium text-red-100 transition hover:border-red-300/50 hover:bg-red-500/20 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={disabled}
            onClick={() => handleSync("full")}
            type="button"
          >
            {syncMode === "full" ? "Full syncing..." : "Full sync"}
          </button>
        </div>
      </div>
      <div className="mt-4 text-xs uppercase tracking-[0.18em] text-slate-500">
        Status: {status}
      </div>
      {feedback ? <div className="mt-2 text-sm text-slate-300">{feedback}</div> : null}
    </div>
  );
}

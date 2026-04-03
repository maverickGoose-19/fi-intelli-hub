"use client";

import { useMemo, useState } from "react";

import { SessionResultsBoard } from "@/components/session-results-board";
import { CompletedWeekendResult } from "@/lib/types";

export function CompletedWeekendResults({
  weekends,
}: {
  weekends: CompletedWeekendResult[];
}) {
  const orderedWeekends = useMemo(() => [...weekends].reverse(), [weekends]);
  const [selectedWeekendId, setSelectedWeekendId] = useState(orderedWeekends[0]?.id || "");

  const selectedWeekend =
    orderedWeekends.find((weekend) => weekend.id === selectedWeekendId) || orderedWeekends[0];

  if (!selectedWeekend) {
    return (
      <section className="rounded-[32px] border border-white/10 bg-black/35 p-6 shadow-panel">
        <div className="text-sm text-slate-300">Completed race-weekend timing will appear here after results land.</div>
      </section>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-4 rounded-[28px] border border-white/10 bg-black/25 px-5 py-4">
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Completed weekends</p>
          <h3 className="mt-2 text-xl font-semibold text-white">Race results and timing</h3>
        </div>
        <label className="min-w-[240px] text-sm text-slate-300">
          <span className="sr-only">Select completed race weekend</span>
          <select
            className="w-full rounded-2xl border border-white/10 bg-black/40 px-4 py-3 text-white"
            onChange={(event) => setSelectedWeekendId(event.target.value)}
            value={selectedWeekend.id}
          >
            {orderedWeekends.map((weekend) => (
              <option key={weekend.id} value={weekend.id}>
                {weekend.name}
              </option>
            ))}
          </select>
        </label>
      </div>

      <SessionResultsBoard
        title={selectedWeekend.name}
        subtitle={`${selectedWeekend.date_range || ""} · practices, qualifying, race`}
        sessions={selectedWeekend.sessions}
      />
    </div>
  );
}

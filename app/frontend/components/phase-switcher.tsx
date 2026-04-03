"use client";

import { useState } from "react";

import { TimelinePhase } from "@/lib/types";

export function PhaseSwitcher({ timeline }: { timeline: TimelinePhase[] }) {
  const [activePhase, setActivePhase] = useState(timeline.find((phase) => phase.state === "active")?.phase || timeline[0]?.phase);

  const activeItem = timeline.find((phase) => phase.phase === activePhase) || timeline[0];

  return (
    <div className="rounded-[32px] border border-white/10 bg-white/[0.04] p-6 shadow-panel">
      <div className="flex flex-wrap gap-3">
        {timeline.map((phase) => {
          const selected = phase.phase === activePhase;
          return (
            <button
              key={phase.phase}
              className={`rounded-full px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] transition ${
                selected
                  ? "bg-red-500 text-white"
                  : "border border-white/10 bg-white/5 text-slate-300 hover:border-white/20 hover:bg-white/10"
              }`}
              onClick={() => setActivePhase(phase.phase)}
              type="button"
            >
              {phase.phase.replace("_", " ")}
            </button>
          );
        })}
      </div>

      <div className="mt-8 rounded-[24px] border border-white/10 bg-black/45 p-6">
        <div className="flex items-center justify-between gap-4">
          <h3 className="text-2xl font-semibold text-white">
            {activeItem.phase.replace("_", " ")}
          </h3>
          <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs uppercase tracking-[0.18em] text-slate-300">
            {activeItem.state}
          </span>
        </div>
        <p className="mt-4 text-lg leading-8 text-slate-100">{activeItem.headline}</p>
        <p className="mt-3 text-sm uppercase tracking-[0.18em] text-red-200">
          Focus: {activeItem.focus}
        </p>
      </div>
    </div>
  );
}

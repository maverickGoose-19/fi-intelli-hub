import { DashboardResponse } from "@/lib/types";

export function NextRacePrediction({
  prediction,
  sessions,
}: {
  prediction: DashboardResponse["next_race_prediction"];
  sessions: DashboardResponse["season"]["next_race_sessions"];
}) {
  return (
    <section className="rounded-[32px] border border-red-500/20 bg-gradient-to-br from-red-600/20 to-black p-6 shadow-panel">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-red-200">Next race outlook</p>
          <h3 className="mt-3 text-2xl font-semibold text-white">{prediction.race_name}</h3>
          <p className="mt-2 text-sm text-red-100">
            {prediction.date_range} · {prediction.weekend_format} weekend
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-3">
        {prediction.top_three.map((entry) => (
          <div key={`${entry.position}-${entry.driver}`} className="rounded-[24px] border border-white/10 bg-black/30 p-5">
            <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Predicted P{entry.position}</p>
            <h4 className="mt-3 text-xl font-semibold text-white">{entry.driver}</h4>
            <p className="mt-2 text-sm text-slate-300">{entry.team}</p>
          </div>
        ))}
      </div>

      <p className="mt-6 text-sm leading-7 text-slate-200">{prediction.reason}</p>

      <div className="mt-6 rounded-[24px] border border-white/10 bg-black/30 p-5">
        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Next-race timetable</p>
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {sessions.map((session) => (
            <div key={session.name} className="rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3">
              <div className="text-sm font-medium text-white">{session.name}</div>
              <div className="mt-1 text-[11px] uppercase tracking-[0.18em] text-slate-500">
                {session.time_local}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

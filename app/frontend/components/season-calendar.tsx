import { ScheduleRace } from "@/lib/types";

export function SeasonCalendar({ races }: { races: ScheduleRace[] }) {
  return (
    <section className="rounded-[32px] border border-white/10 bg-black/35 p-6 shadow-panel">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Official calendar</p>
          <h3 className="mt-3 text-2xl font-semibold text-white">2026 Formula 1 schedule</h3>
        </div>
        <p className="text-xs uppercase tracking-[0.18em] text-slate-500">{races.length} rounds</p>
      </div>

      <div className="mt-6 overflow-hidden rounded-[24px] border border-white/10">
        <table className="min-w-full text-left">
          <thead className="bg-white/5 text-xs uppercase tracking-[0.2em] text-slate-500">
            <tr>
              <th className="px-4 py-3">Round</th>
              <th className="px-4 py-3">Grand Prix</th>
              <th className="px-4 py-3">Dates</th>
              <th className="px-4 py-3">Venue</th>
              <th className="px-4 py-3">Status</th>
            </tr>
          </thead>
          <tbody>
            {races.map((race) => (
              <tr key={`${race.round}-${race.grand_prix}`} className="border-t border-white/10 bg-black/20 text-sm text-slate-200">
                <td className="px-4 py-3 font-semibold text-white">{race.round}</td>
                <td className="px-4 py-3">
                  <div className="font-medium text-white">{race.grand_prix}</div>
                  {race.winner ? (
                    <div className="mt-1 text-[11px] uppercase tracking-[0.18em] text-slate-500">
                      Winner: {race.winner} · {race.winner_team}
                    </div>
                  ) : null}
                </td>
                <td className="px-4 py-3">{race.date_range}</td>
                <td className="px-4 py-3">{race.venue}</td>
                <td className="px-4 py-3">
                  <span
                    className={`rounded-full px-3 py-1 text-[11px] uppercase tracking-[0.16em] ${
                      race.status === "completed"
                        ? "border border-white/10 bg-white/5 text-slate-300"
                        : race.status === "next"
                          ? "border border-red-500/30 bg-red-500/10 text-red-100"
                          : "border border-white/10 bg-black/30 text-slate-500"
                    }`}
                  >
                    {race.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}


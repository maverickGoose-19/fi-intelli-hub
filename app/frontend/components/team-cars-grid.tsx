import { TeamCarWatch } from "@/lib/types";

export function TeamCarsGrid({ teams }: { teams: TeamCarWatch[] }) {
  return (
    <section className="rounded-[32px] border border-white/10 bg-black/35 p-6 shadow-panel">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Team by team</p>
          <h3 className="mt-3 text-2xl font-semibold text-white">Car watch and update status</h3>
        </div>
        <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
          Update status comes from the current ingested feed
        </p>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {teams.map((team) => (
          <div key={team.team} className="rounded-[24px] border border-white/10 bg-white/[0.03] p-5">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
                  P{team.championship_position} constructors
                </p>
                <h4 className="mt-2 text-xl font-semibold text-white">{team.team}</h4>
              </div>
              <div className="rounded-2xl border border-red-500/25 bg-red-500/10 px-3 py-2 text-right">
                <div className="text-xs uppercase tracking-[0.16em] text-red-100">Pts</div>
                <div className="mt-1 text-lg font-semibold text-white">{team.points}</div>
              </div>
            </div>

            <div className="mt-4 space-y-3">
              {team.drivers.map((driver) => (
                <div key={`${team.team}-${driver.name}`} className="flex items-center justify-between rounded-2xl border border-white/10 bg-black/25 px-4 py-3">
                  <div>
                    <div className="text-sm font-medium text-white">{driver.name}</div>
                    <div className="mt-1 text-[11px] uppercase tracking-[0.18em] text-slate-500">
                      {driver.code || driver.name.slice(0, 3).toUpperCase()} · P{driver.position}
                    </div>
                  </div>
                  <div className="text-sm text-slate-200">{driver.points} pts</div>
                </div>
              ))}
            </div>

            <div className="mt-4 rounded-2xl border border-white/10 bg-black/25 p-4">
              <div className="text-[11px] uppercase tracking-[0.18em] text-slate-500">Current update read</div>
              <p className="mt-2 text-sm leading-6 text-slate-300">{team.update_status}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}


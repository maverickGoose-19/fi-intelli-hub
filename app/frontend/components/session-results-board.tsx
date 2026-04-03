import { SessionResult } from "@/lib/types";
import { getTeamColor } from "@/lib/team-colors";

export function SessionResultsBoard({
  title,
  subtitle,
  sessions,
}: {
  title: string;
  subtitle: string;
  sessions: SessionResult[];
}) {
  return (
    <section className="rounded-[32px] border border-white/10 bg-black/35 p-6 shadow-panel">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">{subtitle}</p>
          <h3 className="mt-3 text-2xl font-semibold text-white">{title}</h3>
        </div>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        {sessions.map((session) => (
          <div key={session.name} className="rounded-[24px] border border-white/10 bg-white/[0.03] p-5">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="min-w-0">
                <p className="text-xs uppercase tracking-[0.18em] text-slate-500">{session.category}</p>
                <h4 className="mt-2 text-lg font-semibold text-white">{session.name}</h4>
              </div>
              <span className="shrink-0 whitespace-nowrap rounded-full border border-red-500/30 bg-red-500/10 px-3 py-1 text-[10px] uppercase tracking-[0.14em] text-red-100 sm:text-[11px]">
                {session.status}
              </span>
            </div>
            <div className="mt-4 space-y-3">
              {session.entries.map((entry) => (
                <div
                  key={`${session.name}-${entry.position}-${entry.driver}`}
                  className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-3 rounded-2xl border border-white/10 bg-black/25 px-4 py-3"
                  style={{ boxShadow: `inset 3px 0 0 ${getTeamColor(entry.team)}` }}
                >
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span
                        className="h-2.5 w-2.5 shrink-0 rounded-full"
                        style={{ backgroundColor: getTeamColor(entry.team) }}
                      />
                      <div className="truncate text-sm font-medium text-white">
                        {entry.position}. {entry.driver}
                      </div>
                    </div>
                    <div className="mt-1 truncate text-[11px] uppercase tracking-[0.18em] text-slate-500">
                      {entry.team}
                    </div>
                  </div>
                  <div className="min-w-[88px] text-right">
                    <div className="overflow-hidden text-ellipsis whitespace-nowrap font-mono text-xs font-medium text-slate-100 sm:text-sm">
                      {entry.metric}
                    </div>
                    {entry.points ? (
                      <div className="mt-1 whitespace-nowrap text-[11px] uppercase tracking-[0.18em] text-slate-500">
                        {entry.points} pts
                      </div>
                    ) : null}
                  </div>
                </div>
              ))}
            </div>
            <a
              className="mt-4 inline-block text-xs uppercase tracking-[0.18em] text-red-200 transition hover:text-white"
              href={session.source_url}
              rel="noreferrer"
              target="_blank"
            >
              Official session source
            </a>
          </div>
        ))}
      </div>
    </section>
  );
}

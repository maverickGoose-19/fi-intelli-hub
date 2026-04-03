import { StandingEntry } from "@/lib/types";
import { getTeamColor } from "@/lib/team-colors";

export function StandingsTable({
  title,
  subtitle,
  entries,
  variant,
}: {
  title: string;
  subtitle: string;
  entries: StandingEntry[];
  variant: "drivers" | "constructors";
}) {
  return (
    <section className="rounded-[28px] border border-white/10 bg-black/35 p-6 shadow-panel">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">{subtitle}</p>
          <h3 className="mt-3 text-2xl font-semibold text-white">{title}</h3>
        </div>
        <p className="text-xs uppercase tracking-[0.18em] text-slate-500">{entries.length} entries</p>
      </div>

      <div className="mt-6 overflow-hidden rounded-[24px] border border-white/10">
        <table className="min-w-full text-left">
          <thead className="bg-white/5 text-xs uppercase tracking-[0.2em] text-slate-500">
            <tr>
              <th className="px-4 py-3">Pos</th>
              <th className="px-4 py-3">{variant === "drivers" ? "Driver" : "Team"}</th>
              {variant === "drivers" ? <th className="px-4 py-3">Team</th> : null}
              <th className="px-4 py-3 text-right">Pts</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((entry) => (
              <tr
                key={`${variant}-${entry.position}-${entry.name}`}
                className="border-t border-white/10 bg-black/20 text-sm text-slate-200"
                style={{
                  boxShadow:
                    variant === "drivers"
                      ? `inset 3px 0 0 ${getTeamColor(entry.team)}`
                      : `inset 3px 0 0 ${getTeamColor(entry.name)}`,
                }}
              >
                <td className="px-4 py-3 font-semibold text-white">{entry.position}</td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <span
                      className="h-2.5 w-2.5 shrink-0 rounded-full"
                      style={{ backgroundColor: getTeamColor(variant === "drivers" ? entry.team : entry.name) }}
                    />
                    <div className="font-medium text-white">{entry.name}</div>
                  </div>
                  {entry.code ? (
                    <div className="mt-1 text-[11px] uppercase tracking-[0.18em] text-slate-500">
                      {entry.code} {entry.nationality ? `· ${entry.nationality}` : ""}
                    </div>
                  ) : null}
                </td>
                {variant === "drivers" ? <td className="px-4 py-3 text-slate-300">{entry.team}</td> : null}
                <td className="px-4 py-3 text-right text-white">{entry.points}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

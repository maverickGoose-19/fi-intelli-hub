import Link from "next/link";

import { SiteHeader } from "@/components/site-header";
import { getPredictionAnalytics } from "@/lib/api";

export const dynamic = "force-dynamic";

function percent(value: number) {
  return `${(value * 100).toFixed(1)}%`;
}

function scoreWidth(value: number) {
  return `${Math.max(8, Math.round(value * 100))}%`;
}

export default async function PredictionsPage() {
  const analytics = await getPredictionAnalytics();
  const favorite = analytics.contenders[0];
  const keyFeatureSlice = favorite?.features.slice(0, 6) ?? [];

  return (
    <main className="pb-16">
      <SiteHeader />
      <div className="mx-auto flex max-w-7xl flex-col gap-8 px-4 sm:px-6 lg:px-10">
        <section className="grid gap-6 lg:grid-cols-[1.25fr_0.75fr]">
          <div className="glow-card overflow-hidden rounded-[28px] border border-white/10 bg-black/45 p-5 shadow-panel sm:rounded-[36px] sm:p-8">
            <div className="data-kicker">Prediction Lab</div>
            <div className="mt-6 flex flex-col items-start gap-5 sm:mt-8 lg:flex-row lg:items-start lg:justify-between lg:gap-6">
              <div className="min-w-0 max-w-3xl">
                <h1 className="text-3xl font-semibold leading-tight tracking-tight text-white sm:text-5xl md:text-6xl">
                  {analytics.race.name} winner model
                </h1>
                <p className="mt-4 max-w-2xl text-base leading-7 text-slate-300 sm:mt-5 sm:text-lg sm:leading-8">
                  {analytics.model.overview}
                </p>
              </div>
              <div className="w-full rounded-[24px] border border-emerald-500/20 bg-emerald-500/10 px-4 py-4 sm:w-auto sm:rounded-[28px] sm:px-5">
                <div className="text-xs uppercase tracking-[0.24em] text-emerald-100">Model confidence</div>
                <div className="mt-2 text-2xl font-semibold text-white">{analytics.model.confidence}</div>
                <div className="mt-1 text-sm text-emerald-100">{analytics.model.training.blend}</div>
              </div>
            </div>

            <div className="mt-10 grid gap-4 md:grid-cols-3">
              <div className="rounded-[24px] border border-white/10 bg-black/35 p-5">
                <div className="text-xs uppercase tracking-[0.18em] text-slate-500">Favorite</div>
                <div className="mt-3 text-3xl font-semibold text-white">{favorite?.driver}</div>
                <div className="mt-2 text-sm text-slate-300">{favorite?.team}</div>
                <div className="mt-5 text-sm text-emerald-100">{favorite ? percent(favorite.win_probability) : "-"}</div>
              </div>
              <div className="rounded-[24px] border border-white/10 bg-black/35 p-5">
                <div className="text-xs uppercase tracking-[0.18em] text-slate-500">Weekend format</div>
                <div className="mt-3 text-3xl font-semibold text-white">{analytics.race.weekend_format}</div>
                <div className="mt-2 text-sm text-slate-300">{analytics.race.date_range}</div>
              </div>
              <div className="rounded-[24px] border border-white/10 bg-black/35 p-5">
                <div className="text-xs uppercase tracking-[0.18em] text-slate-500">Training sample</div>
                <div className="mt-3 text-3xl font-semibold text-white">
                  {analytics.model.training.completed_races} races
                </div>
                <div className="mt-2 text-sm text-slate-300">
                  {analytics.model.training.observations} labeled driver-weekend rows
                </div>
              </div>
            </div>
          </div>

          <aside className="overflow-hidden rounded-[28px] border border-white/10 bg-black/45 p-5 shadow-panel sm:rounded-[36px] sm:p-8">
            <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Track model</p>
            <div className="mt-6 space-y-4">
              <div className="rounded-[24px] border border-white/10 bg-white/5 p-5">
                <div className="text-sm text-slate-400">Venue</div>
                <div className="mt-2 break-words text-2xl font-semibold text-white">{analytics.race.venue}</div>
                <div className="mt-2 text-sm text-slate-300">{analytics.track.track_type}</div>
              </div>
              <div className="rounded-[24px] border border-white/10 bg-white/5 p-5">
                <div className="text-xs uppercase tracking-[0.18em] text-slate-500">Expected strategy</div>
                <p className="mt-3 text-sm leading-7 text-slate-200">{analytics.track.expected_strategy}</p>
              </div>
              <div className="rounded-[24px] border border-white/10 bg-white/5 p-5">
                <div className="text-xs uppercase tracking-[0.18em] text-slate-500">Tyre outlook</div>
                <p className="mt-3 text-sm leading-7 text-slate-200">{analytics.track.tyre_outlook}</p>
              </div>
            </div>
          </aside>
        </section>

        <section className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
          <div className="rounded-[32px] border border-white/10 bg-black/40 p-7">
            <div className="flex items-center justify-between gap-4">
              <div>
                <h2 className="text-2xl font-semibold text-white">Podium projection</h2>
                <p className="mt-2 text-sm text-slate-400">Current win and podium probabilities for the leading contenders.</p>
              </div>
              <Link
                href="/"
                className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-300 transition hover:bg-white/10 hover:text-white"
              >
                Back to dashboard
              </Link>
            </div>
            <div className="mt-6 grid gap-4">
              {analytics.contenders.slice(0, 5).map((contender) => (
                <div
                  key={contender.driver}
                  className="rounded-[24px] border border-white/10 bg-white/5 p-5"
                >
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div>
                      <div className="text-xs uppercase tracking-[0.18em] text-slate-500">
                        P{contender.rank} · {contender.confidence}
                      </div>
                      <div className="mt-2 text-2xl font-semibold text-white">{contender.driver}</div>
                      <div className="mt-1 text-sm text-slate-300">{contender.team}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-3xl font-semibold text-white">{percent(contender.win_probability)}</div>
                      <div className="mt-1 text-sm text-slate-300">Win probability</div>
                    </div>
                  </div>
                  <div className="mt-4 grid gap-3 md:grid-cols-2">
                    <div>
                      <div className="flex items-center justify-between text-xs uppercase tracking-[0.18em] text-slate-500">
                        <span>Win</span>
                        <span>{percent(contender.win_probability)}</span>
                      </div>
                      <div className="mt-2 h-2 overflow-hidden rounded-full bg-white/10">
                        <div
                          className="h-full rounded-full bg-[linear-gradient(90deg,#E10600_0%,#FF5A36_45%,#FFD166_100%)]"
                          style={{ width: scoreWidth(contender.win_probability) }}
                        />
                      </div>
                    </div>
                    <div>
                      <div className="flex items-center justify-between text-xs uppercase tracking-[0.18em] text-slate-500">
                        <span>Podium</span>
                        <span>{percent(contender.podium_probability)}</span>
                      </div>
                      <div className="mt-2 h-2 overflow-hidden rounded-full bg-white/10">
                        <div
                          className="h-full rounded-full bg-[linear-gradient(90deg,#38BDF8_0%,#22C55E_100%)]"
                          style={{ width: scoreWidth(contender.podium_probability) }}
                        />
                      </div>
                    </div>
                  </div>
                  <p className="mt-4 text-sm leading-7 text-slate-300">{contender.outlook}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-[32px] border border-white/10 bg-black/40 p-7">
            <h2 className="text-2xl font-semibold text-white">Favorite breakdown</h2>
            <p className="mt-2 text-sm text-slate-400">
              The top prediction is scored across championship form, qualifying pace, track fit, tyres, and strategy.
            </p>
            <div className="mt-6 grid gap-4">
              {keyFeatureSlice.map((feature) => (
                <div key={feature.key} className="rounded-[24px] border border-white/10 bg-white/5 p-5">
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <div className="text-sm font-medium text-white">{feature.label}</div>
                      <div className="mt-1 text-sm text-slate-400">{feature.impact}</div>
                    </div>
                    <div className="text-lg font-semibold text-white">{feature.display_value}</div>
                  </div>
                  <div className="mt-4 h-2 overflow-hidden rounded-full bg-white/10">
                    <div
                      className="h-full rounded-full bg-[linear-gradient(90deg,#E10600_0%,#F97316_50%,#FACC15_100%)]"
                      style={{ width: scoreWidth(feature.value) }}
                    />
                  </div>
                </div>
              ))}
              <div className="rounded-[24px] border border-white/10 bg-white/5 p-5">
                <div className="text-xs uppercase tracking-[0.18em] text-slate-500">Why the model leans this way</div>
                <div className="mt-4 grid gap-3">
                  {favorite?.evidence.map((item) => (
                    <div key={item} className="rounded-2xl border border-white/10 bg-black/30 px-4 py-3 text-sm text-slate-200">
                      {item}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
          <div className="rounded-[32px] border border-white/10 bg-black/40 p-7">
            <h2 className="text-2xl font-semibold text-white">Feature importance</h2>
            <p className="mt-2 text-sm text-slate-400">What the model weighted most strongly in this forecast.</p>
            <div className="mt-6 grid gap-4">
              {analytics.feature_importance.map((item) => (
                <div key={item.label} className="rounded-[24px] border border-white/10 bg-white/5 p-5">
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <div className="text-sm font-medium text-white">{item.label}</div>
                      <div className="mt-1 text-sm text-slate-400">{item.description}</div>
                    </div>
                    <div className="text-sm font-semibold text-white">{percent(item.value)}</div>
                  </div>
                  <div className="mt-4 h-2 overflow-hidden rounded-full bg-white/10">
                    <div
                      className="h-full rounded-full bg-[linear-gradient(90deg,#EF4444_0%,#FB7185_50%,#F59E0B_100%)]"
                      style={{ width: scoreWidth(item.value) }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-[32px] border border-white/10 bg-black/40 p-7">
            <h2 className="text-2xl font-semibold text-white">Scenario matrix</h2>
            <p className="mt-2 text-sm text-slate-400">How the forecast changes when the race shape moves away from the base case.</p>
            <div className="mt-6 grid gap-4">
              {analytics.scenario_matrix.map((scenario) => (
                <div key={scenario.title} className="rounded-[24px] border border-white/10 bg-white/5 p-5">
                  <div className="text-lg font-semibold text-white">{scenario.title}</div>
                  <p className="mt-3 text-sm leading-7 text-slate-300">{scenario.description}</p>
                  <div className="mt-4 rounded-2xl border border-amber-400/20 bg-amber-400/10 px-4 py-3 text-sm text-amber-100">
                    {scenario.effect}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="rounded-[32px] border border-white/10 bg-black/40 p-7">
          <h2 className="text-2xl font-semibold text-white">Contender table</h2>
          <p className="mt-2 text-sm text-slate-400">Full field view with the blended model score, win odds, and podium odds.</p>
          <div className="mt-6 overflow-hidden rounded-[24px] border border-white/10">
            <div className="grid grid-cols-[56px_1.2fr_0.9fr_0.8fr_0.8fr] border-b border-white/10 bg-white/5 px-5 py-4 text-xs uppercase tracking-[0.18em] text-slate-500">
              <div>Rank</div>
              <div>Driver</div>
              <div>Team</div>
              <div>Win</div>
              <div>Podium</div>
            </div>
            {analytics.contenders.map((contender) => (
              <div
                key={contender.driver}
                className="grid grid-cols-[56px_1.2fr_0.9fr_0.8fr_0.8fr] gap-2 border-b border-white/10 px-5 py-4 text-sm text-slate-200 last:border-b-0"
              >
                <div className="font-semibold text-white">{contender.rank}</div>
                <div>
                  <div className="font-medium text-white">{contender.driver}</div>
                  <div className="mt-1 text-xs uppercase tracking-[0.16em] text-slate-500">
                    {contender.confidence} confidence
                  </div>
                </div>
                <div>{contender.team}</div>
                <div>{percent(contender.win_probability)}</div>
                <div>{percent(contender.podium_probability)}</div>
              </div>
            ))}
          </div>
        </section>

        <section className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
          <div className="rounded-[32px] border border-white/10 bg-black/40 p-7">
            <h2 className="text-2xl font-semibold text-white">Constructor outlook</h2>
            <p className="mt-2 text-sm text-slate-400">Car-formula and tyre-strength view by team.</p>
            <div className="mt-6 grid gap-4">
              {analytics.constructor_outlook.map((team) => (
                <div key={team.team} className="rounded-[24px] border border-white/10 bg-white/5 p-5">
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div>
                      <div className="text-lg font-semibold text-white">{team.team}</div>
                      <div className="mt-1 text-sm text-slate-400">{team.car_formula}</div>
                    </div>
                    <div className="text-sm text-slate-300">{percent(team.power_score)} power score</div>
                  </div>
                  <div className="mt-4 grid gap-3 md:grid-cols-3">
                    {[
                      { label: "Qualifying", value: team.qualifying_score },
                      { label: "Tyres", value: team.tyre_score },
                      { label: "Reliability", value: team.reliability },
                    ].map((metric) => (
                      <div key={metric.label} className="rounded-2xl border border-white/10 bg-black/30 p-4">
                        <div className="text-xs uppercase tracking-[0.16em] text-slate-500">{metric.label}</div>
                        <div className="mt-2 text-xl font-semibold text-white">{percent(metric.value)}</div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-[32px] border border-white/10 bg-black/40 p-7">
            <h2 className="text-2xl font-semibold text-white">Resource stack</h2>
            <p className="mt-2 text-sm text-slate-400">
              Sources and modeling references used to shape this page and the prediction service.
            </p>
            <div className="mt-6 grid gap-4">
              {analytics.source_stack.map((source) => (
                <a
                  key={source.label}
                  href={source.url}
                  target="_blank"
                  rel="noreferrer"
                  className="rounded-[24px] border border-white/10 bg-white/5 p-5 transition hover:border-red-500/30 hover:bg-white/[0.08]"
                >
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div className="text-lg font-semibold text-white">{source.label}</div>
                    <div className="rounded-full border border-white/10 bg-black/30 px-3 py-1 text-xs uppercase tracking-[0.18em] text-slate-400">
                      {source.kind}
                    </div>
                  </div>
                  <p className="mt-3 text-sm leading-7 text-slate-300">{source.role}</p>
                </a>
              ))}
            </div>
          </div>
        </section>

        <section className="rounded-[32px] border border-white/10 bg-black/40 p-7">
          <h2 className="text-2xl font-semibold text-white">Method notes</h2>
          <div className="mt-4 grid gap-3">
            {analytics.model.notes.map((note) => (
              <div key={note} className="rounded-[20px] border border-white/10 bg-white/5 px-5 py-4 text-sm leading-7 text-slate-300">
                {note}
              </div>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}

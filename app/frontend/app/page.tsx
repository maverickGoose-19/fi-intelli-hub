import { ArticleFeed } from "@/components/article-feed";
import { ClusterCard } from "@/components/cluster-card";
import { CompletedWeekendResults } from "@/components/completed-weekend-results";
import { NextRacePrediction } from "@/components/next-race-prediction";
import { PhaseSwitcher } from "@/components/phase-switcher";
import { PerformanceCharts } from "@/components/performance-charts";
import { SeasonCalendar } from "@/components/season-calendar";
import { SiteHeader } from "@/components/site-header";
import { StandingsTable } from "@/components/standings-table";
import { SyncButton } from "@/components/sync-button";
import { TeamCarsGrid } from "@/components/team-cars-grid";
import { TrendCard } from "@/components/trend-card";
import { getCurrentDashboard } from "@/lib/api";
import { dashboardMock } from "@/lib/mock-data";

export const dynamic = "force-dynamic";

function hasChartData(charts: (typeof dashboardMock)["performance_charts"] | undefined) {
  if (!charts) {
    return false;
  }
  if (charts.race_labels.length === 0) {
    return false;
  }
  return charts.points_series.some((series) => series.values.length > 0);
}

function hasCompletedWeekendResults(
  weekends: (typeof dashboardMock)["completed_weekend_results"] | undefined,
) {
  return Boolean(weekends && weekends.length > 1);
}

export default async function HomePage() {
  const liveDashboard = await getCurrentDashboard();
  const dashboard = {
    ...dashboardMock,
    ...(liveDashboard || {}),
    season: {
      ...dashboardMock.season,
      ...(liveDashboard?.season || {}),
      next_race_sessions:
        liveDashboard?.season?.next_race_sessions && liveDashboard.season.next_race_sessions.length > 0
          ? liveDashboard.season.next_race_sessions
          : dashboardMock.season.next_race_sessions,
    },
    completed_weekend_results: hasCompletedWeekendResults(liveDashboard?.completed_weekend_results)
      ? liveDashboard.completed_weekend_results
      : dashboardMock.completed_weekend_results,
    performance_charts: hasChartData(liveDashboard?.performance_charts)
      ? liveDashboard.performance_charts
      : dashboardMock.performance_charts,
  };
  const seasonProgress = dashboard.season.total_rounds
    ? (dashboard.season.rounds_completed / dashboard.season.total_rounds) * 100
    : 0;

  return (
    <main className="pb-16">
      <SiteHeader />
      <div className="mx-auto flex max-w-7xl flex-col gap-8 px-6 lg:px-10">
        <section className="grid gap-6 lg:grid-cols-[1.35fr_0.85fr]">
          <div className="glow-card rounded-[36px] border border-white/10 bg-black/40 p-8 shadow-panel">
            <div className="data-kicker">{dashboard.hero.eyebrow}</div>
            <div className="mt-8 flex flex-wrap items-end justify-between gap-6">
              <div className="max-w-3xl">
                <h1 className="text-5xl font-semibold tracking-tight text-white md:text-6xl">
                  {dashboard.hero.title}
                </h1>
                <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-300">
                  {dashboard.hero.subtitle}
                </p>
              </div>
              <div className="rounded-[28px] border border-red-500/20 bg-red-500/10 px-5 py-4">
                <div className="text-xs uppercase tracking-[0.24em] text-red-100">Current phase</div>
                <div className="mt-2 text-2xl font-semibold text-white">
                  {dashboard.hero.stage.replace(/_/g, " ")}
                </div>
                <div className="mt-1 text-sm text-red-100">{dashboard.hero.signal_score}</div>
              </div>
            </div>

            <div className="mt-10 grid gap-4 md:grid-cols-3">
              {dashboard.what_changed.map((item) => (
                <div
                  key={item}
                  className="rounded-[24px] border border-white/10 bg-black/35 p-5"
                >
                  <div className="text-xs uppercase tracking-[0.18em] text-slate-500">
                    Changed since {dashboard.weekend.previous_weekend_name}
                  </div>
                  <p className="mt-3 text-sm leading-7 text-slate-200">{item}</p>
                </div>
              ))}
            </div>
          </div>

          <aside className="rounded-[36px] border border-white/10 bg-black/45 p-8 shadow-panel">
            <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Championship leaders</p>
            <div className="mt-8 grid gap-4">
              <div className="rounded-[24px] border border-red-500/20 bg-red-500/10 p-5">
                <div className="text-xs uppercase tracking-[0.18em] text-red-100">Drivers leader</div>
                <div className="mt-3 text-3xl font-semibold text-white">{dashboard.season.leader_driver}</div>
                <div className="mt-2 text-sm text-red-100">{dashboard.driver_standings[0]?.points} pts</div>
              </div>
              <div className="rounded-[24px] border border-white/10 bg-white/5 p-5">
                <div className="text-xs uppercase tracking-[0.18em] text-slate-500">Constructors leader</div>
                <div className="mt-3 text-3xl font-semibold text-white">{dashboard.season.leader_team}</div>
                <div className="mt-2 text-sm text-slate-300">{dashboard.constructor_standings[0]?.points} pts</div>
              </div>
              <div className="rounded-[24px] border border-white/10 bg-white/5 p-5">
                <div className="text-xs uppercase tracking-[0.18em] text-slate-500">Season progress</div>
                <div className="mt-3 flex items-end justify-between gap-4">
                  <div className="text-3xl font-semibold text-white">
                    {dashboard.season.rounds_completed}/{dashboard.season.total_rounds}
                  </div>
                  <div className="text-lg font-semibold text-red-100">{seasonProgress.toFixed(0)}%</div>
                </div>
                <div className="mt-4 h-3 overflow-hidden rounded-full bg-white/10">
                  <div
                    className="h-full rounded-full bg-[linear-gradient(90deg,#E10600_0%,#FF5A36_45%,#FFD166_100%)] shadow-[0_0_24px_rgba(225,6,0,0.35)]"
                    style={{ width: `${seasonProgress}%` }}
                  />
                </div>
                <div className="mt-3 text-sm text-slate-300">
                  rounds completed before {dashboard.season.next_race_name}
                </div>
              </div>
              <SyncButton status={dashboard.sync.status} message={dashboard.sync.message} />
            </div>
          </aside>
        </section>

        <section className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <StandingsTable
            title="Drivers' championship"
            subtitle="Season standings"
            entries={dashboard.driver_standings}
            variant="drivers"
          />
          <StandingsTable
            title="Constructors' championship"
            subtitle="Season standings"
            entries={dashboard.constructor_standings}
            variant="constructors"
          />
        </section>

        <section className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
          <CompletedWeekendResults weekends={dashboard.completed_weekend_results} />
          <NextRacePrediction
            prediction={dashboard.next_race_prediction}
            sessions={dashboard.season.next_race_sessions}
          />
        </section>

        <PerformanceCharts charts={dashboard.performance_charts} driverStandings={dashboard.driver_standings} />

        <TeamCarsGrid teams={dashboard.team_cars} />

        <section className="grid gap-6 xl:grid-cols-[1fr_1fr]">
          <div>
            <div className="mb-5 flex items-center justify-between">
              <h2 className="text-2xl font-semibold text-white">Weekend state</h2>
              <span className="text-xs uppercase tracking-[0.18em] text-slate-500">Phase timeline</span>
            </div>
            <PhaseSwitcher timeline={dashboard.timeline} />
          </div>
          <div>
            <div className="mb-5 flex items-center justify-between">
              <h2 className="text-2xl font-semibold text-white">Signal watch</h2>
              <span className="text-xs uppercase tracking-[0.18em] text-slate-500">Fact and forecast</span>
            </div>
            <div className="grid gap-4">
              {dashboard.top_clusters.map((cluster) => (
                <TrendCard key={cluster.id} cluster={cluster} />
              ))}
            </div>
          </div>
        </section>

        <section className="grid gap-6 xl:grid-cols-2">
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-semibold text-white">Official surfaces</h2>
              <span className="text-xs uppercase tracking-[0.18em] text-slate-500">Calendar and results</span>
            </div>
            {dashboard.sections.official_updates.map((cluster) => (
              <ClusterCard key={cluster.id} cluster={cluster} compact />
            ))}
            {dashboard.sections.race_results.map((cluster) => (
              <ClusterCard key={cluster.id} cluster={cluster} compact />
            ))}
          </div>
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-semibold text-white">Analysis and outlook</h2>
              <span className="text-xs uppercase tracking-[0.18em] text-slate-500">Separated from official signals</span>
            </div>
            {dashboard.sections.analysis.map((cluster) => (
              <ClusterCard key={cluster.id} cluster={cluster} compact />
            ))}
            {dashboard.sections.predictions.map((cluster) => (
              <ClusterCard key={cluster.id} cluster={cluster} compact />
            ))}
          </div>
        </section>

        <SeasonCalendar races={dashboard.calendar} />

        <ArticleFeed items={dashboard.article_feed} />
      </div>
    </main>
  );
}

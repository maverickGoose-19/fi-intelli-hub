import { ChartSeries, DashboardResponse } from "@/lib/types";
import { getTeamColor } from "@/lib/team-colors";

const CHART_HEIGHT = 240;
const CHART_WIDTH = 640;
const PLOT_TOP = 20;
const PLOT_RIGHT = 18;
const PLOT_BOTTOM = 26;
const PLOT_LEFT = 22;
const plotWidth = CHART_WIDTH - PLOT_LEFT - PLOT_RIGHT;
const plotHeight = CHART_HEIGHT - PLOT_TOP - PLOT_BOTTOM;

function formatFastestLap(seconds: number): string {
  if (!seconds) {
    return "-";
  }
  const minutes = Math.floor(seconds / 60);
  const remainder = seconds - minutes * 60;
  return `${minutes}:${remainder.toFixed(3).padStart(6, "0")}`;
}

function formatValue(metric: "points" | "speed" | "fastestLap", value: number): string {
  if (metric === "points") {
    return `${value.toFixed(0)} pts`;
  }
  if (metric === "speed") {
    return `${value.toFixed(0)} km/h`;
  }
  return formatFastestLap(value);
}

function formatAxisValue(metric: "points" | "speed" | "fastestLap", value: number): string {
  if (metric === "points") {
    return `${value.toFixed(0)}`;
  }
  if (metric === "speed") {
    return `${value.toFixed(0)}`;
  }
  return formatFastestLap(value);
}

function formatDelta(metric: "points" | "speed" | "fastestLap", value: number): string {
  if (metric === "fastestLap") {
    return `${value >= 0 ? "+" : "-"}${Math.abs(value).toFixed(3)}s`;
  }
  return `${value >= 0 ? "+" : ""}${formatValue(metric, value)}`;
}

function getAxisLabel(metric: "points" | "speed" | "fastestLap"): string {
  if (metric === "points") {
    return "Points";
  }
  if (metric === "speed") {
    return "Speed km/h";
  }
  return "Lap time";
}

function buildTicks(minValue: number, maxValue: number): number[] {
  if (maxValue <= minValue) {
    return [maxValue, maxValue, maxValue, maxValue, maxValue];
  }
  const step = (maxValue - minValue) / 4;
  return Array.from({ length: 5 }, (_, index) => maxValue - step * index);
}

function getPointX(index: number, count: number): number {
  if (count <= 1) {
    return PLOT_LEFT + plotWidth / 2;
  }
  return PLOT_LEFT + (index / (count - 1)) * plotWidth;
}

function getPointY(value: number, minValue: number, maxValue: number): number {
  const denominator = maxValue - minValue || 1;
  const normalized = (value - minValue) / denominator;
  return PLOT_TOP + plotHeight - normalized * plotHeight;
}

function buildPath(series: ChartSeries, minValue: number, maxValue: number): string {
  if (series.values.length === 0) {
    return "";
  }
  return series.values
    .map((value, index) => {
      const x = getPointX(index, series.values.length);
      const y = getPointY(value, minValue, maxValue);
      return `${index === 0 ? "M" : "L"} ${x} ${y}`;
    })
    .join(" ");
}

function buildAreaPath(series: ChartSeries, minValue: number, maxValue: number): string {
  if (series.values.length === 0) {
    return "";
  }
  const linePath = buildPath(series, minValue, maxValue);
  const lastX = getPointX(series.values.length - 1, series.values.length);
  const firstX = getPointX(0, series.values.length);
  const baseY = PLOT_TOP + plotHeight;
  return `${linePath} L ${lastX} ${baseY} L ${firstX} ${baseY} Z`;
}

function topSeries(series: ChartSeries[]): ChartSeries[] {
  return [...series]
    .sort((left, right) => (right.values[right.values.length - 1] || 0) - (left.values[left.values.length - 1] || 0))
    .slice(0, 5);
}

function ChartPanel({
  title,
  subtitle,
  labels,
  series,
  metric,
  driverTeams,
}: {
  title: string;
  subtitle: string;
  labels: string[];
  series: ChartSeries[];
  metric: "points" | "speed" | "fastestLap";
  driverTeams: Record<string, string>;
}) {
  const trimmedSeries = topSeries(series);
  const allValues = trimmedSeries.flatMap((item) => item.values).filter((value) => value > 0);
  const minValue = allValues.length ? Math.min(...allValues) : 0;
  const maxValue = allValues.length ? Math.max(...allValues) : 1;
  const ticks = buildTicks(minValue, maxValue);

  return (
    <div className="rounded-[32px] border border-white/10 bg-[radial-gradient(circle_at_top_left,rgba(225,6,0,0.18),transparent_35%),linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))] p-6 shadow-panel">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">{subtitle}</p>
          <h3 className="mt-3 text-2xl font-semibold text-white">{title}</h3>
        </div>
        <div className="rounded-full border border-white/10 bg-black/35 px-4 py-2 text-[11px] uppercase tracking-[0.18em] text-slate-300">
          Y-axis: {getAxisLabel(metric)}
        </div>
      </div>

      <div className="mt-6 rounded-[28px] border border-white/10 bg-black/35 p-4 sm:p-5">
        <div className="grid grid-cols-[auto_minmax(0,1fr)] gap-3">
          <div className="flex h-[240px] flex-col justify-between pb-6 pr-1 text-right text-[10px] uppercase tracking-[0.14em] text-slate-500 sm:text-[11px]">
            {ticks.map((tick) => (
              <div key={`${title}-${tick}`}>{formatAxisValue(metric, tick)}</div>
            ))}
          </div>

          <div className="min-w-0">
            <div className="relative overflow-hidden rounded-[22px] border border-white/5 bg-[linear-gradient(180deg,rgba(225,6,0,0.08),rgba(255,255,255,0.02))] px-2 py-3">
              <svg
                className="h-[240px] w-full"
                viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`}
                preserveAspectRatio="none"
              >
                <defs>
                  {trimmedSeries.map((item, index) => (
                    <linearGradient
                      id={`chart-fill-${metric}-${index}`}
                      key={`fill-${item.label}`}
                      x1="0"
                      x2="0"
                      y1="0"
                      y2="1"
                    >
                      <stop
                        offset="0%"
                        stopColor={getTeamColor(driverTeams[item.label])}
                        stopOpacity="0.30"
                      />
                      <stop
                        offset="100%"
                        stopColor={getTeamColor(driverTeams[item.label])}
                        stopOpacity="0.02"
                      />
                    </linearGradient>
                  ))}
                </defs>

                {ticks.map((tick) => {
                  const y = getPointY(tick, minValue, maxValue);
                  return (
                    <g key={`grid-${tick}`}>
                      <line
                        x1={PLOT_LEFT}
                        x2={CHART_WIDTH - PLOT_RIGHT}
                        y1={y}
                        y2={y}
                        stroke="rgba(255,255,255,0.09)"
                        strokeWidth="1"
                        strokeDasharray="4 8"
                      />
                    </g>
                  );
                })}

                {labels.map((_, index) => {
                  const x = getPointX(index, labels.length);
                  return (
                    <line
                      key={`v-grid-${index}`}
                      x1={x}
                      x2={x}
                      y1={PLOT_TOP}
                      y2={PLOT_TOP + plotHeight}
                      stroke="rgba(255,255,255,0.04)"
                      strokeWidth="1"
                    />
                  );
                })}

                {trimmedSeries.map((item, index) => (
                  <path
                    key={`area-${item.label}`}
                    d={buildAreaPath(item, minValue, maxValue)}
                    fill={`url(#chart-fill-${metric}-${index})`}
                  />
                ))}

                {trimmedSeries.map((item, index) => (
                  <path
                    key={item.label}
                    d={buildPath(item, minValue, maxValue)}
                    fill="none"
                    stroke={getTeamColor(driverTeams[item.label])}
                    strokeWidth="3"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    vectorEffect="non-scaling-stroke"
                  />
                ))}

                {trimmedSeries.map((item) =>
                  item.values.map((value, pointIndex) => (
                    <circle
                      key={`${item.label}-${pointIndex}`}
                      cx={getPointX(pointIndex, item.values.length)}
                      cy={getPointY(value, minValue, maxValue)}
                      fill={getTeamColor(driverTeams[item.label])}
                      r="4"
                      stroke="rgba(7,10,17,0.95)"
                      strokeWidth="2"
                    />
                  )),
                )}
              </svg>
            </div>

            <div
              className="mt-3 grid gap-2 text-[10px] uppercase tracking-[0.18em] text-slate-500 sm:text-[11px]"
              style={{ gridTemplateColumns: `repeat(${Math.max(labels.length, 1)}, minmax(0, 1fr))` }}
            >
              {labels.map((label) => (
                <div key={label} className="truncate">
                  {label}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {trimmedSeries.map((item) => {
          const latestValue = item.values[item.values.length - 1] || 0;
          const firstValue = item.values[0] || 0;
          const delta = latestValue - firstValue;
          return (
            <div
              key={`legend-${item.label}`}
              className="rounded-[22px] border border-white/10 bg-white/[0.03] px-4 py-4"
              style={{ boxShadow: `inset 3px 0 0 ${getTeamColor(driverTeams[item.label])}` }}
            >
              <div className="flex items-center gap-3">
                <span
                  className="h-3 w-3 rounded-full"
                  style={{ backgroundColor: getTeamColor(driverTeams[item.label]) }}
                />
                <div>
                  <div className="text-sm font-medium text-white">{item.label}</div>
                  <div className="text-[11px] uppercase tracking-[0.16em] text-slate-500">
                    {driverTeams[item.label] || "Unknown team"}
                  </div>
                </div>
              </div>
              <div className="mt-3 text-xs uppercase tracking-[0.16em] text-slate-500">Latest</div>
              <div className="mt-1 text-lg font-semibold text-white">{formatValue(metric, latestValue)}</div>
              <div className="mt-2 text-xs text-slate-400">
                Delta from first race: {formatDelta(metric, delta)}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export function PerformanceCharts({
  charts,
  driverStandings,
}: {
  charts: DashboardResponse["performance_charts"];
  driverStandings: DashboardResponse["driver_standings"];
}) {
  const driverTeams = Object.fromEntries(driverStandings.map((entry) => [entry.name, entry.team || "Unknown team"]));

  return (
    <section className="grid gap-6">
      <ChartPanel
        title="Top contender points by race"
        subtitle="Championship scoring trend"
        labels={charts.race_labels}
        series={charts.points_series}
        metric="points"
        driverTeams={driverTeams}
      />
      <ChartPanel
        title="Top contender speed trace"
        subtitle="Best speed trap read by completed race"
        labels={charts.race_labels}
        series={charts.speed_series}
        metric="speed"
        driverTeams={driverTeams}
      />
      <ChartPanel
        title="Top contender fastest laps"
        subtitle="Best race lap for each completed round"
        labels={charts.race_labels}
        series={charts.fastest_lap_series}
        metric="fastestLap"
        driverTeams={driverTeams}
      />
    </section>
  );
}

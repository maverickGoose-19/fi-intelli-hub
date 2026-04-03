import Link from "next/link";

const DASHBOARD_VIEWS = [
  { key: "overview", label: "Overview" },
  { key: "standings", label: "Standings" },
  { key: "timings", label: "Timings" },
  { key: "insights", label: "Insights" },
  { key: "schedule", label: "Schedule" },
  { key: "articles", label: "Articles" },
] as const;

export type DashboardView = (typeof DASHBOARD_VIEWS)[number]["key"];

export function MobileDashboardNav({ activeView }: { activeView: DashboardView }) {
  return (
    <div className="sticky top-0 z-20 -mx-4 border-y border-white/10 bg-black/80 px-4 py-4 backdrop-blur sm:-mx-6 sm:px-6 lg:hidden">
      <div className="mb-3 flex flex-col items-start gap-3 sm:flex-row sm:items-center sm:justify-between sm:gap-4">
        <div className="min-w-0">
          <div className="text-xs uppercase tracking-[0.2em] text-slate-500">Mobile navigation</div>
          <div className="mt-1 text-sm font-medium text-white">Jump between dashboard sections</div>
        </div>
        <Link
          href="/predictions"
          className="w-full rounded-full border border-red-500/25 bg-red-500/10 px-4 py-2 text-center text-xs uppercase tracking-[0.18em] text-red-100 sm:w-auto"
        >
          Predictions
        </Link>
      </div>
      <div className="flex gap-2 overflow-x-auto pb-1">
        {DASHBOARD_VIEWS.map((view) => {
          const isActive = view.key === activeView;
          return (
            <Link
              key={view.key}
              href={`/?view=${view.key}`}
              scroll={false}
              className={`shrink-0 rounded-full border px-4 py-2 text-sm transition ${
                isActive
                  ? "border-red-500/30 bg-red-500/15 text-white"
                  : "border-white/10 bg-white/5 text-slate-300 hover:bg-white/10 hover:text-white"
              }`}
            >
              {view.label}
            </Link>
          );
        })}
      </div>
    </div>
  );
}

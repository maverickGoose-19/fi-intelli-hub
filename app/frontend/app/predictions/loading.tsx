import { SiteHeader } from "@/components/site-header";

export default function PredictionsLoading() {
  return (
    <main className="pb-16">
      <SiteHeader />
      <div className="mx-auto flex max-w-7xl flex-col gap-8 px-6 lg:px-10">
        <section className="glow-card rounded-[36px] border border-white/10 bg-black/45 p-8 shadow-panel">
          <div className="data-kicker">Prediction Lab</div>
          <div className="mt-8">
            <h1 className="text-5xl font-semibold tracking-tight text-white md:text-6xl">
              Loading predictions
            </h1>
            <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-300">
              The analytics model is assembling the next-race forecast and feature breakdown.
            </p>
          </div>
          <div className="mt-10 grid gap-4 md:grid-cols-3">
            {Array.from({ length: 3 }).map((_, index) => (
              <div
                key={index}
                className="h-36 animate-pulse rounded-[24px] border border-white/10 bg-white/5"
              />
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}

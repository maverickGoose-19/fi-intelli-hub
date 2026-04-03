import { AdminWorkbench } from "@/components/admin-workbench";
import { SiteHeader } from "@/components/site-header";
import { getClusters } from "@/lib/api";

export default async function AdminPage() {
  const clusters = await getClusters();

  return (
    <main className="pb-16">
      <SiteHeader />
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        <section className="rounded-[36px] border border-white/10 bg-white/[0.045] p-8 shadow-panel">
          <div className="data-kicker">Editorial workbench</div>
          <h1 className="mt-6 text-5xl font-semibold tracking-tight text-white">
            Guardrails stay visible while summaries move fast
          </h1>
          <p className="mt-5 max-w-3xl text-lg leading-8 text-slate-300">
            Inspect cluster summaries, resummarize from the current source set, and keep labels aligned with what is official, what is interpretive, and what remains prediction.
          </p>
        </section>

        <section className="mt-8">
          <AdminWorkbench initialClusters={clusters} />
        </section>
      </div>
    </main>
  );
}


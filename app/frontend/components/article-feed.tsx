import { ArticleFeedItem } from "@/lib/types";

export function ArticleFeed({ items }: { items: ArticleFeedItem[] }) {
  return (
    <section className="rounded-[32px] border border-white/10 bg-black/35 p-6 shadow-panel">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Ingested feed</p>
          <h3 className="mt-3 text-2xl font-semibold text-white">Latest articles and official documents</h3>
        </div>
        <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Most recent first</p>
      </div>

      <div className="mt-6 space-y-3">
        {items.map((item) => (
          <a
            key={item.id}
            className="block rounded-[24px] border border-white/10 bg-white/[0.03] p-5 transition hover:border-red-400/40 hover:bg-white/[0.06]"
            href={item.url}
            rel="noreferrer"
            target="_blank"
          >
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div className="max-w-3xl">
                <div className="text-xs uppercase tracking-[0.18em] text-slate-500">
                  {item.source_name} · {item.source_kind} · {item.kind} · {item.stance}
                </div>
                <h4 className="mt-3 text-lg font-semibold text-white">{item.title}</h4>
              </div>
              <div className="text-xs uppercase tracking-[0.18em] text-slate-500">
                {new Date(item.publish_time).toLocaleString()}
              </div>
            </div>
          </a>
        ))}
      </div>
    </section>
  );
}

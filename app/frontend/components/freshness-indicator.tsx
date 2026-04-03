export function FreshnessIndicator({
  freshness,
  updatedAt,
}: {
  freshness: string;
  updatedAt: string;
}) {
  return (
    <div className="flex items-center gap-3 text-xs text-slate-300">
      <span className="inline-flex items-center rounded-full border border-white/10 bg-white/5 px-2 py-1 uppercase tracking-[0.2em] text-[10px]">
        {freshness}
      </span>
      <span>Updated {new Date(updatedAt).toLocaleString()}</span>
    </div>
  );
}


import Link from "next/link";

export function SiteHeader() {
  return (
    <header className="mx-auto flex w-full max-w-7xl flex-col items-stretch gap-4 px-4 py-6 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:gap-6 lg:px-10 lg:py-8">
      <Link href="/" className="flex min-w-0 items-center gap-3">
        <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-red-500/30 bg-red-500/15 text-sm font-bold tracking-[0.24em] text-red-100">
          FI
        </div>
        <div className="min-w-0">
          <div className="truncate text-[11px] uppercase tracking-[0.24em] text-slate-500 sm:text-xs">
            F1 Intelligence Hub
          </div>
          <div className="truncate text-sm text-white">Race-week signal system</div>
        </div>
      </Link>
      <nav className="flex w-full items-center gap-2 overflow-x-auto rounded-full border border-white/10 bg-black/30 p-1 text-sm text-slate-300 lg:w-auto">
        <Link className="shrink-0 rounded-full px-4 py-2 hover:bg-white/10 hover:text-white" href="/">
          Dashboard
        </Link>
        <Link className="shrink-0 rounded-full px-4 py-2 hover:bg-white/10 hover:text-white" href="/predictions">
          Predictions
        </Link>
        <Link className="shrink-0 rounded-full px-4 py-2 hover:bg-white/10 hover:text-white" href="/admin">
          Editorial
        </Link>
      </nav>
    </header>
  );
}

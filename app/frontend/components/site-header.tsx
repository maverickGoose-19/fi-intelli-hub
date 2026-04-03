import Link from "next/link";

export function SiteHeader() {
  return (
    <header className="mx-auto flex w-full max-w-7xl items-center justify-between gap-6 px-6 py-8 lg:px-10">
      <Link href="/" className="flex items-center gap-3">
        <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-red-500/30 bg-red-500/15 text-sm font-bold tracking-[0.24em] text-red-100">
          FI
        </div>
        <div>
          <div className="text-xs uppercase tracking-[0.24em] text-slate-500">F1 Intelligence Hub</div>
          <div className="text-sm text-white">Race-week signal system</div>
        </div>
      </Link>
      <nav className="flex items-center gap-2 rounded-full border border-white/10 bg-black/30 p-1 text-sm text-slate-300">
        <Link className="rounded-full px-4 py-2 hover:bg-white/10 hover:text-white" href="/">
          Dashboard
        </Link>
        <Link className="rounded-full px-4 py-2 hover:bg-white/10 hover:text-white" href="/predictions">
          Predictions
        </Link>
        <Link className="rounded-full px-4 py-2 hover:bg-white/10 hover:text-white" href="/admin">
          Editorial
        </Link>
      </nav>
    </header>
  );
}

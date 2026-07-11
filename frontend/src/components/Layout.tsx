export function Header({
  onDiscover,
  discovering,
  filter,
  onFilter,
  onProfile,
}: {
  onDiscover: () => void;
  discovering: boolean;
  filter: "foryou" | "all";
  onFilter: (f: "foryou" | "all") => void;
  onProfile: () => void;
}) {
  const tabCls = (active: boolean) =>
    active ? "text-slate-200 cursor-pointer" : "text-muted hover:text-slate-300 cursor-pointer";
  return (
    <header className="border-b border-white/5 bg-ink/80 backdrop-blur sticky top-0 z-10">
      <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🦡</span>
          <span className="font-bold text-lg tracking-tight">
            JobHunter<span className="text-accent">·AI</span>
          </span>
        </div>
        <nav className="flex items-center gap-5 text-sm">
          <span className={tabCls(filter === "foryou")} onClick={() => onFilter("foryou")}>
            For You
          </span>
          <span className={tabCls(filter === "all")} onClick={() => onFilter("all")}>
            All
          </span>
          <span className="text-muted hover:text-slate-300 cursor-pointer" onClick={onProfile}>
            Profile
          </span>
        </nav>
        <button
          onClick={onDiscover}
          disabled={discovering}
          className="bg-accent text-ink font-semibold px-4 py-2 rounded-lg text-sm disabled:opacity-50"
        >
          {discovering ? "Scanning…" : "↻ Agent scan"}
        </button>
      </div>
    </header>
  );
}

export function Hero() {
  return (
    <section className="border-b border-white/5">
      <div className="max-w-5xl mx-auto px-6 py-10 text-center">
        <h1 className="text-3xl md:text-4xl font-bold">
          The agent hunts. <span className="text-accent">You just decide.</span>
        </h1>
        <p className="text-muted mt-3 max-w-xl mx-auto">
          JobHunter·AI monitors freelance markets, scores every lead against your profile,
          and surfaces only the best-fit gigs. Approve in one tap — the agent drafts and applies.
        </p>
      </div>
    </section>
  );
}

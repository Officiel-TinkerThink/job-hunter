export function Header({ onDiscover, discovering }: { onDiscover: () => void; discovering: boolean }) {
  return (
    <header className="border-b border-white/5 bg-ink/80 backdrop-blur sticky top-0 z-10">
      <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🦡</span>
          <span className="font-bold text-lg tracking-tight">JobHunter<span className="text-accent">·AI</span></span>
        </div>
        <nav className="flex items-center gap-5 text-sm text-muted">
          <span className="text-slate-200">For You</span>
          <span>All</span>
          <span>Profile</span>
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

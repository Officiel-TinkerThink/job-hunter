import type { Opportunity } from "../api";

export function scoreColor(score: number | null): string {
  if (score == null) return "text-muted";
  if (score >= 0.7) return "text-good";
  if (score >= 0.4) return "text-warn";
  return "text-bad";
}

export function scoreLabel(score: number | null): string {
  if (score == null) return "—";
  return `${Math.round(score * 100)}%`;
}

export function stateBadge(state: string): string {
  const map: Record<string, string> = {
    proposed: "bg-accent/20 text-accent",
    promising: "bg-accent2/20 text-accent2",
    draft_ready: "bg-indigo-400/20 text-indigo-300",
    applied: "bg-emerald-400/20 text-emerald-300",
    interview: "bg-amber-400/20 text-amber-300",
    test: "bg-rose-400/20 text-rose-300",
    won: "bg-emerald-500/20 text-emerald-300",
    lost: "bg-zinc-400/20 text-zinc-300",
    not_a_fit: "bg-zinc-500/10 text-zinc-400",
    archived: "bg-zinc-500/10 text-zinc-400",
  };
  return map[state] ?? "bg-zinc-400/20 text-zinc-300";
}

export function OpportunityCard({ opp, onClick }: { opp: Opportunity; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="text-left w-full rounded-2xl bg-panel p-5 border border-white/5 hover:border-accent/40 transition hover:shadow-glow"
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="font-semibold text-lg leading-tight">{opp.title}</h3>
          <p className="text-muted text-sm mt-0.5">{opp.client || opp.source}</p>
        </div>
        <div className="text-right shrink-0">
          <div className={`text-2xl font-bold ${scoreColor(opp.score)}`}>{scoreLabel(opp.score)}</div>
          <div className="text-[11px] text-muted">match</div>
        </div>
      </div>
      <p className="text-sm text-slate-300/80 mt-3 line-clamp-2">{opp.summary || "No description."}</p>
      <div className="flex flex-wrap gap-2 mt-3 items-center">
        <span className={`text-xs px-2 py-0.5 rounded-full ${stateBadge(opp.state)}`}>{opp.state}</span>
        {opp.budget && <span className="text-xs text-good">💰 {opp.budget}</span>}
        {opp.tags.slice(0, 4).map((t) => (
          <span key={t} className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-slate-300">{t}</span>
        ))}
      </div>
    </button>
  );
}

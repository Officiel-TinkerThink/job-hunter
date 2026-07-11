import type { Timeline } from "../api";

const ICONS: Record<string, string> = {
  discovered: "🔎",
  scored: "🧮",
  proposed: "📋",
  draft_ready: "✍️",
  applied: "🚀",
  reply: "💬",
  escalated: "🔔",
  closed: "🏁",
};

export function TimelineView({ timeline }: { timeline: Timeline }) {
  return (
    <ol className="relative border-l border-white/10 ml-2 space-y-5">
      {timeline.events.length === 0 && (
        <li className="text-muted text-sm">No events yet.</li>
      )}
      {timeline.events.map((e, i) => (
        <li key={i} className="ml-4">
          <div className="absolute -left-2 w-4 h-4 rounded-full bg-accent/80 ring-4 ring-ink" />
          <div className="flex items-center gap-2">
            <span>{ICONS[e.kind] ?? "•"}</span>
            <span className="text-xs uppercase tracking-wide text-muted">{e.kind}</span>
            <span className="text-xs text-muted">{new Date(e.at).toLocaleString()}</span>
          </div>
          <p className="text-sm text-slate-200 mt-1">{e.message}</p>
          {e.payload && Object.keys(e.payload).length > 0 && (
            <pre className="text-[11px] text-muted mt-1 bg-black/30 rounded p-2 overflow-auto">
              {JSON.stringify(e.payload, null, 2)}
            </pre>
          )}
        </li>
      ))}
    </ol>
  );
}

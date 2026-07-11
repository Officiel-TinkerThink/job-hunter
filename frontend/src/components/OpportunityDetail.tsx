import { useEffect, useState } from "react";
import api, { type Opportunity, type Timeline } from "../api";
import { TimelineView } from "./TimelineView";
import { scoreColor, scoreLabel } from "./OpportunityCard";

export function OpportunityDetail({
  opp,
  onBack,
  onChanged,
}: {
  opp: Opportunity;
  onBack: () => void;
  onChanged: () => void;
}) {
  const [timeline, setTimeline] = useState<Timeline | null>(null);
  const [preview, setPreview] = useState<string>("");
  const [busy, setBusy] = useState(false);
  const [copied, setCopied] = useState(false);
  const [applyResult, setApplyResult] = useState<{ dry_run: boolean; to: string | null } | null>(null);

  useEffect(() => {
    setApplyResult(null);
  }, [opp.id]);

  useEffect(() => {
    api.timeline(opp.id).then(setTimeline);
    if (!opp.proposal) api.previewProposal(opp.id).then(setPreview);
    else setPreview(opp.proposal);
  }, [opp.id, opp.proposal]);

  async function act(fn: () => Promise<void>) {
    setBusy(true);
    await fn();
    setBusy(false);
    onChanged();
    onBack();
  }

  async function doApply() {
    setBusy(true);
    try {
      const r = await api.apply(opp.id);
      setApplyResult({ dry_run: r.dry_run, to: r.to });
    } finally {
      setBusy(false);
      onChanged();
    }
  }

  async function copy() {
    const text = opp.proposal || preview;
    if (!text) return;
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* clipboard may be blocked; ignore */
    }
  }

  return (
    <div className="max-w-3xl mx-auto">
      <button onClick={onBack} className="text-accent text-sm mb-4">← Back</button>

      <div className="rounded-2xl bg-panel p-6 border border-white/5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold">{opp.title}</h2>
            <p className="text-muted">{opp.client || opp.source}</p>
          </div>
          <div className={`text-3xl font-bold ${scoreColor(opp.score)}`}>{scoreLabel(opp.score)}</div>
        </div>

        <div className="flex flex-wrap gap-2 mt-3 items-center">
          {opp.budget && <span className="text-sm text-good">💰 {opp.budget}</span>}
          {opp.tags.map((t) => (
            <span key={t} className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-slate-300">{t}</span>
          ))}
        </div>

        <p className="text-slate-200 mt-4">{opp.summary || "No description."}</p>

        <a href={opp.url} target="_blank" rel="noreferrer" className="text-accent text-sm mt-3 inline-block">
          Open on {opp.source} ↗
        </a>

        <div className="flex gap-3 mt-6">
          <button
            disabled={busy}
            onClick={() => act(() => api.approve(opp.id))}
            className="bg-good text-ink font-semibold px-4 py-2 rounded-lg disabled:opacity-50"
          >
            ✅ Approve & let agent draft
          </button>
          <button
            disabled={busy}
            onClick={() => act(() => api.pass(opp.id))}
            className="bg-white/5 text-slate-200 px-4 py-2 rounded-lg disabled:opacity-50"
          >
            ✕ Pass
          </button>
          <button
            onClick={copy}
            className="bg-white/5 text-slate-200 px-4 py-2 rounded-lg"
          >
            {copied ? "✓ Copied" : "⧉ Copy pitch"}
          </button>
          {(opp.state === "draft_ready" || opp.state === "applied") && (
            <button
              disabled={busy || opp.state === "applied"}
              onClick={doApply}
              className="bg-accent text-ink font-semibold px-4 py-2 rounded-lg disabled:opacity-50"
            >
              {opp.state === "applied" ? "✓ Applied" : "📧 Apply via email"}
            </button>
          )}
        </div>
        {applyResult && (
          <p className="text-xs mt-2 text-muted">
            {applyResult.dry_run
              ? "Dry-run: email composed but not sent (set SMTP_* env to send for real)."
              : `Sent via email to ${applyResult.to}.`}
          </p>
        )}
      </div>

      {preview && (
        <div className="rounded-2xl bg-panel2 p-6 border border-white/5 mt-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold">Agent's draft proposal</h3>
            <span className="text-[11px] text-muted">{opp.proposal ? "saved" : "preview"}</span>
          </div>
          <pre className="whitespace-pre-wrap text-sm text-slate-200 bg-black/30 rounded p-3">{preview}</pre>
        </div>
      )}

      <div className="rounded-2xl bg-panel p-6 border border-white/5 mt-4">
        <h3 className="font-semibold mb-4">Progress timeline</h3>
        {timeline && <TimelineView timeline={timeline} />}
      </div>
    </div>
  );
}

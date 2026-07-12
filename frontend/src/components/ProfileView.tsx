import { useEffect, useState } from "react";
import api, { type Profile } from "../api";

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="text-xs uppercase tracking-wide text-muted">{label}</span>
      <div className="mt-1">{children}</div>
    </label>
  );
}

const inputCls =
  "w-full bg-panel border border-white/10 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-accent";

export function ProfileView({ onSaved }: { onSaved: () => void }) {
  const [p, setP] = useState<Profile | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [saveError, setSaveError] = useState(false);

  useEffect(() => {
    api.getProfile().then(setP);
  }, []);

  if (!p) return <p className="text-muted">Loading profile…</p>;

  function set<K extends keyof Profile>(k: K, v: Profile[K]) {
    setP({ ...p!, [k]: v });
    setSaved(false);
    setSaveError(false);
  }
  const list = (v: string | string[]) =>
    (Array.isArray(v) ? v : String(v).split(",")).map((x) => x.trim()).filter(Boolean);

  async function save() {
    setSaving(true);
    try {
      await api.saveProfile({
        ...p!,
        skills: list(p!.skills),
        avoid_niches: list(p!.avoid_niches),
      });
      setSaved(true);
      onSaved();
    } catch (err) {
      console.error("profile save failed", err);
      setSaved(false);
      setSaveError(true);
    } finally {
      setSaving(false);
    }
  }

  const skillsStr = Array.isArray(p.skills) ? p.skills.join(", ") : "";
  const avoidStr = Array.isArray(p.avoid_niches) ? p.avoid_niches.join(", ") : "";

  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold mb-1">Your profile</h2>
      <p className="text-muted text-sm mb-6">
        The agent scores every gig against this. Be specific — the better it knows you, the
        sharper its recommendations.
      </p>

      <div className="grid gap-4">
        <Field label="Full name">
          <input className={inputCls} value={p.full_name} onChange={(e) => set("full_name", e.target.value)} />
        </Field>
        <Field label="Headline">
          <input className={inputCls} value={p.headline} onChange={(e) => set("headline", e.target.value)} />
        </Field>
        <Field label="Skills (comma separated)">
          <input
            className={inputCls}
            value={skillsStr}
            onChange={(e) => set("skills", e.target.value as unknown as string[])}
          />
        </Field>
        <Field label="Summary">
          <textarea className={inputCls} rows={3} value={p.summary} onChange={(e) => set("summary", e.target.value)} />
        </Field>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Min hourly rate (USD)">
            <input
              type="number"
              className={inputCls}
              value={p.min_hourly_rate ?? ""}
              onChange={(e) => set("min_hourly_rate", e.target.value ? Number(e.target.value) : null)}
            />
          </Field>
          <Field label="Timezone">
            <input className={inputCls} value={p.timezone} onChange={(e) => set("timezone", e.target.value)} />
          </Field>
        </div>
        <Field label="Avoid niches (comma separated)">
          <input
            className={inputCls}
            value={avoidStr}
            onChange={(e) => set("avoid_niches", e.target.value as unknown as string[])}
          />
        </Field>
        <Field label="Portfolio URL">
          <input className={inputCls} value={p.portfolio_url} onChange={(e) => set("portfolio_url", e.target.value)} />
        </Field>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={p.remote_only}
            onChange={(e) => set("remote_only", e.target.checked)}
          />
          Remote-only
        </label>
      </div>

      <div className="flex items-center gap-3 mt-6">
        <button
          onClick={save}
          disabled={saving}
          className="bg-accent text-ink font-semibold px-5 py-2 rounded-lg text-sm disabled:opacity-50"
        >
          {saving ? "Saving…" : "Save profile"}
        </button>
        {saved && <span className="text-sm text-good">✓ Saved</span>}
        {saveError && <span className="text-sm text-red-400">✕ Save failed — check connection</span>}
      </div>
    </div>
  );
}

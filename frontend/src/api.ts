export interface Opportunity {
  id: number;
  source: string;
  title: string;
  url: string;
  client: string;
  summary: string;
  budget: string | null;
  tags: string[];
  state: string;
  score: number | null;
  score_reasons: string[];
  proposal: string;
  created_at: string;
}

export interface TimelineEvent {
  kind: string;
  message: string;
  at: string;
  payload: Record<string, unknown>;
}

export interface Timeline {
  opportunity: Opportunity;
  events: TimelineEvent[];
}

export interface Profile {
  full_name: string;
  headline: string;
  skills: string[];
  experience_years: number;
  summary: string;
  portfolio_url: string;
  min_hourly_rate: number | null;
  min_fixed_budget: number | null;
  remote_only: boolean;
  avoid_niches: string[];
  timezone: string;
  upwork_profile_url: string;
  fiverr_gig_urls: string[];
}

const api = {
  async getProfile(): Promise<Profile> {
    const r = await fetch("/api/profile");
    return r.json();
  },
  async saveProfile(p: Profile): Promise<void> {
    await fetch("/api/profile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(p),
    });
  },
  async discover(): Promise<{ found: number; new: number; proposed: number }> {
    const r = await fetch("/api/discover", { method: "POST" });
    return r.json();
  },
  async listOpportunities(states?: string): Promise<Opportunity[]> {
    const url = states ? `/api/opportunities?states=${states}` : "/api/opportunities";
    const r = await fetch(url);
    return r.json();
  },
  async timeline(id: number): Promise<Timeline> {
    const r = await fetch(`/api/opportunities/${id}/timeline`);
    return r.json();
  },
  async previewProposal(id: number): Promise<string> {
    const r = await fetch(`/api/opportunities/${id}/preview-proposal`, { method: "POST" });
    const j = await r.json();
    return j.proposal ?? "";
  },
  async approve(id: number): Promise<void> {
    await fetch(`/api/opportunities/${id}/approve`, { method: "POST" });
  },
  async apply(id: number): Promise<{ ok: boolean; dry_run: boolean; to: string | null; subject: string }> {
    const r = await fetch(`/api/opportunities/${id}/apply`, { method: "POST" });
    return r.json();
  },
  async pass(id: number): Promise<void> {
    await fetch(`/api/opportunities/${id}/pass`, { method: "POST" });
  },
};

export default api;

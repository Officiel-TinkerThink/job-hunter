import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import api, { type Opportunity } from "./api";
import { Header, Hero } from "./components/Layout";
import { OpportunityCard } from "./components/OpportunityCard";
import { OpportunityDetail } from "./components/OpportunityDetail";
import { ProfileView } from "./components/ProfileView";

type View = "board" | "detail" | "profile";

const FORYOU_STATES = ["proposed", "promising", "draft_ready", "applied", "interview", "test"];

export default function App() {
  const [opps, setOpps] = useState<Opportunity[]>([]);
  const [filter, setFilter] = useState<"foryou" | "all">("foryou");
  const [selected, setSelected] = useState<Opportunity | null>(null);
  const [view, setView] = useState<View>("board");
  const [discovering, setDiscovering] = useState(false);

  async function load() {
    const data = await api.listOpportunities();
    setOpps(data);
  }

  useEffect(() => {
    load();
  }, []);

  const foryou = useMemo(
    () => opps.filter((o) => FORYOU_STATES.includes(o.state)),
    [opps]
  );
  const shown = filter === "foryou" ? foryou : opps;
  const sorted = useMemo(
    () => [...shown].sort((a, b) => (b.score ?? 0) - (a.score ?? 0)),
    [shown]
  );

  async function doDiscover() {
    setDiscovering(true);
    await api.discover();
    await load();
    setDiscovering(false);
  }

  // Header For You / All must also return to the board (not just change filter),
  // otherwise clicking them from Profile/Detail leaves you stranded on that view.
  function goFilter(f: "foryou" | "all") {
    setFilter(f);
    setSelected(null);
    setView("board");
  }

  if (view === "detail" && selected) {
    return (
      <div>
        <Header onDiscover={doDiscover} discovering={discovering} filter={filter} onFilter={goFilter} onProfile={() => { setView("profile"); setSelected(null); }} />
        <div className="p-6">
          <OpportunityDetail
            opp={selected}
            onBack={() => { setView("board"); setSelected(null); }}
            onChanged={load}
          />
        </div>
      </div>
    );
  }

  if (view === "profile") {
    return (
      <div>
        <Header onDiscover={doDiscover} discovering={discovering} filter={filter} onFilter={goFilter} onProfile={() => setView("profile")} />
        <main className="max-w-5xl mx-auto px-6 py-8">
          <ProfileView onSaved={load} />
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-full">
      <Header onDiscover={doDiscover} discovering={discovering} filter={filter} onFilter={goFilter} onProfile={() => setView("profile")} />
      <Hero />
      <main className="max-w-5xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-5">
          <div className="inline-flex bg-panel rounded-lg p-1 text-sm">
            <button
              onClick={() => setFilter("foryou")}
              className={`px-4 py-1.5 rounded-md ${filter === "foryou" ? "bg-accent text-ink font-semibold" : "text-muted"}`}
            >
              For You ({foryou.length})
            </button>
            <button
              onClick={() => setFilter("all")}
              className={`px-4 py-1.5 rounded-md ${filter === "all" ? "bg-accent text-ink font-semibold" : "text-muted"}`}
            >
              All ({opps.length})
            </button>
          </div>
          {foryou.length > 0 && (
            <span className="text-sm text-muted">
              {foryou.length} recommended by the agent
            </span>
          )}
        </div>

        {sorted.length === 0 ? (
          <div className="text-center text-muted py-20">
            <p className="text-lg">No opportunities yet.</p>
            <p className="text-sm mt-2">Hit “Agent scan” to let the agent hunt for you.</p>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {sorted.map((o, i) => (
              <motion.div
                key={o.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.03 }}
              >
                <OpportunityCard opp={o} onClick={() => { setSelected(o); setView("detail"); }} />
              </motion.div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

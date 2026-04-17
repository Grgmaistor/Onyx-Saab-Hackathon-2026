"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/mil/Header";
import { Panel } from "@/components/mil/Panel";
import {
  listAttackPlans, generateRandomPlans, generateAIPlan, deleteAttackPlan,
  type AttackPlan,
} from "@/lib/api";

export default function PlansPage() {
  const [plans, setPlans] = useState<AttackPlan[]>([]);
  const [filter, setFilter] = useState<string>("all");
  const [selected, setSelected] = useState<AttackPlan | null>(null);
  const [randomCount, setRandomCount] = useState(10);
  const [randomSeed, setRandomSeed] = useState(100);
  const [aiPrompt, setAiPrompt] = useState("Generate a multi-wave attack focused on destroying the capital Arktholm. Use bombers from firewatch_station at tick 1, then drone swarms at tick 30 as a feint on Nordvik.");
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = () => {
    listAttackPlans().then((d) => setPlans(d.plans)).catch((e) => setError(String(e)));
  };

  useEffect(() => { refresh(); }, []);

  const handleRandom = async () => {
    setLoading("random");
    setError(null);
    try {
      await generateRandomPlans(randomCount, randomSeed);
      refresh();
    } catch (e) { setError(String(e)); }
    finally { setLoading(null); }
  };

  const handleAI = async () => {
    setLoading("ai");
    setError(null);
    try {
      const plan = await generateAIPlan(aiPrompt);
      refresh();
      setSelected(plan);
    } catch (e) { setError(String(e)); }
    finally { setLoading(null); }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this attack plan?")) return;
    try {
      await deleteAttackPlan(id);
      if (selected?.id === id) setSelected(null);
      refresh();
    } catch (e) { setError(String(e)); }
  };

  const filtered = filter === "all" ? plans : plans.filter((p) => p.source === filter);

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 p-6 max-w-[1600px] mx-auto w-full">
        <div className="mb-6 flex justify-between items-end">
          <div>
            <h1 className="mil-heading text-2xl mb-1">⌧ ATTACK PLAN LIBRARY</h1>
            <p className="text-dim text-sm tracking-wider">DOCTRINE REPOSITORY // THREAT MODELING</p>
          </div>
          <div className="flex gap-2">
            <span className="mil-badge mil-badge-dim">{plans.length} TOTAL</span>
          </div>
        </div>

        {error && (
          <div className="mil-panel mb-4 p-3 border-red-900/50">
            <span className="text-danger text-xs">⚠ {error}</span>
          </div>
        )}

        <div className="grid grid-cols-2 gap-4 mb-4">
          <Panel title="⚙ RANDOM GENERATOR">
            <div className="space-y-3">
              <p className="text-xs text-dim">
                Generate N random attack plans with varied waves, targets, and compositions.
                Use for broad-coverage robustness testing.
              </p>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <div className="mil-label mb-1">Count</div>
                  <input type="number" value={randomCount}
                    onChange={(e) => setRandomCount(Number(e.target.value))}
                    min={1} max={500} className="mil-input" />
                </div>
                <div>
                  <div className="mil-label mb-1">Base Seed</div>
                  <input type="number" value={randomSeed}
                    onChange={(e) => setRandomSeed(Number(e.target.value))}
                    className="mil-input" />
                </div>
              </div>
              <button onClick={handleRandom} disabled={loading !== null} className="mil-btn mil-btn-primary w-full">
                {loading === "random" ? "◌ GENERATING..." : `⚙ GENERATE ${randomCount} RANDOM PLANS`}
              </button>
            </div>
          </Panel>

          <Panel title="◈ AI GENERATOR (CLAUDE)">
            <div className="space-y-3">
              <p className="text-xs text-dim">
                Describe desired attack characteristics in natural language.
                Claude generates an attack plan matching your intent.
              </p>
              <div>
                <div className="mil-label mb-1">Prompt</div>
                <textarea
                  value={aiPrompt}
                  onChange={(e) => setAiPrompt(e.target.value)}
                  className="mil-textarea"
                  rows={4}
                  placeholder="Describe the attack strategy you want..."
                />
              </div>
              <button onClick={handleAI} disabled={loading !== null || !aiPrompt.trim()} className="mil-btn mil-btn-primary w-full">
                {loading === "ai" ? "◌ CONSULTING AI..." : "◈ GENERATE VIA CLAUDE"}
              </button>
              <p className="text-[10px] text-warn">
                Requires ANTHROPIC_API_KEY in backend environment.
              </p>
            </div>
          </Panel>
        </div>

        <div className="grid grid-cols-[1fr_400px] gap-4">
          <Panel
            title="STORED PLANS"
            actions={
              <span className="flex gap-1">
                {["all", "custom", "random", "ai_generated"].map((f) => (
                  <button key={f} onClick={() => setFilter(f)}
                    className={`mil-btn mil-btn-sm ${filter === f ? "mil-btn-primary" : ""}`}>
                    {f.toUpperCase()}
                  </button>
                ))}
              </span>
            }
          >
            <div className="max-h-[600px] overflow-y-auto">
              <table className="mil-table">
                <thead>
                  <tr>
                    <th>NAME</th>
                    <th style={{ width: 90 }}>SOURCE</th>
                    <th style={{ width: 70 }}>ACTIONS</th>
                    <th>TAGS</th>
                    <th style={{ width: 60 }}></th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((p) => (
                    <tr key={p.id} onClick={() => setSelected(p)} style={{ cursor: "pointer",
                        background: selected?.id === p.id ? "var(--surface-2)" : undefined }}>
                      <td>
                        <div className="mil-value text-xs">{p.name}</div>
                        <div className="text-[10px] text-dim">{p.id}</div>
                      </td>
                      <td>
                        <span className={`mil-badge ${
                          p.source === "random" ? "mil-badge-dim" :
                          p.source === "ai_generated" ? "mil-badge-running" :
                          "mil-badge-win"
                        }`}>
                          {p.source.substring(0, 4).toUpperCase()}
                        </span>
                      </td>
                      <td className="font-mono">{p.actions.length}</td>
                      <td>
                        <div className="flex gap-1 flex-wrap">
                          {p.tags.slice(0, 3).map((t, i) => (
                            <span key={i} className="text-[9px] text-dim">{t}</span>
                          ))}
                        </div>
                      </td>
                      <td>
                        <button onClick={(e) => { e.stopPropagation(); handleDelete(p.id); }}
                          className="mil-btn mil-btn-sm mil-btn-danger">
                          DEL
                        </button>
                      </td>
                    </tr>
                  ))}
                  {filtered.length === 0 && (
                    <tr><td colSpan={5} className="text-center text-dim py-6">[ EMPTY ]</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </Panel>

          <Panel title="PLAN DETAIL">
            {selected ? (
              <div className="space-y-3">
                <div>
                  <div className="mil-label">Name</div>
                  <div className="mil-value text-sm">{selected.name}</div>
                </div>
                <div>
                  <div className="mil-label">Description</div>
                  <div className="text-xs">{selected.description}</div>
                </div>
                <div>
                  <div className="mil-label">Plan ID</div>
                  <div className="font-mono text-[10px] text-dim">{selected.id}</div>
                </div>
                <hr className="mil-divider" />
                <div>
                  <div className="mil-label mb-2">ACTION SEQUENCE ({selected.actions.length})</div>
                  <div className="space-y-1 max-h-[400px] overflow-y-auto">
                    {selected.actions.map((a, i) => (
                      <div key={i} className="mil-panel p-2 text-[11px]">
                        <div className="flex justify-between">
                          <span className="text-accent font-bold">T+{String(a.tick).padStart(4, "0")}</span>
                          <span className="mil-badge mil-badge-dim">{a.type}</span>
                        </div>
                        <div className="text-dim mt-1">
                          {a.count}× {a.aircraft_type}
                          {a.from_base && <> from <span className="text-accent">{a.from_base}</span></>}
                          {a.target && (
                            <> → <span className="text-warn">
                              {a.target.id || `(${a.target.x_km}, ${a.target.y_km})`}
                            </span></>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-dim text-xs">Select a plan from the list to view details.</p>
            )}
          </Panel>
        </div>
      </main>
    </div>
  );
}

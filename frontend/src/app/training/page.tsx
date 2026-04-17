"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/mil/Header";
import { Panel, MetricRow } from "@/components/mil/Panel";
import {
  listAttackPlans, runTraining, getStrategies,
  type AttackPlan, type TrainingResponse, type Strategy,
} from "@/lib/api";

export default function TrainingPage() {
  const [plans, setPlans] = useState<AttackPlan[]>([]);
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [strategyId, setStrategyId] = useState("defensive_v1");
  const [seedsPerPlan, setSeedsPerPlan] = useState(5);
  const [filter, setFilter] = useState<string>("all");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<TrainingResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listAttackPlans().then((d) => setPlans(d.plans)).catch((e) => setError(String(e)));
    getStrategies().then((d) => setStrategies(d.strategies)).catch(() => {});
  }, []);

  const filteredPlans = filter === "all" ? plans : plans.filter((p) => p.source === filter);

  const toggleAll = () => {
    if (selected.size === filteredPlans.length) {
      setSelected(new Set());
    } else {
      setSelected(new Set(filteredPlans.map((p) => p.id)));
    }
  };

  const toggleOne = (id: string) => {
    const next = new Set(selected);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setSelected(next);
  };

  const handleRun = async () => {
    if (selected.size === 0) return;
    setLoading(true);
    setError(null);
    try {
      const res = await runTraining({
        attack_plan_ids: Array.from(selected),
        strategy_id: strategyId,
        seeds_per_plan: seedsPerPlan,
      });
      setResult(res);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 p-6 max-w-[1600px] mx-auto w-full">
        <div className="mb-6">
          <h1 className="mil-heading text-2xl mb-1">⚡ TRAINING MODE</h1>
          <p className="text-dim text-sm tracking-wider">MULTI-THREAT STRESS TEST // BATCH ANALYSIS</p>
        </div>

        {error && (
          <div className="mil-panel mb-4 p-3 border-red-900/50">
            <span className="text-danger text-xs">⚠ {error}</span>
          </div>
        )}

        <div className="grid grid-cols-[320px_1fr] gap-4">
          {/* LEFT - Config */}
          <div className="space-y-4">
            <Panel title="TRAINING CONFIG">
              <div className="space-y-3">
                <div>
                  <div className="mil-label mb-1">Defense Strategy</div>
                  <select value={strategyId} onChange={(e) => setStrategyId(e.target.value)} className="mil-select">
                    {strategies.map((s) => (
                      <option key={s.id} value={s.id}>{s.name}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <div className="mil-label mb-1">Seeds per Plan</div>
                  <input
                    type="number" value={seedsPerPlan}
                    onChange={(e) => setSeedsPerPlan(Number(e.target.value))}
                    min={1} max={50} className="mil-input"
                  />
                  <p className="text-[10px] text-dim mt-1">
                    Each plan runs {seedsPerPlan}× with different seeds for statistical confidence.
                  </p>
                </div>

                <hr className="mil-divider" />

                <div className="text-xs">
                  <div className="flex justify-between mb-1">
                    <span className="mil-metric-label">Plans Selected</span>
                    <span className="mil-value-accent">{selected.size}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="mil-metric-label">Total Simulations</span>
                    <span className="mil-value-accent">{selected.size * seedsPerPlan}</span>
                  </div>
                </div>

                <button
                  onClick={handleRun}
                  disabled={loading || selected.size === 0}
                  className="mil-btn mil-btn-primary w-full"
                >
                  {loading ? "◌ RUNNING BATCH..." : "⚡ INITIATE TRAINING"}
                </button>
              </div>
            </Panel>

            {result && (
              <Panel title="TRAINING RESULT" badge={result.batch_id}>
                <div className="mb-3">
                  <div className="text-3xl mil-value-accent font-bold">
                    {(result.overall_defense_rate * 100).toFixed(1)}%
                  </div>
                  <div className="text-dim text-xs tracking-wider">OVERALL DEFENSE RATE</div>
                </div>
                <MetricRow label="Total Simulations" value={result.total_simulations} />
                <MetricRow label="Total Wins" value={result.total_wins} />
                <MetricRow label="Plans Tested" value={result.by_attack_plan.length} />
              </Panel>
            )}
          </div>

          {/* RIGHT - Plan selector / results */}
          <div className="space-y-4">
            <Panel title="ATTACK PLAN SELECTION"
              actions={
                <span className="flex gap-2">
                  <button onClick={() => setFilter("all")}
                    className={`mil-btn mil-btn-sm ${filter === "all" ? "mil-btn-primary" : ""}`}>
                    ALL ({plans.length})
                  </button>
                  <button onClick={() => setFilter("random")}
                    className={`mil-btn mil-btn-sm ${filter === "random" ? "mil-btn-primary" : ""}`}>
                    RANDOM
                  </button>
                  <button onClick={() => setFilter("ai_generated")}
                    className={`mil-btn mil-btn-sm ${filter === "ai_generated" ? "mil-btn-primary" : ""}`}>
                    AI
                  </button>
                  <button onClick={() => setFilter("custom")}
                    className={`mil-btn mil-btn-sm ${filter === "custom" ? "mil-btn-primary" : ""}`}>
                    CUSTOM
                  </button>
                </span>
              }
            >
              <div className="max-h-[400px] overflow-y-auto">
                <table className="mil-table">
                  <thead>
                    <tr>
                      <th style={{ width: 40 }}>
                        <input type="checkbox"
                          checked={filteredPlans.length > 0 && selected.size === filteredPlans.length}
                          onChange={toggleAll}
                          className="accent-green-400"
                        />
                      </th>
                      <th>NAME</th>
                      <th style={{ width: 90 }}>SOURCE</th>
                      <th style={{ width: 70 }}>ACTIONS</th>
                      <th>TAGS</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredPlans.map((p) => (
                      <tr key={p.id} onClick={() => toggleOne(p.id)} style={{ cursor: "pointer" }}>
                        <td>
                          <input type="checkbox" checked={selected.has(p.id)} onChange={() => {}} className="accent-green-400" />
                        </td>
                        <td>
                          <div className="mil-value text-xs">{p.name}</div>
                          <div className="text-[10px] text-dim">{p.description.substring(0, 60)}</div>
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
                            {p.tags.slice(0, 2).map((t, i) => (
                              <span key={i} className="text-[9px] text-dim">{t}</span>
                            ))}
                          </div>
                        </td>
                      </tr>
                    ))}
                    {filteredPlans.length === 0 && (
                      <tr><td colSpan={5} className="text-center text-dim py-6">[ NO PLANS MATCHING FILTER ]</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            </Panel>

            {result && (
              <Panel title="PER-PLAN RESULTS">
                <table className="mil-table">
                  <thead>
                    <tr>
                      <th>PLAN ID</th>
                      <th>SIMS</th>
                      <th>WINS</th>
                      <th>LOSSES</th>
                      <th>TIMEOUTS</th>
                      <th>SUCCESS</th>
                      <th>AVG CAS</th>
                      <th>AVG LOST</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.by_attack_plan.map((r) => (
                      <tr key={r.attack_plan_id}>
                        <td className="font-mono text-[10px]">{r.attack_plan_id}</td>
                        <td>{r.simulations}</td>
                        <td className="text-accent">{r.wins}</td>
                        <td className="text-danger">{r.losses}</td>
                        <td className="text-warn">{r.timeouts}</td>
                        <td className="mil-value-accent">{(r.defense_success_rate * 100).toFixed(0)}%</td>
                        <td>{r.avg_casualties.toFixed(0)}</td>
                        <td>{r.avg_aircraft_lost.toFixed(1)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </Panel>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

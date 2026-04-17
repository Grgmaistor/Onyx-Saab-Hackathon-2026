"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Header } from "@/components/mil/Header";
import { Panel, MetricRow } from "@/components/mil/Panel";
import { getAttackPlanSummary, getStrategies, getScenarios, type AttackPlanSummary, type Strategy, type Scenario } from "@/lib/api";

export default function Home() {
  const [summary, setSummary] = useState<AttackPlanSummary | null>(null);
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      getAttackPlanSummary(),
      getStrategies(),
      getScenarios(),
    ]).then(([s, st, sc]) => {
      setSummary(s);
      setStrategies(st.strategies);
      setScenarios(sc.scenarios);
    }).catch((e) => setError(String(e)));
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 p-6 max-w-7xl mx-auto w-full">
        <div className="mb-6">
          <h1 className="mil-heading text-2xl mb-1">COMMAND OVERVIEW</h1>
          <p className="text-dim text-sm tracking-wider">SYSTEM STATUS // MISSION READINESS</p>
        </div>

        {error && (
          <div className="mil-panel mb-4 p-3 border-red-900/50">
            <span className="text-danger text-xs">⚠ CONN ERROR: {error}</span>
          </div>
        )}

        <div className="grid grid-cols-3 gap-4 mb-6">
          <Panel title="DOCTRINE LIBRARY">
            <div className="text-4xl mil-value-accent font-bold mb-2">
              {summary?.total ?? 0}
            </div>
            <div className="text-dim text-xs tracking-wider mb-3">ATTACK PLANS STORED</div>
            <MetricRow label="Custom" value={summary?.by_source?.custom ?? 0} />
            <MetricRow label="Random" value={summary?.by_source?.random ?? 0} />
            <MetricRow label="AI Generated" value={summary?.by_source?.ai_generated ?? 0} />
          </Panel>

          <Panel title="DEFENSE STRATEGIES">
            <div className="text-4xl mil-value-accent font-bold mb-2">
              {strategies.length}
            </div>
            <div className="text-dim text-xs tracking-wider mb-3">ACTIVE PROFILES</div>
            {strategies.map((s) => (
              <div key={s.id} className="mil-metric">
                <span className="mil-metric-label">{s.name}</span>
                <span className="mil-badge mil-badge-dim">ACTIVE</span>
              </div>
            ))}
          </Panel>

          <Panel title="SCENARIOS">
            <div className="text-4xl mil-value-accent font-bold mb-2">
              {scenarios.length}
            </div>
            <div className="text-dim text-xs tracking-wider mb-3">THEATER CONFIGURATIONS</div>
            {scenarios.map((s) => (
              <div key={s.id}>
                <div className="text-xs mil-value mb-1">{s.name}</div>
                <div className="text-[10px] text-dim">
                  {s.theater_width_km}KM × {s.theater_height_km}KM
                </div>
              </div>
            ))}
          </Panel>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-6">
          <Link href="/evaluate" className="mil-panel mil-brackets p-5 hover:bg-surface-1 transition-all group">
            <div className="flex items-center justify-between mb-3">
              <span className="mil-heading text-lg">◉ EVALUATE MODE</span>
              <span className="mil-badge mil-badge-dim">01</span>
            </div>
            <p className="text-sm text-dim leading-relaxed mb-3">
              Run a single attack plan against your defense posture.
              Observe real-time engagement, unit losses, and civilian impact.
              Use for tactical analysis of specific threat vectors.
            </p>
            <span className="text-accent text-xs tracking-widest group-hover:mil-glow">
              → LAUNCH EVALUATION
            </span>
          </Link>

          <Link href="/training" className="mil-panel mil-brackets p-5 hover:bg-surface-1 transition-all group">
            <div className="flex items-center justify-between mb-3">
              <span className="mil-heading text-lg">⚡ TRAINING MODE</span>
              <span className="mil-badge mil-badge-dim">02</span>
            </div>
            <p className="text-sm text-dim leading-relaxed mb-3">
              Stress-test defense strategy against many attack plans in parallel.
              Measure defense robustness across randomized and curated threat libraries.
              Identify weaknesses, not just successes.
            </p>
            <span className="text-accent text-xs tracking-widest group-hover:mil-glow">
              → INITIATE TRAINING
            </span>
          </Link>
        </div>

        <Panel title="SYSTEM LOG">
          <div className="space-y-1 text-xs font-mono">
            <div className="text-dim">
              <span className="text-accent">[OK]</span> Simulation engine online — hexagonal architecture loaded
            </div>
            <div className="text-dim">
              <span className="text-accent">[OK]</span> SQLite persistence initialized
            </div>
            <div className="text-dim">
              <span className="text-accent">[OK]</span> Attack plan repository available
            </div>
            <div className="text-dim">
              <span className="text-accent">[OK]</span> {strategies.length} defense strategies registered
            </div>
            <div className="text-dim">
              <span className="text-warn">[WARN]</span> AI generation requires ANTHROPIC_API_KEY env var
            </div>
          </div>
        </Panel>
      </main>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Header } from "@/components/mil/Header";
import { Panel, MetricRow } from "@/components/mil/Panel";
import { getActiveSettings, getKnowledgeSummary, type SettingsDetail } from "@/lib/api";

export default function Home() {
  const [settings, setSettings] = useState<SettingsDetail | null>(null);
  const [counts, setCounts] = useState<Record<string, number>>({});
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getActiveSettings(), getKnowledgeSummary()])
      .then(([s, kb]) => {
        setSettings(s);
        setCounts(kb.counts);
      })
      .catch((e) => setError(String(e)));
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 p-6 max-w-[1400px] mx-auto w-full">
        <div className="mb-6">
          <h1 className="mil-heading text-2xl mb-1">COMMAND OVERVIEW</h1>
          <p className="text-dim text-sm tracking-wider">
            AIR DEFENSE SIMULATION // LLM-DRIVEN DOCTRINE LEARNING
          </p>
        </div>

        {error && (
          <div className="mil-panel mb-4 p-3 border-red-900/50">
            <span className="text-danger text-xs">⚠ {error}</span>
          </div>
        )}

        {/* Status cards */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <Panel title="ACTIVE SETTINGS">
            <div className="text-sm mil-value-accent font-bold mb-1">
              {settings?.name ?? "—"}
            </div>
            <div className="text-[10px] text-dim">{settings?.settings_id ?? ""}</div>
          </Panel>
          <Panel title="ATTACK PLANS">
            <div className="text-3xl mil-value-accent font-bold">{counts.attack_plans ?? 0}</div>
            <div className="text-dim text-[10px]">
              {counts.attack_patterns ?? 0} unique patterns
            </div>
          </Panel>
          <Panel title="PLAYBOOKS">
            <div className="text-3xl mil-value-accent font-bold">{counts.defense_playbooks ?? 0}</div>
            <div className="text-dim text-[10px]">defensive doctrines</div>
          </Panel>
          <Panel title="KNOWLEDGE">
            <div className="text-3xl mil-value-accent font-bold">{counts.doctrine_entries ?? 0}</div>
            <div className="text-dim text-[10px]">
              {counts.match_results ?? 0} match outcomes
            </div>
          </Panel>
        </div>

        {/* What this is */}
        <Panel title="WHAT THIS SYSTEM IS">
          <div className="text-xs text-dim leading-relaxed space-y-2">
            <p>
              The system simulates air defense scenarios deterministically. You control the
              scenario (map, resources, engagement rules), generate or write attack plans,
              and train LLM-authored defense playbooks against them. Every simulation outcome
              is analyzed by an LLM and lessons are written into a growing knowledge base of
              doctrine entries. Over time, new playbooks are generated from the accumulated
              doctrine — the system gets smarter with every match.
            </p>
            <p>
              Simulations are <span className="text-accent">deterministic</span> given the triple
              (attack plan, defense playbook, settings). One simulation per pair — no variance
              to average away. Robustness comes from running against many different attack plans.
            </p>
          </div>
        </Panel>

        <div className="mt-4 grid grid-cols-3 gap-4">
          <Panel title="▶ TEST THE DEFENSE">
            <div className="text-xs text-dim space-y-2 leading-relaxed">
              <p>Run a single attack against a single defense. See the outcome, watch the replay.</p>
            </div>
            <Link href="/evaluation"
                  className="mil-btn mil-btn-primary block text-center mt-3 no-underline">
              GO TO EVALUATE →
            </Link>
          </Panel>

          <Panel title="⚡ TRAIN THE DEFENSE">
            <div className="text-xs text-dim space-y-2 leading-relaxed">
              <p>
                Generate attack sets (random batches or AI-crafted). Train a playbook against
                them. Doctrine grows.
              </p>
            </div>
            <Link href="/training"
                  className="mil-btn mil-btn-primary block text-center mt-3 no-underline">
              GO TO TRAIN →
            </Link>
          </Panel>

          <Panel title="⌧ INSPECT KNOWLEDGE">
            <div className="text-xs text-dim space-y-2 leading-relaxed">
              <p>Browse doctrine, attack patterns, playbooks, and the full match history.</p>
            </div>
            <Link href="/knowledge"
                  className="mil-btn mil-btn-primary block text-center mt-3 no-underline">
              OPEN KNOWLEDGE →
            </Link>
          </Panel>
        </div>

        {/* Workflows */}
        <div className="mt-6">
          <h2 className="mil-heading text-sm mb-3">TYPICAL WORKFLOWS</h2>

          <div className="grid grid-cols-2 gap-4">
            <Panel title="WORKFLOW A — TRAIN FROM SCRATCH">
              <ol className="text-xs text-dim space-y-2 list-decimal list-inside leading-relaxed">
                <li>
                  Go to <Link href="/training" className="text-accent">Train</Link>. In the left
                  <span className="text-foreground"> Generate Attacks </span> panel, create a
                  batch (Random × 8 or Random × 16).
                </li>
                <li>
                  In the <span className="text-foreground">Start Training</span> panel, leave
                  playbook as <span className="font-mono text-[11px]">[NEW]</span> so the LLM
                  generates one from current doctrine.
                </li>
                <li>Press <span className="text-accent">TRAIN ON N PLANS</span>. A background job runs.</li>
                <li>
                  When done, go to <Link href="/knowledge" className="text-accent">Knowledge</Link> to
                  see new doctrine entries and the generated playbook.
                </li>
              </ol>
            </Panel>

            <Panel title="WORKFLOW B — TEST AGAINST A SPECIFIC ATTACK">
              <ol className="text-xs text-dim space-y-2 list-decimal list-inside leading-relaxed">
                <li>
                  Go to <Link href="/training" className="text-accent">Train</Link>. Switch the
                  generator to <span className="text-foreground">AI</span> and describe the
                  attack shape (e.g., "bomber wave on capital with drone feint").
                </li>
                <li>Press <span className="text-accent">GENERATE VIA CLAUDE</span>.</li>
                <li>
                  Either train on it right away (the LLM will generate a defense playbook), OR
                  go to <Link href="/evaluation" className="text-accent">Evaluate</Link> to test
                  an existing playbook against it.
                </li>
                <li>
                  After training, go back to <Link href="/evaluation" className="text-accent">Evaluate</Link> and
                  run the same attack against the new playbook — see if defense improved.
                </li>
              </ol>
            </Panel>

            <Panel title="WORKFLOW C — ROBUSTNESS STRESS TEST">
              <ol className="text-xs text-dim space-y-2 list-decimal list-inside leading-relaxed">
                <li>Generate 3–5 varied random batches in <Link href="/training" className="text-accent">Train</Link>.</li>
                <li>Select all batches (hit SELECT ALL) and train one playbook against all of them.</li>
                <li>
                  Check per-plan outcomes in
                  <Link href="/knowledge" className="text-accent"> Knowledge → Matches</Link>.
                  A robust playbook wins against diverse attacks.
                </li>
              </ol>
            </Panel>

            <Panel title="WORKFLOW D — COMPARE PLAYBOOKS">
              <ol className="text-xs text-dim space-y-2 list-decimal list-inside leading-relaxed">
                <li>Run multiple training jobs — each produces a new playbook.</li>
                <li>
                  In <Link href="/evaluation" className="text-accent">Evaluate</Link>, run the
                  same attack plan against each playbook (swap the playbook dropdown).
                </li>
                <li>The match IDs let you compare fitness scores in Knowledge.</li>
              </ol>
            </Panel>
          </div>
        </div>

        <Panel title="WHERE IS EVERYTHING STORED">
          <div className="text-xs text-dim leading-relaxed space-y-1 mt-2">
            <MetricRow label="Database" value="SQLite at data/simulations.db" />
            <MetricRow label="Tables" value="settings, attack_plans, attack_patterns, defense_playbooks, match_results, doctrine_entries, training_jobs" />
            <MetricRow label="Scope" value="Everything is scoped to the active Settings row. Switching settings shows a different knowledge base." />
            <MetricRow label="Determinism" value="RNG seed = hash(attack_plan_id + defense_playbook_id + settings_id)" />
          </div>
        </Panel>
      </main>
    </div>
  );
}

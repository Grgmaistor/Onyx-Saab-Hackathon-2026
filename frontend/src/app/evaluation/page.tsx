"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Header } from "@/components/mil/Header";
import { Panel, MetricRow, OutcomeBadge } from "@/components/mil/Panel";
import { TacticalMap } from "@/components/mil/TacticalMap";
import { ReplayControls, type PlaybackSpeed, msPerTickFor } from "@/components/mil/ReplayControls";
import {
  getReplay,
  listAttackPlans,
  listPlaybooks,
  runEvaluation,
  type AttackPlan,
  type DefensePlaybook,
  type MatchResult,
  type Replay,
} from "@/lib/api";

export default function EvaluationPage() {
  const [plans, setPlans] = useState<AttackPlan[]>([]);
  const [playbooks, setPlaybooks] = useState<DefensePlaybook[]>([]);
  const [attackId, setAttackId] = useState<string>("");
  const [playbookId, setPlaybookId] = useState<string>("");
  const [analyze, setAnalyze] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<MatchResult | null>(null);
  const [replay, setReplay] = useState<Replay | null>(null);
  const [tickFloat, setTickFloat] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState<PlaybackSpeed>(1);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([listAttackPlans(), listPlaybooks()])
      .then(([p, pb]) => {
        setPlans(p.plans);
        setPlaybooks(pb.playbooks);
        if (p.plans[0]) setAttackId(p.plans[0].plan_id);
        if (pb.playbooks[0]) setPlaybookId(pb.playbooks[0].playbook_id);
      })
      .catch((e) => setError(String(e)));
  }, []);

  const togglePlay = useCallback(() => setIsPlaying((p) => !p), []);

  // Smooth playback via requestAnimationFrame
  const rafRef = useRef<number | null>(null);
  const lastTimeRef = useRef<number>(0);

  useEffect(() => {
    if (!replay) return;
    const maxTick = replay.ticks.length - 1;

    const step = (now: number) => {
      if (lastTimeRef.current === 0) lastTimeRef.current = now;
      const dt = now - lastTimeRef.current;
      lastTimeRef.current = now;

      setTickFloat((prev) => {
        if (!isPlaying) return prev;
        const msPerTick = msPerTickFor(speed);
        const delta = dt / msPerTick;
        const next = prev + delta;
        if (next >= maxTick) {
          setIsPlaying(false);
          return maxTick;
        }
        return next;
      });

      if (isPlaying) {
        rafRef.current = requestAnimationFrame(step);
      }
    };

    if (isPlaying) {
      lastTimeRef.current = 0;
      rafRef.current = requestAnimationFrame(step);
    } else {
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }

    return () => {
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
    };
  }, [isPlaying, replay, speed]);

  const onRun = async () => {
    if (!attackId || !playbookId) return;
    setLoading(true);
    setError(null);
    setReplay(null);
    setTickFloat(0);
    try {
      const res = await runEvaluation({
        attack_plan_id: attackId,
        defense_playbook_id: playbookId,
        analyze,
      });
      setResult(res);
      const rep = await getReplay(res.match_id);
      setReplay(rep);
      setTickFloat(0);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  const currentTick = Math.floor(tickFloat);
  const currentEvents: Array<Record<string, unknown>> =
    replay && replay.ticks[currentTick] ? (replay.ticks[currentTick].events as Array<Record<string, unknown>>) : [];

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 p-6 max-w-[1800px] mx-auto w-full">
        <div className="mb-6">
          <h1 className="mil-heading text-2xl mb-1">◉ EVALUATE</h1>
          <p className="text-dim text-sm tracking-wider">
            RUN ANY ATTACK × ANY PLAYBOOK // DETERMINISTIC OUTCOME // FULL REPLAY
          </p>
        </div>

        {error && (
          <div className="mil-panel mb-4 p-3 border-red-900/50">
            <span className="text-danger text-xs">⚠ {error}</span>
          </div>
        )}

        <div className="grid grid-cols-[320px_1fr_380px] gap-4">
          <Panel title="CONFIG">
            <div className="space-y-3">
              <div>
                <div className="mil-label mb-1">Attack Plan</div>
                <select value={attackId} onChange={(e) => setAttackId(e.target.value)} className="mil-select">
                  <option value="">— Select —</option>
                  {plans.map((p) => (
                    <option key={p.plan_id} value={p.plan_id}>
                      [{p.source.substring(0, 3).toUpperCase()}] {p.name}
                    </option>
                  ))}
                </select>
                <p className="text-[10px] text-dim mt-1">{plans.length} plans available</p>
              </div>

              <div>
                <div className="mil-label mb-1">Defense Playbook</div>
                <select value={playbookId} onChange={(e) => setPlaybookId(e.target.value)} className="mil-select">
                  <option value="">— Select —</option>
                  {playbooks.map((p) => (
                    <option key={p.playbook_id} value={p.playbook_id}>
                      {p.name}
                    </option>
                  ))}
                </select>
                <p className="text-[10px] text-dim mt-1">
                  {playbooks.length} playbooks.{" "}
                  {playbooks.length === 0 && "Run a Training job to generate one."}
                </p>
              </div>

              <label className="flex items-center gap-2 text-xs">
                <input
                  type="checkbox"
                  checked={analyze}
                  onChange={(e) => setAnalyze(e.target.checked)}
                  className="accent-green-400"
                />
                <span>Include AI analysis (~$0.10, API key required)</span>
              </label>

              <button
                onClick={onRun}
                disabled={loading || !attackId || !playbookId}
                className="mil-btn mil-btn-primary w-full"
              >
                {loading ? "◌ SIMULATING..." : "▶ RUN EVALUATION"}
              </button>
            </div>
          </Panel>

          <div className="space-y-2">
            <Panel title="TACTICAL DISPLAY" badge={replay ? "LIVE" : "STANDBY"}>
              <div className="mil-brackets">
                <TacticalMap replay={replay} tickFloat={tickFloat} />
              </div>
            </Panel>
            <ReplayControls
              totalTicks={replay ? replay.ticks.length - 1 : 0}
              currentTick={currentTick}
              isPlaying={isPlaying}
              speed={speed}
              tickMinutes={5}
              onTickChange={(t) => setTickFloat(t)}
              onTogglePlay={togglePlay}
              onSpeedChange={setSpeed}
            />
            {replay && (
              <Panel title="COMMS LOG" badge={`T+${currentTick}`}>
                <div className="max-h-52 overflow-y-auto space-y-0.5 text-[10px] font-mono">
                  {currentEvents.length === 0 ? (
                    <div className="text-dim">[ no events ]</div>
                  ) : (
                    currentEvents.slice(0, 60).map((evt, i) => (
                      <div key={i} className="text-dim">
                        <span className="text-accent">[{String(evt.type).toUpperCase()}]</span>{" "}
                        {_formatEventSummary(evt)}
                      </div>
                    ))
                  )}
                </div>
              </Panel>
            )}
          </div>

          <div className="space-y-4">
            {result ? (
              <>
                <Panel title="OUTCOME" actions={<OutcomeBadge outcome={result.outcome} />}>
                  <div className="mb-3">
                    <div className="mil-label">Match ID</div>
                    <div className="font-mono text-[10px] text-dim">{result.match_id}</div>
                  </div>
                  <MetricRow label="Fitness" value={result.fitness_score.toFixed(1)} accent />
                  <MetricRow
                    label="Capital Survived"
                    value={result.metrics.capital_survived ? "YES" : "NO"}
                    accent={result.metrics.capital_survived}
                  />
                  <MetricRow
                    label="Civilian Casualties"
                    value={result.metrics.total_civilian_casualties.toLocaleString()}
                  />
                  <MetricRow label="Cities Defended" value={`${result.metrics.cities_defended} / 3`} />
                  <MetricRow label="Aircraft Lost" value={result.metrics.aircraft_lost} />
                  <MetricRow label="Aircraft Remaining" value={result.metrics.aircraft_remaining} />
                  <MetricRow label="Bases Lost" value={result.metrics.bases_lost} />
                  <MetricRow label="Parked Destroyed" value={result.metrics.parked_aircraft_destroyed} />
                  <MetricRow label="Engagements" value={result.metrics.total_engagements} />
                  <MetricRow label="Enemy Deterred" value={result.metrics.enemy_sorties_deterred} />
                  <MetricRow
                    label="Air Denial"
                    value={`${(result.metrics.air_denial_score * 100).toFixed(0)}%`}
                  />
                  <MetricRow label="Sorties Flown" value={result.metrics.sorties_flown} />
                </Panel>

                {result.ai_analysis_text && (
                  <Panel title="AI ANALYSIS">
                    <div className="text-xs text-dim leading-relaxed whitespace-pre-wrap">
                      {result.ai_analysis_text}
                    </div>
                    {result.ai_takeaways.length > 0 && (
                      <>
                        <hr className="mil-divider" />
                        <div className="mil-label mb-2">TAKEAWAYS</div>
                        {result.ai_takeaways.map((t, i) => (
                          <div key={i} className="mb-2 text-xs">
                            <div className="text-accent">{t.principle}</div>
                            <div className="text-[10px] text-dim">
                              confidence: {(t.confidence * 100).toFixed(0)}% · tags: {t.tags.join(", ")}
                            </div>
                          </div>
                        ))}
                      </>
                    )}
                  </Panel>
                )}
              </>
            ) : (
              <Panel title="INSTRUCTIONS">
                <div className="space-y-2 text-xs text-dim leading-relaxed">
                  <p>
                    Pick one attack plan and one defense playbook from the dropdowns, then press
                    RUN EVALUATION.
                  </p>
                  <p>
                    The simulation is deterministic: the same pair always produces the same
                    outcome and the same replay.
                  </p>
                  <p>
                    Use the playback controls to scrub through the replay. Aircraft move in
                    interpolated real-time between ticks.
                  </p>
                </div>
              </Panel>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

function _formatEventSummary(evt: Record<string, unknown>): string {
  const t = evt.type as string;
  if (t === "launch") return `${evt.aircraft_id} from ${evt.from_base}`;
  if (t === "landed") return `${evt.aircraft_id} landed at ${evt.base_name}`;
  if (t === "engagement") {
    const o = evt.outcomes as { attacker: string; defender: string } | undefined;
    return `${evt.attacker_id} vs ${evt.defender_id} → ${o?.attacker ?? "?"} / ${o?.defender ?? "?"}`;
  }
  if (t === "aircraft_destroyed") return `${evt.aircraft_id} (${evt.cause})`;
  if (t === "civilian_casualties") return `${evt.location_name}: +${evt.casualties}`;
  if (t === "weapons_delivered") return `${evt.attacker_id} → ${evt.target_name}: ${evt.weapons_delivered}× ${evt.weapon_type}`;
  if (t === "pilot_reflex") return `${evt.aircraft_id} ${evt.reflex} → ${evt.action}`;
  if (t === "playbook_trigger_fired") return `${evt.trigger_name} (${evt.commands_issued} cmds)`;
  return JSON.stringify(evt).substring(0, 150);
}

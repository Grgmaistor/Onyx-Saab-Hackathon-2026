"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { Header } from "@/components/mil/Header";
import { Panel, MetricRow, OutcomeBadge } from "@/components/mil/Panel";
import { TacticalMap } from "@/components/mil/TacticalMap";
import { ReplayControls, msPerTickFor, type PlaybackSpeed } from "@/components/mil/ReplayControls";
import {
  listAttackPlans, evaluateAttackPlan, getReplay, getStrategies,
  type AttackPlan, type EvaluateResponse, type ReplayData, type Strategy,
} from "@/lib/api";

export default function EvaluatePage() {
  const [plans, setPlans] = useState<AttackPlan[]>([]);
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [selectedPlan, setSelectedPlan] = useState<string>("");
  const [strategyId, setStrategyId] = useState("defensive_v1");
  const [seed, setSeed] = useState(42);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<EvaluateResponse | null>(null);
  const [replay, setReplay] = useState<ReplayData | null>(null);
  const [currentTick, setCurrentTick] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState<PlaybackSpeed>(1);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    listAttackPlans().then((d) => {
      setPlans(d.plans);
      if (d.plans.length > 0) setSelectedPlan(d.plans[0].id);
    }).catch((e) => setError(String(e)));
    getStrategies().then((d) => setStrategies(d.strategies)).catch(() => {});
  }, []);

  const handleRun = async () => {
    if (!selectedPlan) return;
    setLoading(true);
    setError(null);
    setReplay(null);
    try {
      const res = await evaluateAttackPlan({
        attack_plan_id: selectedPlan,
        strategy_id: strategyId,
        seed,
      });
      setResult(res);
      const rep = await getReplay(res.simulation_id);
      setReplay(rep);
      setCurrentTick(0);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  const togglePlay = useCallback(() => {
    setIsPlaying((p) => {
      if (!p && replay && currentTick >= replay.ticks.length - 1) {
        setCurrentTick(0);
      }
      return !p;
    });
  }, [replay, currentTick]);

  useEffect(() => {
    if (isPlaying && replay) {
      intervalRef.current = setInterval(() => {
        setCurrentTick((prev) => {
          if (prev >= replay.ticks.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, msPerTickFor(speed));
    } else if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    return () => { if (intervalRef.current) clearInterval(intervalRef.current); };
  }, [isPlaying, replay, speed]);

  const selectedPlanObj = plans.find((p) => p.id === selectedPlan);

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 p-6 max-w-[1600px] mx-auto w-full">
        <div className="mb-6">
          <h1 className="mil-heading text-2xl mb-1">◉ EVALUATE MODE</h1>
          <p className="text-dim text-sm tracking-wider">SINGLE-THREAT ENGAGEMENT ANALYSIS</p>
        </div>

        {error && (
          <div className="mil-panel mb-4 p-3 border-red-900/50">
            <span className="text-danger text-xs">⚠ {error}</span>
          </div>
        )}

        <div className="grid grid-cols-[320px_1fr_360px] gap-4">
          {/* LEFT - Config */}
          <Panel title="ENGAGEMENT PARAMS">
            <div className="space-y-3">
              <div>
                <div className="mil-label mb-1">Attack Plan</div>
                <select value={selectedPlan} onChange={(e) => setSelectedPlan(e.target.value)} className="mil-select">
                  <option value="">— SELECT —</option>
                  {plans.map((p) => (
                    <option key={p.id} value={p.id}>
                      [{p.source.toUpperCase().substring(0, 3)}] {p.name}
                    </option>
                  ))}
                </select>
                {plans.length === 0 && (
                  <p className="text-[10px] text-warn mt-1">NO PLANS STORED. Generate some in Attack Plans section.</p>
                )}
              </div>

              <div>
                <div className="mil-label mb-1">Defense Strategy</div>
                <select value={strategyId} onChange={(e) => setStrategyId(e.target.value)} className="mil-select">
                  {strategies.map((s) => (
                    <option key={s.id} value={s.id}>{s.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <div className="mil-label mb-1">Random Seed</div>
                <input type="number" value={seed} onChange={(e) => setSeed(Number(e.target.value))} className="mil-input" />
              </div>

              <button onClick={handleRun} disabled={loading || !selectedPlan} className="mil-btn mil-btn-primary w-full">
                {loading ? "◌ EXECUTING..." : "▶ RUN EVALUATION"}
              </button>
            </div>

            {selectedPlanObj && (
              <div className="mt-4">
                <hr className="mil-divider-dashed" />
                <div className="mil-label mb-2">Plan Brief</div>
                <div className="text-xs mil-value mb-1">{selectedPlanObj.name}</div>
                <div className="text-[11px] text-dim mb-2">{selectedPlanObj.description}</div>
                <div className="flex gap-1 flex-wrap mb-2">
                  {selectedPlanObj.tags.map((t, i) => (
                    <span key={i} className="mil-badge mil-badge-dim text-[9px]">{t}</span>
                  ))}
                </div>
                <div className="text-[10px] text-dim">{selectedPlanObj.actions.length} scripted actions</div>
              </div>
            )}
          </Panel>

          {/* CENTER - Map + events */}
          <div className="space-y-2">
            <Panel title="TACTICAL DISPLAY" badge={replay ? "LIVE" : "STANDBY"}>
              <div className="mil-brackets">
                <TacticalMap replay={replay} currentTick={currentTick} />
              </div>
            </Panel>
            <ReplayControls
              totalTicks={replay ? replay.ticks.length - 1 : 0}
              currentTick={currentTick}
              isPlaying={isPlaying}
              speed={speed}
              tickMinutes={replay?.tick_minutes ?? 5}
              onTickChange={setCurrentTick}
              onTogglePlay={togglePlay}
              onSpeedChange={setSpeed}
            />
            {replay && replay.ticks[currentTick] && (
              <Panel title="COMMS LOG" badge={`T+${currentTick}`}>
                <div className="max-h-44 overflow-y-auto space-y-0.5">
                  {replay.ticks[currentTick].events.length === 0 ? (
                    <div className="text-[10px] text-dim">[ NO TRAFFIC ]</div>
                  ) : (
                    replay.ticks[currentTick].events.map((evt, i) => (
                      <div key={i} className="text-[11px] font-mono">
                        <span className="text-dim">[{String(i).padStart(3, "0")}]</span>{" "}
                        <span className="mil-value">{evt}</span>
                      </div>
                    ))
                  )}
                </div>
              </Panel>
            )}
          </div>

          {/* RIGHT - Results */}
          <div className="space-y-4">
            {result ? (
              <>
                <Panel title="OUTCOME" actions={<OutcomeBadge outcome={result.outcome} />}>
                  <div className="mb-3">
                    <div className="mil-label">Simulation ID</div>
                    <div className="text-[10px] font-mono text-dim">{result.simulation_id}</div>
                  </div>
                  <MetricRow label="Total Ticks" value={result.total_ticks} />
                  {result.metrics && (
                    <>
                      <MetricRow label="Capital Survived" value={result.metrics.capital_survived ? "YES" : "NO"} accent={result.metrics.capital_survived} />
                      <MetricRow label="Civilian Casualties" value={result.metrics.total_civilian_casualties.toLocaleString()} />
                      <MetricRow label="Cities Defended" value={`${result.metrics.cities_defended} / 3`} />
                      <MetricRow label="Aircraft Lost" value={result.metrics.aircraft_lost} />
                      <MetricRow label="Aircraft Remaining" value={result.metrics.aircraft_remaining} />
                      <MetricRow label="Engagement Win Rate" value={`${(result.metrics.engagement_win_rate * 100).toFixed(1)}%`} />
                      <MetricRow label="Sorties Flown" value={result.metrics.sorties_flown} />
                      <MetricRow label="Total Engagements" value={result.metrics.total_engagements} />
                    </>
                  )}
                </Panel>
              </>
            ) : (
              <Panel title="AWAITING RESULTS">
                <p className="text-dim text-xs">
                  Select an attack plan and press RUN EVALUATION to analyze defense performance against a specific threat vector.
                </p>
              </Panel>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

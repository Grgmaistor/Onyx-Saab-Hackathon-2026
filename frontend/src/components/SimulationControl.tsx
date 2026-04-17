"use client";

import { useState, useEffect } from "react";
import {
  getStrategies,
  getScenarios,
  runSimulation,
  runBatch,
  type Strategy,
  type Scenario,
  type SimulationResponse,
  type BatchResponse,
} from "@/lib/api";

interface Props {
  onSimResult: (result: SimulationResponse) => void;
  onBatchResult: (result: BatchResponse) => void;
}

export function SimulationControl({ onSimResult, onBatchResult }: Props) {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [scenarioId, setScenarioId] = useState("boreal_passage_v1");
  const [strategyId, setStrategyId] = useState("defensive_v1");
  const [enemyStrategyId, setEnemyStrategyId] = useState("balanced_v1");
  const [side, setSide] = useState("north");
  const [seed, setSeed] = useState(42);
  const [batchCount, setBatchCount] = useState(20);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getStrategies().then((d) => setStrategies(d.strategies)).catch(() => {});
    getScenarios().then((d) => setScenarios(d.scenarios)).catch(() => {});
  }, []);

  const handleRunSingle = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await runSimulation({
        scenario_id: scenarioId,
        strategy_id: strategyId,
        enemy_strategy_id: enemyStrategyId,
        side,
        seed,
      });
      onSimResult(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed");
    } finally {
      setLoading(false);
    }
  };

  const handleRunBatch = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await runBatch({
        scenario_id: scenarioId,
        side,
        runs: [
          {
            strategy_id: strategyId,
            enemy_strategy_id: enemyStrategyId,
            seed_start: 1,
            seed_count: batchCount,
          },
        ],
      });
      onBatchResult(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card space-y-4">
      <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">
        Simulation Control
      </h2>

      <div className="space-y-3">
        <label className="block">
          <span className="text-xs text-slate-500">Scenario</span>
          <select
            value={scenarioId}
            onChange={(e) => setScenarioId(e.target.value)}
            className="mt-1 block w-full bg-slate-800 border border-slate-700 rounded px-2 py-1.5 text-sm"
          >
            {scenarios.map((s) => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
            {scenarios.length === 0 && (
              <option value="boreal_passage_v1">Boreal Passage</option>
            )}
          </select>
        </label>

        <label className="block">
          <span className="text-xs text-slate-500">Side</span>
          <select
            value={side}
            onChange={(e) => setSide(e.target.value)}
            className="mt-1 block w-full bg-slate-800 border border-slate-700 rounded px-2 py-1.5 text-sm"
          >
            <option value="north">Country X (North)</option>
            <option value="south">Country Y (South)</option>
          </select>
        </label>

        <label className="block">
          <span className="text-xs text-slate-500">Your Strategy</span>
          <select
            value={strategyId}
            onChange={(e) => setStrategyId(e.target.value)}
            className="mt-1 block w-full bg-slate-800 border border-slate-700 rounded px-2 py-1.5 text-sm"
          >
            {strategies.map((s) => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
            {strategies.length === 0 && (
              <>
                <option value="defensive_v1">defensive_v1</option>
                <option value="aggressive_v1">aggressive_v1</option>
                <option value="balanced_v1">balanced_v1</option>
              </>
            )}
          </select>
        </label>

        <label className="block">
          <span className="text-xs text-slate-500">Enemy Strategy</span>
          <select
            value={enemyStrategyId}
            onChange={(e) => setEnemyStrategyId(e.target.value)}
            className="mt-1 block w-full bg-slate-800 border border-slate-700 rounded px-2 py-1.5 text-sm"
          >
            {strategies.map((s) => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
            {strategies.length === 0 && (
              <>
                <option value="defensive_v1">defensive_v1</option>
                <option value="aggressive_v1">aggressive_v1</option>
                <option value="balanced_v1">balanced_v1</option>
              </>
            )}
          </select>
        </label>

        <div className="grid grid-cols-2 gap-2">
          <label className="block">
            <span className="text-xs text-slate-500">Seed</span>
            <input
              type="number"
              value={seed}
              onChange={(e) => setSeed(Number(e.target.value))}
              className="mt-1 block w-full bg-slate-800 border border-slate-700 rounded px-2 py-1.5 text-sm font-mono"
            />
          </label>
          <label className="block">
            <span className="text-xs text-slate-500">Batch Size</span>
            <input
              type="number"
              value={batchCount}
              onChange={(e) => setBatchCount(Number(e.target.value))}
              className="mt-1 block w-full bg-slate-800 border border-slate-700 rounded px-2 py-1.5 text-sm font-mono"
            />
          </label>
        </div>
      </div>

      <div className="space-y-2 pt-2">
        <button
          onClick={handleRunSingle}
          disabled={loading}
          className="w-full bg-cyan-700 hover:bg-cyan-600 disabled:bg-slate-700 text-white text-sm font-medium py-2 px-4 rounded transition"
        >
          {loading ? "Running..." : "Run Single Simulation"}
        </button>
        <button
          onClick={handleRunBatch}
          disabled={loading}
          className="w-full bg-emerald-700 hover:bg-emerald-600 disabled:bg-slate-700 text-white text-sm font-medium py-2 px-4 rounded transition"
        >
          {loading ? "Running..." : `Run Batch (${batchCount} sims)`}
        </button>
      </div>

      {error && (
        <p className="text-xs text-red-400 mt-2">{error}</p>
      )}
    </div>
  );
}

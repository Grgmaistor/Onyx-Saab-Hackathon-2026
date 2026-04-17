"use client";

import type { SimulationResponse, BatchResults, StrategyAgg } from "@/lib/api";

interface Props {
  simResult: SimulationResponse | null;
  batchResults: BatchResults | null;
}

function OutcomeBadge({ outcome }: { outcome: string }) {
  const cls = outcome === "WIN" ? "badge-win" : outcome === "LOSS" ? "badge-loss" : "badge-timeout";
  return <span className={cls}>{outcome}</span>;
}

function MetricRow({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex justify-between py-1 border-b border-slate-800">
      <span className="text-xs text-slate-500">{label}</span>
      <span className="text-xs font-mono text-slate-300">{value}</span>
    </div>
  );
}

function StrategyCard({ s }: { s: StrategyAgg }) {
  return (
    <div className="card space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-sm font-semibold text-cyan-400">{s.strategy_id}</span>
        <span className="text-xs text-slate-500">{s.simulations} sims</span>
      </div>
      <div className="text-2xl font-bold font-mono text-emerald-400">
        {(s.win_rate * 100).toFixed(1)}%
        <span className="text-xs text-slate-500 font-normal ml-1">win rate</span>
      </div>
      <MetricRow label="Wins / Losses / Timeouts" value={`${s.wins} / ${s.losses} / ${s.timeouts}`} />
      <MetricRow label="Avg Casualties" value={s.avg_civilian_casualties.toFixed(0)} />
      <MetricRow label="Avg Aircraft Lost" value={s.avg_aircraft_lost.toFixed(1)} />
      <MetricRow label="Capital Survival" value={`${(s.capital_survival_rate * 100).toFixed(0)}%`} />
      <MetricRow label="Engagement Win Rate" value={`${(s.avg_engagement_win_rate * 100).toFixed(1)}%`} />
    </div>
  );
}

export function ResultsDashboard({ simResult, batchResults }: Props) {
  if (!simResult && !batchResults) {
    return (
      <div className="card">
        <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-2">Results</h2>
        <p className="text-xs text-slate-600">Run a simulation to see results here.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Results</h2>

      {simResult && (
        <div className="card space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-xs font-mono text-slate-500">{simResult.simulation_id}</span>
            {simResult.outcome && <OutcomeBadge outcome={simResult.outcome} />}
          </div>
          {simResult.total_ticks && (
            <MetricRow label="Total Ticks" value={simResult.total_ticks} />
          )}
          {simResult.metrics && (
            <>
              <MetricRow label="Civilian Casualties" value={simResult.metrics.total_civilian_casualties} />
              <MetricRow label="Time to First Casualty" value={simResult.metrics.time_to_first_casualty ?? "None"} />
              <MetricRow label="Aircraft Lost" value={simResult.metrics.aircraft_lost} />
              <MetricRow label="Aircraft Remaining" value={simResult.metrics.aircraft_remaining} />
              <MetricRow label="Cities Defended" value={simResult.metrics.cities_defended} />
              <MetricRow label="Capital Survived" value={simResult.metrics.capital_survived ? "Yes" : "No"} />
              <MetricRow label="Engagements Won" value={`${(simResult.metrics.engagement_win_rate * 100).toFixed(1)}%`} />
              <MetricRow label="Sorties Flown" value={simResult.metrics.sorties_flown} />
              <MetricRow label="Fuel Efficiency" value={`${(simResult.metrics.fuel_efficiency * 100).toFixed(1)}%`} />
            </>
          )}
        </div>
      )}

      {batchResults && (
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-xs font-mono text-slate-500">{batchResults.batch_id}</span>
            <span className="text-xs text-slate-500">{batchResults.total} simulations</span>
          </div>
          {batchResults.best_strategy && (
            <div className="text-xs text-emerald-400">
              Best strategy: <span className="font-bold">{batchResults.best_strategy}</span>
            </div>
          )}
          {batchResults.by_strategy.map((s) => (
            <StrategyCard key={s.strategy_id} s={s} />
          ))}
        </div>
      )}
    </div>
  );
}

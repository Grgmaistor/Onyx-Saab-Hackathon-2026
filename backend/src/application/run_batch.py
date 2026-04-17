from __future__ import annotations

import os
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed

from src.domain.entities.aircraft import Side
from src.domain.entities.simulation import SimulationConfig, SimulationResult
from src.domain.ports.simulation_repository import SimulationRepository
from src.domain.ports.strategy import StrategyPort
from src.domain.services.simulation_engine import run_simulation


def _run_one(args: tuple) -> SimulationResult:
    scenario, strategy, enemy_strategy, config = args
    return run_simulation(scenario, strategy, enemy_strategy, config)


class RunBatchUseCase:
    def __init__(self, repo: SimulationRepository, scenarios: dict[str, dict],
                 strategies: dict[str, StrategyPort], max_workers: int | None = None) -> None:
        self._repo = repo
        self._scenarios = scenarios
        self._strategies = strategies
        self._max_workers = max_workers or os.cpu_count() or 4

    def execute(self, scenario_id: str, side: str, runs: list[dict]) -> dict:
        batch_id = f"batch-{uuid.uuid4().hex[:8]}"
        scenario = self._scenarios[scenario_id]
        tasks: list[tuple] = []

        for r in runs:
            strat = self._strategies[r["strategy_id"]]
            enemy = self._strategies[r["enemy_strategy_id"]]
            for seed in range(r.get("seed_start", 1), r.get("seed_start", 1) + r.get("seed_count", 10)):
                cfg = SimulationConfig(scenario_id=scenario_id, strategy_id=r["strategy_id"],
                                       enemy_strategy_id=r["enemy_strategy_id"], side=Side(side), seed=seed)
                tasks.append((scenario, strat, enemy, cfg))

        results: list[SimulationResult] = []
        with ProcessPoolExecutor(max_workers=self._max_workers) as pool:
            futs = {pool.submit(_run_one, t): i for i, t in enumerate(tasks)}
            for fut in as_completed(futs):
                res = fut.result()
                res.batch_id = batch_id
                self._repo.save(res)
                results.append(res)

        return {"batch_id": batch_id, "total": len(results), "results": results}

from __future__ import annotations

import os
from concurrent.futures import ProcessPoolExecutor, as_completed

from src.domain.entities.simulation import SimulationConfig, SimulationResult
from src.domain.ports.strategy import StrategyPort
from src.domain.services.simulation_engine import run_simulation


def _run_one(
    scenario: dict,
    strategy: StrategyPort,
    enemy_strategy: StrategyPort,
    config: SimulationConfig,
) -> SimulationResult:
    return run_simulation(scenario, strategy, enemy_strategy, config)


def run_batch_parallel(
    configs: list[SimulationConfig],
    strategies: dict[str, StrategyPort],
    enemy_strategies: dict[str, StrategyPort],
    scenario: dict,
    max_workers: int | None = None,
) -> list[SimulationResult]:
    """Run many simulations in parallel using ProcessPoolExecutor.

    Note: StrategyPort implementations must be picklable for this to work
    across processes.
    """
    max_workers = max_workers or os.cpu_count() or 4
    results: list[SimulationResult] = []

    with ProcessPoolExecutor(max_workers=max_workers) as pool:
        futures = {}
        for cfg in configs:
            strategy = strategies[cfg.strategy_id]
            enemy_strategy = enemy_strategies[cfg.enemy_strategy_id]
            fut = pool.submit(_run_one, scenario, strategy, enemy_strategy, cfg)
            futures[fut] = cfg

        for future in as_completed(futures):
            result = future.result()
            results.append(result)

    return results

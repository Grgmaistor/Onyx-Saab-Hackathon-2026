from __future__ import annotations

from src.domain.entities.simulation import SimulationConfig, SimulationResult
from src.domain.ports.simulation_repository import SimulationRepository
from src.domain.ports.strategy import StrategyPort
from src.domain.services.simulation_engine import run_simulation


class RunSimulationUseCase:
    def __init__(self, repo: SimulationRepository, scenarios: dict[str, dict],
                 strategies: dict[str, StrategyPort]) -> None:
        self._repo = repo
        self._scenarios = scenarios
        self._strategies = strategies

    def execute(self, config: SimulationConfig) -> SimulationResult:
        scenario = self._scenarios[config.scenario_id]
        strategy = self._strategies[config.strategy_id]
        enemy = self._strategies[config.enemy_strategy_id]
        result = run_simulation(scenario, strategy, enemy, config)
        self._repo.save(result)
        return result

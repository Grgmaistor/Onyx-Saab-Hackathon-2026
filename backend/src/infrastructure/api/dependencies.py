from __future__ import annotations

import sys
from pathlib import Path
from functools import lru_cache

from src.infrastructure.persistence.sqlite_repo import SQLiteSimulationRepo
from src.infrastructure.persistence.database import init_db
from src.infrastructure.export.json_export import JSONExportAdapter
from src.infrastructure.simulation.scenario_loader import load_scenarios
from src.infrastructure.simulation.strategy_registry import StrategyRegistry
from src.application.run_simulation import RunSimulationUseCase
from src.application.run_batch import RunBatchUseCase
from src.application.get_results import GetResultsUseCase
from src.application.export_replay import ExportReplayUseCase


def _load_strategies() -> StrategyRegistry:
    registry = StrategyRegistry()

    # Add scenario/strategies to path
    strat_dir = Path("scenario/strategies")
    if strat_dir.exists():
        sys.path.insert(0, str(strat_dir.parent.parent))

    try:
        from scenario.strategies.defensive import DefensiveStrategy
        registry.register(DefensiveStrategy())
    except ImportError:
        pass
    try:
        from scenario.strategies.aggressive import AggressiveStrategy
        registry.register(AggressiveStrategy())
    except ImportError:
        pass
    try:
        from scenario.strategies.balanced import BalancedStrategy
        registry.register(BalancedStrategy())
    except ImportError:
        pass

    return registry


@lru_cache
def get_registry() -> StrategyRegistry:
    return _load_strategies()


@lru_cache
def get_scenarios() -> dict[str, dict]:
    return load_scenarios("scenario")


@lru_cache
def get_repo() -> SQLiteSimulationRepo:
    init_db()
    return SQLiteSimulationRepo()


@lru_cache
def get_exporter() -> JSONExportAdapter:
    return JSONExportAdapter()


def get_run_sim_uc() -> RunSimulationUseCase:
    return RunSimulationUseCase(get_repo(), get_scenarios(), get_registry().as_dict())


def get_run_batch_uc() -> RunBatchUseCase:
    return RunBatchUseCase(get_repo(), get_scenarios(), get_registry().as_dict())


def get_results_uc() -> GetResultsUseCase:
    return GetResultsUseCase(get_repo())


def get_export_uc() -> ExportReplayUseCase:
    return ExportReplayUseCase(get_repo(), get_exporter())

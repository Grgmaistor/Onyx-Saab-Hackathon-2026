from __future__ import annotations

from pydantic import BaseModel


class RunSimulationRequest(BaseModel):
    scenario_id: str = "boreal_passage_v1"
    strategy_id: str = "defensive_v1"
    enemy_strategy_id: str = "balanced_v1"
    side: str = "north"
    seed: int = 42


class SimulationResponse(BaseModel):
    simulation_id: str
    status: str
    outcome: str | None = None
    total_ticks: int | None = None
    metrics: dict | None = None


class BatchRunConfig(BaseModel):
    strategy_id: str
    enemy_strategy_id: str
    seed_start: int = 1
    seed_count: int = 10


class BatchRequest(BaseModel):
    scenario_id: str = "boreal_passage_v1"
    side: str = "north"
    runs: list[BatchRunConfig]


class BatchResponse(BaseModel):
    batch_id: str
    total_simulations: int
    status: str

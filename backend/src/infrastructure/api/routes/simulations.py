from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.domain.entities.aircraft import Side
from src.domain.entities.simulation import SimulationConfig
from src.infrastructure.api.schemas.simulation import (
    RunSimulationRequest, SimulationResponse, BatchRequest, BatchResponse,
)
from src.infrastructure.api.dependencies import get_run_sim_uc, get_run_batch_uc, get_results_uc, get_export_uc

router = APIRouter(prefix="/simulations", tags=["simulations"])


@router.post("", response_model=SimulationResponse)
def run_simulation(req: RunSimulationRequest):
    uc = get_run_sim_uc()
    config = SimulationConfig(
        scenario_id=req.scenario_id, strategy_id=req.strategy_id,
        enemy_strategy_id=req.enemy_strategy_id, side=Side(req.side), seed=req.seed)
    result = uc.execute(config)
    return SimulationResponse(
        simulation_id=result.simulation_id, status="completed",
        outcome=result.outcome.value, total_ticks=result.total_ticks,
        metrics=result.metrics.to_dict() if result.metrics else None)


@router.post("/batch", response_model=BatchResponse)
def run_batch(req: BatchRequest):
    uc = get_run_batch_uc()
    runs = [{"strategy_id": r.strategy_id, "enemy_strategy_id": r.enemy_strategy_id,
             "seed_start": r.seed_start, "seed_count": r.seed_count} for r in req.runs]
    result = uc.execute(req.scenario_id, req.side, runs)
    return BatchResponse(batch_id=result["batch_id"], total_simulations=result["total"], status="completed")


@router.get("/{simulation_id}", response_model=SimulationResponse)
def get_simulation(simulation_id: str):
    uc = get_results_uc()
    result = uc.get(simulation_id)
    if not result:
        raise HTTPException(404, "Simulation not found")
    return SimulationResponse(
        simulation_id=result.simulation_id, status="completed",
        outcome=result.outcome.value, total_ticks=result.total_ticks,
        metrics=result.metrics.to_dict() if result.metrics else None)


@router.get("/{simulation_id}/replay")
def get_replay(simulation_id: str):
    uc = get_export_uc()
    replay = uc.execute(simulation_id)
    if not replay:
        raise HTTPException(404, "Simulation not found")
    return replay

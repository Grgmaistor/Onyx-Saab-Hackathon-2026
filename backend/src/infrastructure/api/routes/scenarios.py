from __future__ import annotations

from fastapi import APIRouter, HTTPException
from src.infrastructure.api.dependencies import get_scenarios

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


@router.get("")
def list_scenarios():
    scenarios = get_scenarios()
    return {"scenarios": [
        {"id": sid, "name": s.get("name", sid),
         "theater_width_km": s.get("theater_width_km"),
         "theater_height_km": s.get("theater_height_km")}
        for sid, s in scenarios.items()]}


@router.get("/{scenario_id}")
def get_scenario(scenario_id: str):
    scenarios = get_scenarios()
    if scenario_id not in scenarios:
        raise HTTPException(404, "Scenario not found")
    return scenarios[scenario_id]

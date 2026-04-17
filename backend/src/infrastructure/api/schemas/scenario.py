from __future__ import annotations

from pydantic import BaseModel


class ScenarioSummary(BaseModel):
    id: str
    name: str
    theater_width_km: float = 0
    theater_height_km: float = 0
    tick_minutes: float = 5
    max_ticks: int = 1000
    north_bases: int = 0
    south_bases: int = 0
    total_aircraft: int = 0


class ScenarioDetail(BaseModel):
    id: str
    name: str
    theater_width_km: float = 0
    theater_height_km: float = 0
    tick_minutes: float = 5
    max_ticks: int = 1000
    bases: list[dict] = []
    cities: list[dict] = []
    starting_aircraft: dict = {}

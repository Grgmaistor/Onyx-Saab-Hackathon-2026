from __future__ import annotations

from pydantic import BaseModel


class StrategyAggregation(BaseModel):
    strategy_id: str
    simulations: int
    wins: int
    losses: int
    timeouts: int
    win_rate: float
    avg_civilian_casualties: float
    avg_aircraft_lost: float
    avg_engagement_win_rate: float
    capital_survival_rate: float


class BatchResultsResponse(BaseModel):
    batch_id: str
    status: str
    total: int
    by_strategy: list[StrategyAggregation]
    best_strategy: str | None = None

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from src.infrastructure.api.dependencies import get_results_uc

router = APIRouter(prefix="/results", tags=["results"])


@router.get("/compare")
def compare_strategies(batch_id: str = Query(...), strategy_a: str = Query(...), strategy_b: str = Query(...)):
    uc = get_results_uc()
    results = uc.list_by_batch(batch_id)
    if not results:
        raise HTTPException(404, "Batch not found")

    def agg(strat_id):
        rs = [r for r in results if r.config.strategy_id == strat_id]
        if not rs:
            return None
        n = len(rs)
        wins = sum(1 for r in rs if r.outcome.value == "WIN")
        cas = sum(r.metrics.total_civilian_casualties for r in rs if r.metrics)
        return {"strategy_id": strat_id, "simulations": n, "win_rate": wins / n,
                "avg_casualties": cas / n}

    a = agg(strategy_a)
    b = agg(strategy_b)
    if not a or not b:
        raise HTTPException(404, "Strategy not found in batch")

    return {"strategy_a": a, "strategy_b": b, "comparison": {
        "win_rate_delta": round(a["win_rate"] - b["win_rate"], 4),
        "casualties_delta": round(a["avg_casualties"] - b["avg_casualties"], 1),
        "recommended": a["strategy_id"] if a["win_rate"] > b["win_rate"] else b["strategy_id"],
    }}

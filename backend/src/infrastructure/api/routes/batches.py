from __future__ import annotations

from fastapi import APIRouter, HTTPException
from src.infrastructure.api.dependencies import get_results_uc

router = APIRouter(prefix="/batches", tags=["batches"])


@router.get("/{batch_id}/results")
def get_batch_results(batch_id: str):
    uc = get_results_uc()
    results = uc.list_by_batch(batch_id)
    if not results:
        raise HTTPException(404, "Batch not found")

    by_strategy: dict[str, dict] = {}
    for r in results:
        sid = r.config.strategy_id
        if sid not in by_strategy:
            by_strategy[sid] = {"wins": 0, "losses": 0, "timeouts": 0, "total": 0,
                                "casualties": 0, "ac_lost": 0, "win_rate_sum": 0, "cap_survived": 0}
        s = by_strategy[sid]
        s["total"] += 1
        if r.outcome.value == "WIN":
            s["wins"] += 1
        elif r.outcome.value == "LOSS":
            s["losses"] += 1
        else:
            s["timeouts"] += 1
        if r.metrics:
            s["casualties"] += r.metrics.total_civilian_casualties
            s["ac_lost"] += r.metrics.aircraft_lost
            s["win_rate_sum"] += r.metrics.engagement_win_rate
            if r.metrics.capital_survived:
                s["cap_survived"] += 1

    agg = []
    for sid, s in by_strategy.items():
        n = s["total"]
        agg.append({
            "strategy_id": sid, "simulations": n,
            "wins": s["wins"], "losses": s["losses"], "timeouts": s["timeouts"],
            "win_rate": s["wins"] / n if n else 0,
            "avg_civilian_casualties": s["casualties"] / n if n else 0,
            "avg_aircraft_lost": s["ac_lost"] / n if n else 0,
            "avg_engagement_win_rate": s["win_rate_sum"] / n if n else 0,
            "capital_survival_rate": s["cap_survived"] / n if n else 0,
        })

    best = max(agg, key=lambda x: x["win_rate"])["strategy_id"] if agg else None
    return {"batch_id": batch_id, "status": "completed", "total": len(results),
            "by_strategy": agg, "best_strategy": best}

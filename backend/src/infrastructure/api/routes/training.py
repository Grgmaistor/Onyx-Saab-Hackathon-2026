from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.domain.entities.aircraft import Side
from src.domain.entities.attack_plan import AttackPlan
from src.domain.entities.simulation import SimulationConfig
from src.domain.services.attack_plan_strategy import AttackPlanStrategy
from src.domain.services.simulation_engine import run_simulation
from src.infrastructure.persistence.attack_plan_repo import AttackPlanRepo
from src.infrastructure.api.dependencies import get_scenarios, get_registry, get_repo

import uuid
import os
from concurrent.futures import ProcessPoolExecutor, as_completed

router = APIRouter(prefix="/training", tags=["training"])
_plan_repo = AttackPlanRepo()


class EvaluateRequest(BaseModel):
    attack_plan_id: str
    strategy_id: str = "defensive_v1"
    scenario_id: str = "boreal_passage_v1"
    side: str = "north"
    seed: int = 42


class TrainingRequest(BaseModel):
    attack_plan_ids: list[str]
    strategy_id: str = "defensive_v1"
    scenario_id: str = "boreal_passage_v1"
    side: str = "north"
    seeds_per_plan: int = 5
    seed_start: int = 1


def _run_one_eval(scenario, strategy, enemy_strategy, config):
    return run_simulation(scenario, strategy, enemy_strategy, config)


@router.post("/evaluate")
def evaluate(req: EvaluateRequest):
    plan = _plan_repo.get(req.attack_plan_id)
    if not plan:
        raise HTTPException(404, "Attack plan not found")

    scenarios = get_scenarios()
    scenario = scenarios.get(req.scenario_id)
    if not scenario:
        raise HTTPException(404, "Scenario not found")

    registry = get_registry()
    strategy = registry.get(req.strategy_id)
    if not strategy:
        raise HTTPException(404, f"Strategy {req.strategy_id} not found")

    enemy_strategy = AttackPlanStrategy(plan)

    config = SimulationConfig(
        scenario_id=req.scenario_id,
        strategy_id=req.strategy_id,
        enemy_strategy_id=f"attack_plan:{plan.id}",
        side=Side(req.side),
        seed=req.seed,
    )

    result = run_simulation(scenario, strategy, enemy_strategy, config)
    sim_repo = get_repo()
    sim_repo.save(result)

    return {
        "simulation_id": result.simulation_id,
        "outcome": result.outcome.value,
        "total_ticks": result.total_ticks,
        "attack_plan": plan.to_dict(),
        "metrics": result.metrics.to_dict() if result.metrics else None,
    }


@router.post("/run")
def run_training(req: TrainingRequest):
    scenarios = get_scenarios()
    scenario = scenarios.get(req.scenario_id)
    if not scenario:
        raise HTTPException(404, "Scenario not found")

    registry = get_registry()
    strategy = registry.get(req.strategy_id)
    if not strategy:
        raise HTTPException(404, f"Strategy {req.strategy_id} not found")

    plans: list[AttackPlan] = []
    for pid in req.attack_plan_ids:
        p = _plan_repo.get(pid)
        if p:
            plans.append(p)
    if not plans:
        raise HTTPException(400, "No valid attack plans found")

    batch_id = f"train-{uuid.uuid4().hex[:8]}"
    sim_repo = get_repo()
    all_results = []
    max_workers = os.cpu_count() or 4

    # Build tasks
    tasks = []
    for plan in plans:
        enemy = AttackPlanStrategy(plan)
        for seed in range(req.seed_start, req.seed_start + req.seeds_per_plan):
            config = SimulationConfig(
                scenario_id=req.scenario_id,
                strategy_id=req.strategy_id,
                enemy_strategy_id=f"attack_plan:{plan.id}",
                side=Side(req.side),
                seed=seed,
            )
            tasks.append((scenario, strategy, enemy, config))

    # Run in parallel
    with ProcessPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_run_one_eval, *t): i for i, t in enumerate(tasks)}
        for fut in as_completed(futures):
            res = fut.result()
            res.batch_id = batch_id
            sim_repo.save(res)
            all_results.append(res)

    # Aggregate by attack plan
    by_plan: dict[str, dict] = {}
    for r in all_results:
        pid = r.config.enemy_strategy_id.replace("attack_plan:", "")
        if pid not in by_plan:
            by_plan[pid] = {"wins": 0, "losses": 0, "timeouts": 0, "total": 0,
                            "casualties": 0, "ac_lost": 0}
        s = by_plan[pid]
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

    summary = []
    for pid, s in by_plan.items():
        n = s["total"]
        summary.append({
            "attack_plan_id": pid,
            "simulations": n,
            "wins": s["wins"],
            "losses": s["losses"],
            "timeouts": s["timeouts"],
            "defense_success_rate": s["wins"] / n if n else 0,
            "avg_casualties": s["casualties"] / n if n else 0,
            "avg_aircraft_lost": s["ac_lost"] / n if n else 0,
        })

    total_sims = len(all_results)
    total_wins = sum(s["wins"] for s in by_plan.values())

    return {
        "batch_id": batch_id,
        "total_simulations": total_sims,
        "total_wins": total_wins,
        "overall_defense_rate": total_wins / total_sims if total_sims else 0,
        "by_attack_plan": summary,
    }

from __future__ import annotations

import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.domain.entities.attack_plan import AttackPlan, AttackPlanSource
from src.domain.services.random_plan_generator import generate_random_plan, generate_random_plans
from src.infrastructure.persistence.attack_plan_repo import AttackPlanRepo
from src.infrastructure.ai.claude_generator import generate_attack_plan_with_claude

router = APIRouter(prefix="/attack-plans", tags=["attack-plans"])

_repo = AttackPlanRepo()


class CreatePlanRequest(BaseModel):
    name: str
    description: str = ""
    tags: list[str] = []
    actions: list[dict]


class GenerateRandomRequest(BaseModel):
    count: int = 10
    base_seed: int = 1


class AIGenerateRequest(BaseModel):
    prompt: str


@router.get("")
def list_plans(source: str | None = None):
    plans = _repo.list_all(source=source)
    return {"plans": [p.to_dict() for p in plans], "total": len(plans)}


@router.get("/summary")
def get_summary():
    counts = _repo.count_by_source()
    total = sum(counts.values())
    return {"total": total, "by_source": counts}


@router.get("/{plan_id}")
def get_plan(plan_id: str):
    plan = _repo.get(plan_id)
    if not plan:
        raise HTTPException(404, "Attack plan not found")
    return plan.to_dict()


@router.post("")
def create_plan(req: CreatePlanRequest):
    import uuid
    from datetime import datetime, timezone

    plan_data = {
        "id": f"cst-{uuid.uuid4().hex[:8]}",
        "name": req.name,
        "source": "custom",
        "description": req.description,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "tags": req.tags + ["custom"],
        "actions": req.actions,
    }
    plan = AttackPlan.from_dict(plan_data)
    _repo.save(plan)
    return plan.to_dict()


@router.post("/generate-random")
def generate_random(req: GenerateRandomRequest):
    plans = generate_random_plans(count=req.count, base_seed=req.base_seed)
    for p in plans:
        _repo.save(p)
    return {"generated": len(plans), "plans": [p.to_dict() for p in plans]}


@router.post("/generate-ai")
async def generate_ai(req: AIGenerateRequest):
    try:
        plan = await generate_attack_plan_with_claude(req.prompt)
        _repo.save(plan)
        return plan.to_dict()
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"AI generation failed: {str(e)}")


@router.delete("/{plan_id}")
def delete_plan(plan_id: str):
    if not _repo.delete(plan_id):
        raise HTTPException(404, "Attack plan not found")
    return {"deleted": True}

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.infrastructure.api.dependencies import (
    get_active_settings_or_bootstrap,
    get_attack_uc,
    get_kb,
)
from src.infrastructure.api.schemas import (
    AttackPlanResponse,
    GenerateAIAttackRequest,
    GenerateRandomAttackRequest,
)


router = APIRouter(prefix="/attack-plans", tags=["attack-plans"])


def _to_response(plan) -> dict:
    return plan.to_dict()


@router.get("")
def list_plans():
    settings = get_active_settings_or_bootstrap()
    uc = get_attack_uc()
    plans = uc.list_for_settings(settings.settings_id)
    return {"plans": [_to_response(p) for p in plans], "total": len(plans)}


@router.get("/{plan_id}")
def get_plan(plan_id: str):
    uc = get_attack_uc()
    plan = uc.get(plan_id)
    if not plan:
        raise HTTPException(404, "Attack plan not found")
    return _to_response(plan)


@router.post("/generate-random")
def generate_random(req: GenerateRandomAttackRequest):
    settings = get_active_settings_or_bootstrap()
    uc = get_attack_uc()
    plans = uc.generate_random(settings, count=req.count, base_seed=req.base_seed)
    return {"generated": len(plans), "plans": [_to_response(p) for p in plans]}


@router.post("/generate-ai")
async def generate_ai(req: GenerateAIAttackRequest):
    settings = get_active_settings_or_bootstrap()
    uc = get_attack_uc()
    try:
        plan = await uc.generate_ai(settings, req.prompt)
        return _to_response(plan)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"AI generation failed: {e}")


@router.delete("/{plan_id}")
def delete_plan(plan_id: str):
    uc = get_attack_uc()
    if not uc.delete(plan_id):
        raise HTTPException(404, "Attack plan not found")
    return {"deleted": plan_id}

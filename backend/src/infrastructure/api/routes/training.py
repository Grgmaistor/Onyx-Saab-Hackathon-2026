from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.infrastructure.api.dependencies import (
    get_active_settings_or_bootstrap,
    get_training_orchestrator,
)
from src.infrastructure.api.schemas import StartTrainingRequest


router = APIRouter(prefix="/training", tags=["training"])


@router.post("/start")
async def start_training(req: StartTrainingRequest):
    settings = get_active_settings_or_bootstrap()
    if not req.attack_plan_ids:
        raise HTTPException(400, "Must provide at least one attack_plan_id")
    orch = get_training_orchestrator()
    job_id = orch.start_job(
        settings=settings,
        attack_plan_ids=req.attack_plan_ids,
        defense_playbook_id=req.defense_playbook_id,
        extra_playbook_prompt=req.extra_playbook_prompt,
    )
    return {"job_id": job_id, "status": "pending"}


@router.get("/jobs/{job_id}")
def get_job(job_id: str):
    orch = get_training_orchestrator()
    status = orch.get_job_status(job_id)
    if not status:
        raise HTTPException(404, "Job not found")
    return status


@router.get("/jobs")
def list_jobs():
    settings = get_active_settings_or_bootstrap()
    orch = get_training_orchestrator()
    return {"jobs": orch.list_jobs(settings.settings_id)}

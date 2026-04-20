from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.infrastructure.api.dependencies import (
    get_active_settings_or_bootstrap,
    get_attack_uc,
    get_kb,
    get_match_uc,
    get_playbook_uc,
)
from src.infrastructure.api.schemas import RunEvaluationRequest


router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.post("/run")
async def run_evaluation(req: RunEvaluationRequest):
    """Run a single evaluation: attack plan × defense playbook → MatchResult."""
    settings = get_active_settings_or_bootstrap()
    attack = get_attack_uc().get(req.attack_plan_id)
    if not attack:
        raise HTTPException(404, "Attack plan not found")
    playbook = get_playbook_uc().get(req.defense_playbook_id)
    if not playbook:
        raise HTTPException(404, "Defense playbook not found")

    match_uc = get_match_uc()
    if req.analyze:
        match = await match_uc.run_and_analyze(settings, attack, playbook)
    else:
        match = match_uc.run(settings, attack, playbook)

    return {
        "match_id": match.match_id,
        "outcome": match.outcome.value,
        "fitness_score": match.fitness_score,
        "metrics": match.metrics.to_dict(),
        "ai_analysis_text": match.ai_analysis_text,
        "ai_takeaways": [t.to_dict() for t in match.ai_takeaways],
        "total_ticks": len(match.event_log) - 1,
    }


@router.get("/matches/{match_id}")
def get_match(match_id: str):
    match = get_kb().match_results.get(match_id)
    if not match:
        raise HTTPException(404, "Match not found")
    return {
        "match_id": match.match_id,
        "settings_id": match.settings_id,
        "attack_plan_id": match.attack_plan_id,
        "pattern_id": match.pattern_id,
        "defense_playbook_id": match.defense_playbook_id,
        "outcome": match.outcome.value,
        "fitness_score": match.fitness_score,
        "metrics": match.metrics.to_dict(),
        "ai_analysis_text": match.ai_analysis_text,
        "ai_takeaways": [t.to_dict() for t in match.ai_takeaways],
        "created_at": match.created_at,
        "analysis_completed_at": match.analysis_completed_at,
    }


@router.get("/matches/{match_id}/replay")
def get_replay(match_id: str):
    match = get_kb().match_results.get(match_id)
    if not match:
        raise HTTPException(404, "Match not found")
    return {
        "match_id": match.match_id,
        "outcome": match.outcome.value,
        "total_ticks": len(match.event_log) - 1,
        "ticks": match.event_log,
        "metrics": match.metrics.to_dict(),
    }


@router.get("/matches")
def list_matches(limit: int = 50):
    settings = get_active_settings_or_bootstrap()
    # Summary query skips the massive event_log_json column (10-50x faster)
    matches = get_kb().match_results.list_summary_by_settings(
        settings.settings_id, limit=limit,
    )
    return {"matches": matches, "total": len(matches)}

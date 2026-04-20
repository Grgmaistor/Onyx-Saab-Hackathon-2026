from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.infrastructure.api.dependencies import (
    get_active_settings_or_bootstrap,
    get_kb,
)


router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("/summary")
def summary():
    settings = get_active_settings_or_bootstrap()
    kb = get_kb()
    # Use cheap COUNT(*) for matches; other tables are small enough to list directly
    return {
        "settings_id": settings.settings_id,
        "settings_name": settings.name,
        "counts": {
            "attack_plans": len(kb.attack_plans.list_by_settings(settings.settings_id)),
            "attack_patterns": len(kb.attack_patterns.list_by_settings(settings.settings_id)),
            "defense_playbooks": len(kb.defense_playbooks.list_by_settings(settings.settings_id)),
            "match_results": kb.match_results.count_by_settings(settings.settings_id),
            "doctrine_entries": len(kb.doctrine.list_active(settings.settings_id)),
        },
    }


@router.get("/doctrine")
def list_doctrine(category: str | None = None):
    settings = get_active_settings_or_bootstrap()
    kb = get_kb()
    entries = kb.doctrine.list_active(settings.settings_id, category=category)
    return {
        "entries": [e.to_dict() for e in entries],
        "total": len(entries),
    }


@router.get("/patterns")
def list_patterns():
    settings = get_active_settings_or_bootstrap()
    kb = get_kb()
    patterns = kb.attack_patterns.list_by_settings(settings.settings_id)
    return {"patterns": [p.to_dict() for p in patterns], "total": len(patterns)}


@router.get("/patterns/{pattern_id}/matches")
def pattern_matches(pattern_id: str, top_k: int = 10):
    kb = get_kb()
    matches = kb.match_results.list_by_pattern(pattern_id, top_k=top_k)
    return {
        "matches": [
            {
                "match_id": m.match_id,
                "attack_plan_id": m.attack_plan_id,
                "defense_playbook_id": m.defense_playbook_id,
                "outcome": m.outcome.value,
                "fitness_score": m.fitness_score,
                "ai_analysis_text": m.ai_analysis_text[:500] if m.ai_analysis_text else "",
                "created_at": m.created_at,
            }
            for m in matches
        ],
    }

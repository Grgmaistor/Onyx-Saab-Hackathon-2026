"""
LLM-powered generators for attacks, playbooks, match analysis, and doctrine.
Thin adapters around ClaudeAgent with role-specific system prompts.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from src.domain.ports.llm_agent import LLMAgentPort, LLMMessage
from src.domain.value_objects.attack_plan import AttackPlan, AttackPlanSource
from src.domain.value_objects.defense_playbook import DefensePlaybook, PlaybookSource
from src.domain.value_objects.doctrine_entry import DoctrineEntry
from src.domain.value_objects.match_result import AITakeaway, MatchResult
from src.domain.value_objects.settings import Settings

from .prompts import (
    ATTACK_PLAN_GENERATOR_SYSTEM,
    DEFENSE_PLAYBOOK_GENERATOR_SYSTEM,
    DOCTRINE_SYNTHESIZER_SYSTEM,
    MATCH_ANALYZER_SYSTEM,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# =======================================================================
# Attack plan generator
# =======================================================================

class AttackPlanGenerator:
    def __init__(self, agent: LLMAgentPort) -> None:
        self._agent = agent

    async def generate(self, settings: Settings, user_prompt: str) -> AttackPlan:
        context = _settings_context(settings)
        user_msg = f"""Settings context:
{context}

User request:
{user_prompt}

Generate a valid attack plan JSON matching the schema. Use only the aircraft and bases
listed above. Stay within the attacker's resource counts."""

        parsed, _resp = await self._agent.call_json(
            system_prompt=ATTACK_PLAN_GENERATOR_SYSTEM,
            messages=[LLMMessage(role="user", content=user_msg)],
            max_tokens=4096,
            temperature=1.0,
        )
        parsed["plan_id"] = f"ai-{uuid.uuid4().hex[:8]}"
        parsed["settings_id"] = settings.settings_id
        parsed["pattern_id"] = None
        parsed["source"] = AttackPlanSource.AI_GENERATED.value
        parsed["created_at"] = _now()
        if "tags" not in parsed:
            parsed["tags"] = []
        parsed["tags"].append("ai_generated")
        return AttackPlan.from_dict(parsed)


# =======================================================================
# Defense playbook generator
# =======================================================================

class DefensePlaybookGenerator:
    def __init__(self, agent: LLMAgentPort) -> None:
        self._agent = agent

    async def generate(
        self,
        settings: Settings,
        doctrine: list[DoctrineEntry],
        similar_cases: list[MatchResult],
        extra_prompt: str = "",
    ) -> DefensePlaybook:
        context = _settings_context(settings)
        doctrine_block = _doctrine_context(doctrine)
        cases_block = _cases_context(similar_cases)
        user_msg = f"""Settings context:
{context}

Current doctrine:
{doctrine_block}

Relevant past cases:
{cases_block}

{extra_prompt}

Produce a defense playbook JSON matching the schema. Ground the playbook in the doctrine
above, learning from past cases. Be specific about standing orders and triggers."""

        parsed, _resp = await self._agent.call_json(
            system_prompt=DEFENSE_PLAYBOOK_GENERATOR_SYSTEM,
            messages=[LLMMessage(role="user", content=user_msg)],
            max_tokens=4096,
            temperature=1.0,
        )
        parsed["playbook_id"] = f"pbk-{uuid.uuid4().hex[:8]}"
        parsed["settings_id"] = settings.settings_id
        parsed["source"] = PlaybookSource.AI_GENERATED.value
        parsed["created_at"] = _now()
        return DefensePlaybook.from_dict(parsed)


# =======================================================================
# Match analyzer
# =======================================================================

class MatchAnalyzer:
    def __init__(self, agent: LLMAgentPort) -> None:
        self._agent = agent

    async def analyze(
        self,
        match: MatchResult,
        attack_plan_name: str,
        playbook_name: str,
    ) -> tuple[str, list[AITakeaway]]:
        # Summarize event log to stay within token budget
        significant_events = _filter_significant_events(match.event_log)

        user_msg = f"""Match outcome: {match.outcome.value}
Fitness score: {match.fitness_score:.2f}
Attack plan: {attack_plan_name}
Defense playbook: {playbook_name}

Metrics:
{json.dumps(match.metrics.to_dict(), indent=2)}

Significant events (filtered from full log, {len(significant_events)} of {_event_count(match.event_log)} total):
{json.dumps(significant_events, indent=2, default=str)[:30000]}

Analyze why this outcome occurred and extract 2-5 structured takeaways."""

        parsed, _resp = await self._agent.call_json(
            system_prompt=MATCH_ANALYZER_SYSTEM,
            messages=[LLMMessage(role="user", content=user_msg)],
            max_tokens=3000,
            temperature=0.7,
        )
        analysis = parsed.get("analysis", "")
        takeaways = [AITakeaway.from_dict(t) for t in parsed.get("takeaways", [])]
        return analysis, takeaways


# =======================================================================
# Doctrine synthesizer
# =======================================================================

class DoctrineSynthesizer:
    def __init__(self, agent: LLMAgentPort) -> None:
        self._agent = agent

    async def synthesize(
        self,
        settings_id: str,
        existing_doctrine: list[DoctrineEntry],
        recent_takeaways: list[tuple[str, AITakeaway]],  # (match_id, takeaway)
    ) -> dict:
        """
        Returns dict with 'additions' (new entries), 'reinforcements' (updates),
        'supersessions' (version bumps).
        """
        existing_block = _doctrine_context(existing_doctrine)
        takeaways_block = json.dumps(
            [
                {"match_id": mid, **t.to_dict()}
                for mid, t in recent_takeaways
            ],
            indent=2,
        )[:20000]

        user_msg = f"""Existing doctrine:
{existing_block}

Recent match takeaways:
{takeaways_block}

Decide doctrine updates per the output schema."""

        parsed, _resp = await self._agent.call_json(
            system_prompt=DOCTRINE_SYNTHESIZER_SYSTEM,
            messages=[LLMMessage(role="user", content=user_msg)],
            max_tokens=3000,
            temperature=0.6,
        )
        return parsed


# =======================================================================
# Context builders
# =======================================================================

def _settings_context(settings: Settings) -> str:
    bases_n = settings.scenario.get("bases", {}).get("north", [])
    bases_s = settings.scenario.get("bases", {}).get("south", [])
    cities_n = settings.scenario.get("cities", {}).get("north", [])
    cities_s = settings.scenario.get("cities", {}).get("south", [])

    def _fmt_base(b):
        return f"  - {b['id']} ({b.get('archetype', 'air_base')}): pos {b['position']}, capacity {b.get('max_aircraft_capacity', 12)}"

    def _fmt_city(c):
        cap = " CAPITAL" if c.get("is_capital") else ""
        return f"  - {c['id']}{cap}: pos {c['position']}, population {c.get('population', 0):,}"

    attacker_res = "\n".join(
        f"  {b}: " + ", ".join(f"{c} {t}" for t, c in types.items())
        for b, types in settings.attacker_resources.items()
    )
    defender_res = "\n".join(
        f"  {b}: " + ", ".join(f"{c} {t}" for t, c in types.items())
        for b, types in settings.defender_resources.items()
    )

    return f"""Settings: {settings.name}

NORTH (defender) bases:
{chr(10).join(_fmt_base(b) for b in bases_n)}

NORTH defender resources:
{defender_res}

NORTH cities:
{chr(10).join(_fmt_city(c) for c in cities_n)}

SOUTH (attacker) bases:
{chr(10).join(_fmt_base(b) for b in bases_s)}

SOUTH attacker resources:
{attacker_res}

SOUTH cities:
{chr(10).join(_fmt_city(c) for c in cities_s)}

Tick = {settings.tick_minutes} minutes. Max ticks = {settings.max_ticks}.
"""


def _doctrine_context(doctrine: list[DoctrineEntry]) -> str:
    if not doctrine:
        return "  (doctrine is currently empty — this is the first training run)"
    return "\n".join(
        f"  [{d.category}] {d.principle_text} (confidence: {d.confidence_score:.2f})"
        for d in doctrine
    )


def _cases_context(cases: list[MatchResult]) -> str:
    if not cases:
        return "  (no relevant cases found)"
    parts = []
    for c in cases[:5]:
        parts.append(
            f"  - Match {c.match_id}: outcome={c.outcome.value}, fitness={c.fitness_score:.1f}\n"
            f"    Analysis: {c.ai_analysis_text[:300] if c.ai_analysis_text else '(not analyzed)'}\n"
            f"    Takeaways: {'; '.join(t.principle for t in c.ai_takeaways[:3])}"
        )
    return "\n".join(parts)


def _filter_significant_events(event_log: list[dict]) -> list[dict]:
    """Reduce event log to significant events only (for token budget)."""
    significant_types = {
        "simulation_started",
        "simulation_ended",
        "launch",
        "engagement",
        "aircraft_destroyed",
        "pilot_reflex",
        "weapons_delivered",
        "civilian_casualties",
        "location_destroyed",
        "launch_disabled",
        "playbook_trigger_fired",
        "llm_command",
    }

    out: list[dict] = []
    for tick_snap in event_log:
        events_in_tick = tick_snap.get("events", [])
        for ev in events_in_tick:
            if ev.get("type") in significant_types:
                out.append(ev)
    return out[:300]   # cap to 300 to stay in token budget


def _event_count(event_log: list[dict]) -> int:
    return sum(len(t.get("events", [])) for t in event_log)

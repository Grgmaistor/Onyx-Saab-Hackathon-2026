from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum

from .metrics import SimulationMetrics


class SimulationOutcome(str, Enum):
    WIN = "WIN"
    LOSS = "LOSS"
    TIMEOUT = "TIMEOUT"
    UNDECIDED = "UNDECIDED"


@dataclass
class AITakeaway:
    """Structured observation extracted by the analyzer LLM."""
    principle: str                # natural-language lesson
    confidence: float             # 0.0 to 1.0
    tags: list[str]               # ["multi_wave", "bomber_defense"]
    supporting_tick_refs: list[int] = field(default_factory=list)   # which ticks show this

    def to_dict(self) -> dict:
        return {
            "principle": self.principle,
            "confidence": self.confidence,
            "tags": self.tags,
            "supporting_tick_refs": self.supporting_tick_refs,
        }

    @staticmethod
    def from_dict(data: dict) -> "AITakeaway":
        return AITakeaway(
            principle=data.get("principle", ""),
            confidence=data.get("confidence", 0.5),
            tags=data.get("tags", []),
            supporting_tick_refs=data.get("supporting_tick_refs", []),
        )


@dataclass
class MatchResult:
    """
    One row in the case library: a specific (attack, defense, settings) triple's
    deterministic outcome plus the LLM's analysis.

    match_id is deterministic: re-running the same triple overwrites the row
    via INSERT OR REPLACE. No duplicates possible.
    """
    match_id: str
    settings_id: str
    attack_plan_id: str
    pattern_id: str
    defense_playbook_id: str
    outcome: SimulationOutcome
    fitness_score: float
    metrics: SimulationMetrics
    event_log: list[dict]                    # full simulation events (structured)
    ai_analysis_text: str = ""               # narrative from match analyzer LLM
    ai_takeaways: list[AITakeaway] = field(default_factory=list)
    created_at: str = ""
    analysis_completed_at: str | None = None

    @staticmethod
    def compute_id(attack_plan_id: str, defense_playbook_id: str, settings_id: str) -> str:
        key = f"{attack_plan_id}|{defense_playbook_id}|{settings_id}"
        return "mtc-" + hashlib.sha256(key.encode()).hexdigest()[:16]

    def to_dict(self) -> dict:
        return {
            "match_id": self.match_id,
            "settings_id": self.settings_id,
            "attack_plan_id": self.attack_plan_id,
            "pattern_id": self.pattern_id,
            "defense_playbook_id": self.defense_playbook_id,
            "outcome": self.outcome.value,
            "fitness_score": self.fitness_score,
            "metrics": self.metrics.to_dict(),
            "event_log": self.event_log,
            "ai_analysis_text": self.ai_analysis_text,
            "ai_takeaways": [t.to_dict() for t in self.ai_takeaways],
            "created_at": self.created_at,
            "analysis_completed_at": self.analysis_completed_at,
        }

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class Settings:
    """
    Root scope for all training data. Two identical Settings produce the
    same settings_id (content-addressable dedup).

    All match_results, attack_patterns, defense_playbooks, and doctrine_entries
    reference a settings_id. Training data never crosses settings boundaries.
    """
    settings_id: str
    name: str
    scenario: dict                 # map geometry, bases, cities
    defender_resources: dict       # per-type, per-base aircraft counts
    attacker_resources: dict
    engagement_params: dict        # detection_range_km, base Pk values, etc.
    tick_minutes: float
    max_ticks: int
    created_at: str
    notes: str = ""

    @staticmethod
    def compute_id(
        scenario: dict,
        defender_resources: dict,
        attacker_resources: dict,
        engagement_params: dict,
        tick_minutes: float,
        max_ticks: int,
    ) -> str:
        """Deterministic hash of settings content."""
        canonical = json.dumps(
            {
                "scenario": scenario,
                "defender_resources": defender_resources,
                "attacker_resources": attacker_resources,
                "engagement_params": engagement_params,
                "tick_minutes": tick_minutes,
                "max_ticks": max_ticks,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return "set-" + hashlib.sha256(canonical.encode()).hexdigest()[:16]

    def to_dict(self) -> dict:
        return {
            "settings_id": self.settings_id,
            "name": self.name,
            "scenario": self.scenario,
            "defender_resources": self.defender_resources,
            "attacker_resources": self.attacker_resources,
            "engagement_params": self.engagement_params,
            "tick_minutes": self.tick_minutes,
            "max_ticks": self.max_ticks,
            "created_at": self.created_at,
            "notes": self.notes,
        }

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field


@dataclass
class AttackPattern:
    """
    Fuzzy tactical grouping of similar attack plans. Multiple plans can share
    one pattern. Pattern features are extracted deterministically so identical
    tactical shapes collapse to the same pattern_id.
    """
    pattern_id: str
    settings_id: str
    canonical_description: str
    feature_tags: list[str]
    force_composition: dict[str, int]   # {"bombers": 4, "drones": 8, ...}
    target_profile: str                 # "capital_primary" | "city_distributed" | etc
    wave_count: int
    first_seen_at: str

    # Mutable champion pointer (managed by repo on match insert)
    total_plans_count: int = 0
    total_matches_count: int = 0
    best_defense_playbook_id: str | None = None
    best_fitness_score: float | None = None
    best_match_id: str | None = None

    @staticmethod
    def compute_id(
        settings_id: str,
        feature_tags: list[str],
        force_composition: dict[str, int],
        target_profile: str,
        wave_count: int,
    ) -> str:
        canonical = json.dumps(
            {
                "settings_id": settings_id,
                "tags": sorted(feature_tags),
                "forces": {k: v for k, v in sorted(force_composition.items())},
                "target_profile": target_profile,
                "waves": wave_count,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return "ptn-" + hashlib.sha256(canonical.encode()).hexdigest()[:12]

    def to_dict(self) -> dict:
        return {
            "pattern_id": self.pattern_id,
            "settings_id": self.settings_id,
            "canonical_description": self.canonical_description,
            "feature_tags": self.feature_tags,
            "force_composition": self.force_composition,
            "target_profile": self.target_profile,
            "wave_count": self.wave_count,
            "first_seen_at": self.first_seen_at,
            "total_plans_count": self.total_plans_count,
            "total_matches_count": self.total_matches_count,
            "best_defense_playbook_id": self.best_defense_playbook_id,
            "best_fitness_score": self.best_fitness_score,
            "best_match_id": self.best_match_id,
        }

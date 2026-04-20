from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class EngagementOutcome(str, Enum):
    """Possible outcomes per aircraft in a multi-step BVR exchange."""
    HARD_KILL = "hard_kill"             # destroyed
    MISSION_KILL = "mission_kill"       # flyable but combat-ineffective, RTB
    DAMAGED_RTB = "damaged_rtb"         # damaged, flyable, RTB for repair
    LIGHT_DAMAGE = "light_damage"       # minor, may continue mission
    EVADED = "evaded"                   # missile miss
    DISENGAGED = "disengaged"           # broke off voluntarily
    DETERRED = "deterred"               # turned back before shots fired
    NO_ENGAGEMENT = "no_engagement"     # detected but ROE/range prevented fight


class DamageLevel(str, Enum):
    NONE = "none"
    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"
    DESTROYED = "destroyed"


@dataclass(frozen=True)
class DamageState:
    level: DamageLevel
    speed_reduction: float = 0.0        # 0.0 to 0.5 (fraction of speed lost)
    weapons_operational: bool = True
    repair_time_minutes: float = 0.0


@dataclass(frozen=True)
class EngagementResult:
    """Result of a single multi-step BVR exchange between two aircraft."""
    engagement_id: str
    tick: int
    attacker_id: str
    defender_id: str
    attacker_outcome: EngagementOutcome
    defender_outcome: EngagementOutcome
    attacker_damage: DamageLevel
    defender_damage: DamageLevel
    missiles_fired_attacker: int
    missiles_fired_defender: int
    rounds_fought: int
    collateral_damage: float = 0.0

    def to_dict(self) -> dict:
        return {
            "engagement_id": self.engagement_id,
            "tick": self.tick,
            "attacker_id": self.attacker_id,
            "defender_id": self.defender_id,
            "attacker_outcome": self.attacker_outcome.value,
            "defender_outcome": self.defender_outcome.value,
            "attacker_damage": self.attacker_damage.value,
            "defender_damage": self.defender_damage.value,
            "missiles_fired_attacker": self.missiles_fired_attacker,
            "missiles_fired_defender": self.missiles_fired_defender,
            "rounds_fought": self.rounds_fought,
            "collateral_damage": self.collateral_damage,
        }


@dataclass(frozen=True)
class EngagementParams:
    """Tunable parameters for the multi-step engagement engine."""
    pk_optimal_range: float = 0.45
    pk_max_range: float = 0.15
    pk_wvr: float = 0.65
    missiles_per_salvo: int = 2
    max_rounds: int = 3
    cm_effectiveness: float = 0.15
    ecm_effectiveness: float = 0.20
    maneuver_effectiveness: float = 0.10
    p_hard_kill: float = 0.25
    p_mission_kill: float = 0.35
    p_damage_rtb: float = 0.30
    p_light_damage: float = 0.10
    light_repair_minutes: float = 240.0
    moderate_repair_minutes: float = 1440.0
    heavy_repair_minutes: float = 7200.0
    fuel_disengage_threshold: float = 0.20
    ammo_disengage_threshold: int = 0

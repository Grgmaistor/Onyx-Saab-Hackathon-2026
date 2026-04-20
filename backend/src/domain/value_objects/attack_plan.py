from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AttackActionType(str, Enum):
    LAUNCH = "launch"
    RTB = "rtb"
    PATROL = "patrol"
    INTERCEPT_ZONE = "intercept_zone"
    REGROUP = "regroup"
    HOLD = "hold"


class AttackPlanSource(str, Enum):
    CUSTOM = "custom"
    RANDOM = "random"
    AI_GENERATED = "ai_generated"


@dataclass(frozen=True)
class AttackTarget:
    type: str                      # "city" | "base" | "position" | "nearest_base"
    id: str | None = None
    x_km: float | None = None
    y_km: float | None = None


@dataclass(frozen=True)
class AbortConditions:
    """Per-action tuning of pilot reflex abort behavior."""
    p_success_threshold: float = 0.35
    jettison_weapons_on_abort: bool = True


@dataclass(frozen=True)
class AttackAction:
    tick: int
    type: AttackActionType
    aircraft_type: str             # "bomber" | "combat_plane" | "uav" | "drone_swarm" | "all"
    count: int = 0                 # 0 means all available of this type
    from_base: str | None = None
    target: AttackTarget | None = None
    abort_conditions: AbortConditions = field(default_factory=AbortConditions)


@dataclass
class AttackPlan:
    """
    Scripted adversary actions over time. Attacker controls tempo;
    plan is mostly a timeline. Abort conditions modulate Layer 2 reflexes.
    """
    plan_id: str
    settings_id: str
    pattern_id: str | None         # assigned after PatternExtractor runs
    name: str
    description: str
    source: AttackPlanSource
    actions: list[AttackAction]
    tags: list[str] = field(default_factory=list)
    created_at: str = ""

    def to_dict(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "settings_id": self.settings_id,
            "pattern_id": self.pattern_id,
            "name": self.name,
            "description": self.description,
            "source": self.source.value,
            "created_at": self.created_at,
            "tags": self.tags,
            "actions": [
                {
                    "tick": a.tick,
                    "type": a.type.value,
                    "aircraft_type": a.aircraft_type,
                    "count": a.count,
                    "from_base": a.from_base,
                    "target": (
                        {
                            "type": a.target.type,
                            "id": a.target.id,
                            "x_km": a.target.x_km,
                            "y_km": a.target.y_km,
                        }
                        if a.target
                        else None
                    ),
                    "abort_conditions": {
                        "p_success_threshold": a.abort_conditions.p_success_threshold,
                        "jettison_weapons_on_abort": a.abort_conditions.jettison_weapons_on_abort,
                    },
                }
                for a in self.actions
            ],
        }

    @staticmethod
    def from_dict(data: dict) -> "AttackPlan":
        actions: list[AttackAction] = []
        for a in data.get("actions", []):
            target = None
            if a.get("target"):
                t = a["target"]
                target = AttackTarget(
                    type=t.get("type", "position"),
                    id=t.get("id"),
                    x_km=t.get("x_km"),
                    y_km=t.get("y_km"),
                )
            ab = a.get("abort_conditions", {})
            actions.append(
                AttackAction(
                    tick=a["tick"],
                    type=AttackActionType(a["type"]),
                    aircraft_type=a.get("aircraft_type", "all"),
                    count=a.get("count", 0),
                    from_base=a.get("from_base"),
                    target=target,
                    abort_conditions=AbortConditions(
                        p_success_threshold=ab.get("p_success_threshold", 0.35),
                        jettison_weapons_on_abort=ab.get("jettison_weapons_on_abort", True),
                    ),
                )
            )
        return AttackPlan(
            plan_id=data.get("plan_id") or data.get("id", ""),
            settings_id=data.get("settings_id", ""),
            pattern_id=data.get("pattern_id"),
            name=data.get("name", "Unnamed"),
            description=data.get("description", ""),
            source=AttackPlanSource(data.get("source", "custom")),
            actions=sorted(actions, key=lambda x: x.tick),
            tags=data.get("tags", []),
            created_at=data.get("created_at", ""),
        )

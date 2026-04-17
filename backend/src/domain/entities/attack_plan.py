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


@dataclass
class AttackTarget:
    type: str          # "city", "base", "position", "nearest_base"
    id: str | None = None
    x_km: float | None = None
    y_km: float | None = None


@dataclass
class AttackAction:
    tick: int
    type: AttackActionType
    aircraft_type: str         # "bomber", "combat_plane", "uav", "drone_swarm", "all"
    count: int = 0             # 0 means "all available of this type"
    from_base: str | None = None
    target: AttackTarget | None = None


@dataclass
class AttackPlan:
    id: str
    name: str
    source: AttackPlanSource
    description: str
    actions: list[AttackAction]
    created_at: str = ""
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "source": self.source.value,
            "description": self.description,
            "created_at": self.created_at,
            "tags": self.tags,
            "actions": [
                {
                    "tick": a.tick,
                    "type": a.type.value,
                    "aircraft_type": a.aircraft_type,
                    "count": a.count,
                    "from_base": a.from_base,
                    "target": {
                        "type": a.target.type,
                        "id": a.target.id,
                        "x_km": a.target.x_km,
                        "y_km": a.target.y_km,
                    } if a.target else None,
                }
                for a in self.actions
            ],
        }

    @staticmethod
    def from_dict(data: dict) -> "AttackPlan":
        actions = []
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
            actions.append(AttackAction(
                tick=a["tick"],
                type=AttackActionType(a["type"]),
                aircraft_type=a.get("aircraft_type", "all"),
                count=a.get("count", 0),
                from_base=a.get("from_base"),
                target=target,
            ))
        return AttackPlan(
            id=data.get("id", ""),
            name=data.get("name", "Unnamed"),
            source=AttackPlanSource(data.get("source", "custom")),
            description=data.get("description", ""),
            actions=sorted(actions, key=lambda x: x.tick),
            created_at=data.get("created_at", ""),
            tags=data.get("tags", []),
        )

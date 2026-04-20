from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class PlaybookSource(str, Enum):
    AI_GENERATED = "ai_generated"
    CUSTOM = "custom"
    COACHED = "coached"   # produced during a coach iteration after reflection


# ==== Standing Orders ====

@dataclass(frozen=True)
class StandingOrder:
    """
    A long-running assignment like 'keep 2-ship CAP over capital'.
    Runs every tick; simulation tries to maintain the specified posture.
    """
    name: str
    type: str                       # "patrol" | "ready_alert" | "defensive_line"
    aircraft_type: str              # "combat_plane" | "uav" | "any"
    count: int                      # number of aircraft to dedicate
    zone: dict                      # {"type":"circle","center":"arktholm","radius_km":80}
                                    # or {"type":"line","from":[x,y],"to":[x,y]}
                                    # or {"type":"point","position":[x,y]}
    base: str | None = None         # which base to draw from (optional)
    rotation_fuel_threshold: float = 0.35  # swap out at this fuel fraction
    priority: int = 0                       # higher = maintained first under scarcity


# ==== Triggers (reactive rules) ====

@dataclass(frozen=True)
class Trigger:
    """
    A conditional rule fired every tick based on state.
    Condition DSL is simple: string key with parameters.
    """
    name: str
    when: dict                      # {"condition": "bomber_detected_within_km_of_asset",
                                    #  "threshold_km": 400,
                                    #  "asset_type": ["capital", "city"]}
    action: dict                    # {"type":"scramble_intercept","count":3,"from":"nearest"}
    priority: int = 0               # higher fires first
    cooldown_ticks: int = 0         # min ticks between firings


# ==== Constraints (hard limits) ====

@dataclass(frozen=True)
class Constraints:
    reserve_fraction: float = 0.30              # always keep N% grounded
    never_leave_capital_uncovered: bool = True
    max_commit_from_base_fraction: float = 0.70 # don't drain one base
    min_fuel_to_launch_fraction: float = 0.40


# ==== Full Playbook ====

@dataclass
class DefensePlaybook:
    """
    The defender's 'brain'. Not a timeline — a reactive ruleset.
    Executed deterministically by PlaybookExecutor each tick.
    """
    playbook_id: str
    settings_id: str
    name: str
    description: str
    source: PlaybookSource
    standing_orders: list[StandingOrder]
    triggers: list[Trigger]
    constraints: Constraints
    doctrine_notes: str = ""
    parent_playbook_id: str | None = None       # lineage for coached versions
    created_at: str = ""

    def to_dict(self) -> dict:
        return {
            "playbook_id": self.playbook_id,
            "settings_id": self.settings_id,
            "name": self.name,
            "description": self.description,
            "source": self.source.value,
            "standing_orders": [
                {
                    "name": o.name,
                    "type": o.type,
                    "aircraft_type": o.aircraft_type,
                    "count": o.count,
                    "zone": o.zone,
                    "base": o.base,
                    "rotation_fuel_threshold": o.rotation_fuel_threshold,
                    "priority": o.priority,
                }
                for o in self.standing_orders
            ],
            "triggers": [
                {
                    "name": t.name,
                    "when": t.when,
                    "action": t.action,
                    "priority": t.priority,
                    "cooldown_ticks": t.cooldown_ticks,
                }
                for t in self.triggers
            ],
            "constraints": {
                "reserve_fraction": self.constraints.reserve_fraction,
                "never_leave_capital_uncovered": self.constraints.never_leave_capital_uncovered,
                "max_commit_from_base_fraction": self.constraints.max_commit_from_base_fraction,
                "min_fuel_to_launch_fraction": self.constraints.min_fuel_to_launch_fraction,
            },
            "doctrine_notes": self.doctrine_notes,
            "parent_playbook_id": self.parent_playbook_id,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_dict(data: dict) -> "DefensePlaybook":
        orders = [
            StandingOrder(
                name=o["name"],
                type=o["type"],
                aircraft_type=o.get("aircraft_type", "any"),
                count=o.get("count", 2),
                zone=o.get("zone", {}),
                base=o.get("base"),
                rotation_fuel_threshold=o.get("rotation_fuel_threshold", 0.35),
                priority=o.get("priority", 0),
            )
            for o in data.get("standing_orders", [])
        ]
        triggers = [
            Trigger(
                name=t["name"],
                when=t.get("when", {}),
                action=t.get("action", {}),
                priority=t.get("priority", 0),
                cooldown_ticks=t.get("cooldown_ticks", 0),
            )
            for t in data.get("triggers", [])
        ]
        c = data.get("constraints", {})
        constraints = Constraints(
            reserve_fraction=c.get("reserve_fraction", 0.30),
            never_leave_capital_uncovered=c.get("never_leave_capital_uncovered", True),
            max_commit_from_base_fraction=c.get("max_commit_from_base_fraction", 0.70),
            min_fuel_to_launch_fraction=c.get("min_fuel_to_launch_fraction", 0.40),
        )
        return DefensePlaybook(
            playbook_id=data.get("playbook_id") or data.get("id", ""),
            settings_id=data.get("settings_id", ""),
            name=data.get("name", "Unnamed"),
            description=data.get("description", ""),
            source=PlaybookSource(data.get("source", "custom")),
            standing_orders=orders,
            triggers=triggers,
            constraints=constraints,
            doctrine_notes=data.get("doctrine_notes", ""),
            parent_playbook_id=data.get("parent_playbook_id"),
            created_at=data.get("created_at", ""),
        )

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class EventType(str, Enum):
    # Aircraft lifecycle
    LAUNCH = "launch"
    RTB = "rtb"
    LANDED = "landed"
    REFUEL_COMPLETE = "refuel_complete"
    REARM_COMPLETE = "rearm_complete"
    REPAIR_COMPLETE = "repair_complete"

    # Combat
    ENGAGEMENT = "engagement"
    MISSILE_FIRED = "missile_fired"
    HIT = "hit"
    MISS = "miss"
    AIRCRAFT_DESTROYED = "aircraft_destroyed"
    AIRCRAFT_DAMAGED = "aircraft_damaged"

    # Strike on ground target
    WEAPONS_DELIVERED = "weapons_delivered"
    CIVILIAN_CASUALTIES = "civilian_casualties"
    PARKED_AIRCRAFT_DESTROYED = "parked_aircraft_destroyed"
    LAUNCH_CAPACITY_REDUCED = "launch_capacity_reduced"
    REFUEL_RATE_REDUCED = "refuel_rate_reduced"
    LAUNCH_DISABLED = "launch_disabled"
    LOCATION_DESTROYED = "location_destroyed"
    CASUALTY_MULTIPLIER_INCREASED = "casualty_multiplier_increased"

    # Pilot reflexes
    PILOT_REFLEX = "pilot_reflex"

    # Command layer
    PLAYBOOK_TRIGGER_FIRED = "playbook_trigger_fired"
    STANDING_ORDER_MAINTAINED = "standing_order_maintained"
    LLM_COMMAND = "llm_command"
    LLM_PLAYBOOK_PATCH = "llm_playbook_patch"

    # Detection
    THREAT_DETECTED = "threat_detected"

    # Meta
    SIMULATION_STARTED = "simulation_started"
    SIMULATION_ENDED = "simulation_ended"


@dataclass
class Event:
    """
    Structured event log entry. Preferred over plain strings so the LLM
    analyzer can reason about patterns across ticks.
    """
    type: EventType
    tick: int
    payload: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "type": self.type.value,
            "tick": self.tick,
            **self.payload,
        }

    @staticmethod
    def from_dict(data: dict) -> "Event":
        t = data.get("type", "")
        payload = {k: v for k, v in data.items() if k not in ("type", "tick")}
        return Event(
            type=EventType(t) if t in EventType._value2member_map_ else EventType.LLM_COMMAND,
            tick=data.get("tick", 0),
            payload=payload,
        )

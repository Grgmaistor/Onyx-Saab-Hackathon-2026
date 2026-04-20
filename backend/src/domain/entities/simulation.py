from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .aircraft import Aircraft, Side
from .location import Location


class SimulationStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SimulationState:
    """Full world state at a given tick; what the playbook/LLM sees."""
    tick: int
    friendly_aircraft: list[Aircraft]
    enemy_aircraft: list[Aircraft]
    friendly_bases: list[Location]              # air_base / forward_base archetypes
    enemy_bases: list[Location]
    friendly_cities: list[Location]             # capital / major_city archetypes
    enemy_cities: list[Location]
    detected_threats: list[Aircraft] = field(default_factory=list)

    @property
    def all_aircraft(self) -> list[Aircraft]:
        return self.friendly_aircraft + self.enemy_aircraft

    @property
    def friendly_locations(self) -> list[Location]:
        return self.friendly_bases + self.friendly_cities

    @property
    def enemy_locations(self) -> list[Location]:
        return self.enemy_bases + self.enemy_cities


@dataclass
class SimulationTick:
    """One tick's snapshot for the replay log."""
    tick: int
    aircraft_states: list[dict]
    location_states: list[dict]           # bases + cities
    events: list[dict]                    # structured events (Event.to_dict())

    def to_dict(self) -> dict:
        return {
            "tick": self.tick,
            "aircraft": self.aircraft_states,
            "locations": self.location_states,
            "events": self.events,
        }


@dataclass
class SimulationConfig:
    """What a single simulation run needs to execute."""
    settings_id: str
    attack_plan_id: str
    defense_playbook_id: str
    defender_side: Side                   # which side is being defended
    live_commander_enabled: bool = False  # if True, LLM is called per tick

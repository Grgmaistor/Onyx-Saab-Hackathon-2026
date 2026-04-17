from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .aircraft import Aircraft, Side
from .base import Base
from .battle import Battle
from .city import City
from ..value_objects.metrics import SimulationMetrics


class SimulationStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SimulationOutcome(str, Enum):
    WIN = "WIN"
    LOSS = "LOSS"
    TIMEOUT = "TIMEOUT"
    UNDECIDED = "UNDECIDED"


@dataclass
class SimulationState:
    tick: int
    friendly_aircraft: list[Aircraft]
    enemy_aircraft: list[Aircraft]
    friendly_bases: list[Base]
    enemy_bases: list[Base]
    friendly_cities: list[City]
    enemy_cities: list[City]
    active_battles: list[Battle]
    detected_threats: list[Aircraft] = field(default_factory=list)

    @property
    def all_aircraft(self) -> list[Aircraft]:
        return self.friendly_aircraft + self.enemy_aircraft

    @property
    def all_bases(self) -> list[Base]:
        return self.friendly_bases + self.enemy_bases


@dataclass
class SimulationTick:
    tick: int
    aircraft_states: list[dict]
    base_states: list[dict]
    city_states: list[dict]
    battles: list[dict]
    decisions_made: list[dict]
    events: list[str]


@dataclass
class SimulationConfig:
    scenario_id: str
    strategy_id: str
    enemy_strategy_id: str
    side: Side
    seed: int
    max_ticks: int = 1000
    tick_minutes: float = 5.0
    detection_range_km: float = 200.0
    engagement_range_km: float = 50.0


@dataclass
class SimulationResult:
    simulation_id: str
    batch_id: str | None
    config: SimulationConfig
    outcome: SimulationOutcome
    total_ticks: int
    event_log: list[SimulationTick]
    metrics: SimulationMetrics | None = None

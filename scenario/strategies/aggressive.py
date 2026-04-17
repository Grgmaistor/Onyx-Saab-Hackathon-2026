from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

from src.domain.ports.strategy import StrategyPort
from src.domain.entities.simulation import SimulationState
from src.domain.entities.aircraft import AircraftState, AircraftType
from src.domain.value_objects.decision import Decision, DecisionType


class AggressiveStrategy(StrategyPort):

    @property
    def name(self) -> str:
        return "aggressive_v1"

    @property
    def description(self) -> str:
        return "Launch everything. Target enemy bombers first. Push forward aggressively."

    def decide(self, state: SimulationState) -> list[Decision]:
        decisions: list[Decision] = []
        assigned: set[str] = set()

        # RTB only when critically low on fuel
        for ac in state.friendly_aircraft:
            if ac.state == AircraftState.AIRBORNE and ac.fuel_current < ac.fuel_capacity * 0.15:
                nearest = min(state.friendly_bases, key=lambda b: b.position.distance_to(ac.position))
                decisions.append(Decision(type=DecisionType.RTB, aircraft_id=ac.id, target_id=nearest.id))
                assigned.add(ac.id)

        # Target bombers first, then any threat
        bombers = [t for t in state.detected_threats if t.type == AircraftType.BOMBER]
        others = [t for t in state.detected_threats if t.type != AircraftType.BOMBER]
        priority_threats = bombers + others

        available = [a for a in state.friendly_aircraft
                     if a.state in (AircraftState.GROUNDED, AircraftState.AIRBORNE)
                     and a.id not in assigned and a.ammo_current > 0]

        for threat in priority_threats:
            if not available:
                break
            interceptor = available.pop(0)
            decisions.append(Decision(type=DecisionType.INTERCEPT,
                                      aircraft_id=interceptor.id, target_id=threat.id))
            assigned.add(interceptor.id)

        # Launch all remaining grounded aircraft and push toward enemy territory
        enemy_center_y = 1100 if state.friendly_bases[0].side.value == "north" else 200
        push_position = state.friendly_bases[0].position.__class__(
            x_km=833, y_km=enemy_center_y)

        for ac in state.friendly_aircraft:
            if ac.state == AircraftState.GROUNDED and ac.id not in assigned:
                decisions.append(Decision(type=DecisionType.LAUNCH,
                                          aircraft_id=ac.id, position=push_position))
                assigned.add(ac.id)

        return decisions

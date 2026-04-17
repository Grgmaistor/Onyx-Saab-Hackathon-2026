from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

from src.domain.ports.strategy import StrategyPort
from src.domain.entities.simulation import SimulationState
from src.domain.entities.aircraft import AircraftState, AircraftType
from src.domain.value_objects.decision import Decision, DecisionType


class DefensiveStrategy(StrategyPort):

    @property
    def name(self) -> str:
        return "defensive_v1"

    @property
    def description(self) -> str:
        return "Protect capital and cities. Engage only approaching threats. Keep 40% reserves."

    def decide(self, state: SimulationState) -> list[Decision]:
        decisions: list[Decision] = []
        assigned: set[str] = set()

        available = [a for a in state.friendly_aircraft
                     if a.state in (AircraftState.GROUNDED, AircraftState.AIRBORNE)
                     and a.id not in assigned]

        # RTB low fuel aircraft first
        for ac in state.friendly_aircraft:
            if ac.state == AircraftState.AIRBORNE and ac.fuel_current < ac.fuel_capacity * 0.25:
                nearest_base = min(state.friendly_bases,
                                   key=lambda b: b.position.distance_to(ac.position))
                decisions.append(Decision(type=DecisionType.RTB, aircraft_id=ac.id,
                                          target_id=nearest_base.id))
                assigned.add(ac.id)

        # Keep reserves - only use 60% of available
        reserve_count = int(len(available) * 0.4)
        deployable = [a for a in available if a.id not in assigned]
        if len(deployable) <= reserve_count:
            return decisions

        # Intercept threats sorted by proximity to capital
        capitals = [c for c in state.friendly_cities if c.is_capital]
        capital_pos = capitals[0].position if capitals else state.friendly_bases[0].position

        threats = sorted(state.detected_threats,
                         key=lambda t: t.position.distance_to(capital_pos))

        for threat in threats:
            if not deployable:
                break
            # Prefer combat planes for interception
            interceptor = None
            for ac in deployable:
                if ac.type == AircraftType.COMBAT_PLANE and ac.id not in assigned:
                    interceptor = ac
                    break
            if not interceptor:
                for ac in deployable:
                    if ac.id not in assigned and ac.ammo_current > 0:
                        interceptor = ac
                        break
            if interceptor:
                decisions.append(Decision(type=DecisionType.INTERCEPT,
                                          aircraft_id=interceptor.id, target_id=threat.id))
                assigned.add(interceptor.id)
                deployable = [a for a in deployable if a.id not in assigned]

        # Patrol around capital if no threats
        if not threats:
            patrol_count = 0
            for ac in deployable:
                if patrol_count >= 2:
                    break
                if ac.state == AircraftState.GROUNDED and ac.id not in assigned:
                    decisions.append(Decision(type=DecisionType.PATROL,
                                              aircraft_id=ac.id, position=capital_pos))
                    assigned.add(ac.id)
                    patrol_count += 1

        return decisions

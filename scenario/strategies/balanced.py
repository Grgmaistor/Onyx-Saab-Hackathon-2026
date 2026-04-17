from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

from src.domain.ports.strategy import StrategyPort
from src.domain.entities.simulation import SimulationState
from src.domain.entities.aircraft import AircraftState, AircraftType
from src.domain.value_objects.decision import Decision, DecisionType
from src.domain.value_objects.position import Position


class BalancedStrategy(StrategyPort):

    @property
    def name(self) -> str:
        return "balanced_v1"

    @property
    def description(self) -> str:
        return "Maintain patrol zones, respond proportionally, keep 30% reserves, rotate aircraft."

    def decide(self, state: SimulationState) -> list[Decision]:
        decisions: list[Decision] = []
        assigned: set[str] = set()

        # RTB at 20% fuel
        for ac in state.friendly_aircraft:
            if ac.state == AircraftState.AIRBORNE and ac.fuel_current < ac.fuel_capacity * 0.20:
                nearest = min(state.friendly_bases, key=lambda b: b.position.distance_to(ac.position))
                decisions.append(Decision(type=DecisionType.RTB, aircraft_id=ac.id, target_id=nearest.id))
                assigned.add(ac.id)

        available = [a for a in state.friendly_aircraft
                     if a.state in (AircraftState.GROUNDED, AircraftState.AIRBORNE)
                     and a.id not in assigned and a.ammo_current > 0]

        # Keep 30% reserve
        reserve = int(len(available) * 0.3)
        deployable = available[:len(available) - reserve] if len(available) > reserve else available

        # Respond to threats proportionally
        for threat in state.detected_threats:
            if not deployable:
                break
            # Match type: send combat planes against combat planes, drones against drones
            best = None
            for ac in deployable:
                if ac.id in assigned:
                    continue
                if ac.type == threat.type or ac.type == AircraftType.COMBAT_PLANE:
                    best = ac
                    break
            if not best and deployable:
                best = next((a for a in deployable if a.id not in assigned), None)
            if best:
                decisions.append(Decision(type=DecisionType.INTERCEPT,
                                          aircraft_id=best.id, target_id=threat.id))
                assigned.add(best.id)
                deployable = [a for a in deployable if a.id not in assigned]

        # Set up patrol zones around key positions
        patrol_positions = []
        capitals = [c for c in state.friendly_cities if c.is_capital]
        if capitals:
            patrol_positions.append(capitals[0].position)
        for base in state.friendly_bases[:2]:
            patrol_positions.append(base.position)

        patrol_idx = 0
        for ac in deployable:
            if ac.id in assigned:
                continue
            if ac.state == AircraftState.GROUNDED and patrol_idx < len(patrol_positions):
                decisions.append(Decision(type=DecisionType.PATROL,
                                          aircraft_id=ac.id,
                                          position=patrol_positions[patrol_idx % len(patrol_positions)]))
                assigned.add(ac.id)
                patrol_idx += 1

        return decisions

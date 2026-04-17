"""Built-in strategies for the simulation engine."""
from __future__ import annotations

from src.domain.entities.aircraft import Aircraft, AircraftState, AircraftType
from src.domain.entities.base import Base
from src.domain.entities.simulation import SimulationState
from src.domain.ports.strategy import StrategyPort
from src.domain.value_objects.decision import Decision, DecisionType
from src.domain.value_objects.position import Position


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _nearest_available(aircraft: list[Aircraft], pos: Position, exclude: set[str]) -> Aircraft | None:
    best: Aircraft | None = None
    best_dist = float("inf")
    for ac in aircraft:
        if ac.id in exclude:
            continue
        if ac.state == AircraftState.AIRBORNE and ac.ammo_current > 0:
            d = ac.position.distance_to(pos)
            if d < best_dist:
                best_dist = d
                best = ac
    return best


def _nearest_grounded(aircraft: list[Aircraft], exclude: set[str]) -> Aircraft | None:
    for ac in aircraft:
        if ac.id in exclude:
            continue
        if ac.state == AircraftState.GROUNDED:
            return ac
    return None


def _nearest_base(bases: list[Base], pos: Position) -> Base | None:
    best: Base | None = None
    best_dist = float("inf")
    for b in bases:
        if not b.is_operational:
            continue
        d = b.position.distance_to(pos)
        if d < best_dist:
            best_dist = d
            best = b
    return best


# ---------------------------------------------------------------------------
# Defensive Strategy
# ---------------------------------------------------------------------------

class DefensiveStrategy(StrategyPort):
    @property
    def name(self) -> str:
        return "defensive_v1"

    @property
    def description(self) -> str:
        return "Protect capital and cities. Engage only approaching threats."

    def decide(self, state: SimulationState) -> list[Decision]:
        decisions: list[Decision] = []
        assigned: set[str] = set()

        # Launch some aircraft if we have grounded ones and there are threats
        if state.detected_threats:
            for _threat in state.detected_threats:
                grounded = _nearest_grounded(state.friendly_aircraft, assigned)
                if grounded:
                    decisions.append(Decision(
                        type=DecisionType.LAUNCH,
                        aircraft_id=grounded.id,
                    ))
                    assigned.add(grounded.id)

        # Intercept detected threats
        for threat in state.detected_threats:
            interceptor = _nearest_available(state.friendly_aircraft, threat.position, assigned)
            if interceptor:
                decisions.append(Decision(
                    type=DecisionType.INTERCEPT,
                    aircraft_id=interceptor.id,
                    target_id=threat.id,
                ))
                assigned.add(interceptor.id)

        # RTB low-fuel aircraft
        for ac in state.friendly_aircraft:
            if ac.id in assigned:
                continue
            if ac.state == AircraftState.AIRBORNE and ac.fuel_current < ac.fuel_capacity * 0.2:
                base = _nearest_base(state.friendly_bases, ac.position)
                if base:
                    decisions.append(Decision(
                        type=DecisionType.RTB,
                        aircraft_id=ac.id,
                        target_id=base.id,
                    ))
                    assigned.add(ac.id)

        return decisions


# ---------------------------------------------------------------------------
# Aggressive Strategy
# ---------------------------------------------------------------------------

class AggressiveStrategy(StrategyPort):
    @property
    def name(self) -> str:
        return "aggressive_v1"

    @property
    def description(self) -> str:
        return "Push forward, target enemy bases and bombers proactively."

    def decide(self, state: SimulationState) -> list[Decision]:
        decisions: list[Decision] = []
        assigned: set[str] = set()

        # Launch all grounded aircraft
        for ac in state.friendly_aircraft:
            if ac.state == AircraftState.GROUNDED and ac.id not in assigned:
                decisions.append(Decision(
                    type=DecisionType.LAUNCH,
                    aircraft_id=ac.id,
                ))
                assigned.add(ac.id)

        # Intercept any detected threats, prioritising bombers
        threats_sorted = sorted(
            state.detected_threats,
            key=lambda t: (0 if t.type == AircraftType.BOMBER else 1),
        )
        for threat in threats_sorted:
            interceptor = _nearest_available(state.friendly_aircraft, threat.position, assigned)
            if interceptor:
                decisions.append(Decision(
                    type=DecisionType.INTERCEPT,
                    aircraft_id=interceptor.id,
                    target_id=threat.id,
                ))
                assigned.add(interceptor.id)

        # Send unassigned bombers toward enemy cities
        for ac in state.friendly_aircraft:
            if ac.id in assigned:
                continue
            if ac.state == AircraftState.AIRBORNE and ac.type == AircraftType.BOMBER:
                if state.enemy_cities:
                    target_city = state.enemy_cities[0]
                    decisions.append(Decision(
                        type=DecisionType.PATROL,
                        aircraft_id=ac.id,
                        position=target_city.position,
                    ))
                    assigned.add(ac.id)

        # Send unassigned combat planes toward enemy bases
        for ac in state.friendly_aircraft:
            if ac.id in assigned:
                continue
            if ac.state == AircraftState.AIRBORNE and ac.type == AircraftType.COMBAT_PLANE:
                if state.enemy_bases:
                    target_base = state.enemy_bases[0]
                    decisions.append(Decision(
                        type=DecisionType.PATROL,
                        aircraft_id=ac.id,
                        position=target_base.position,
                    ))
                    assigned.add(ac.id)

        # RTB low-fuel
        for ac in state.friendly_aircraft:
            if ac.id in assigned:
                continue
            if ac.state == AircraftState.AIRBORNE and ac.fuel_current < ac.fuel_capacity * 0.15:
                base = _nearest_base(state.friendly_bases, ac.position)
                if base:
                    decisions.append(Decision(
                        type=DecisionType.RTB,
                        aircraft_id=ac.id,
                        target_id=base.id,
                    ))
                    assigned.add(ac.id)

        return decisions


# ---------------------------------------------------------------------------
# Balanced Strategy
# ---------------------------------------------------------------------------

class BalancedStrategy(StrategyPort):
    @property
    def name(self) -> str:
        return "balanced_v1"

    @property
    def description(self) -> str:
        return "Mix of patrol zones and responsive intercepts."

    def decide(self, state: SimulationState) -> list[Decision]:
        decisions: list[Decision] = []
        assigned: set[str] = set()

        # Launch aircraft if threats detected (up to half)
        if state.detected_threats:
            grounded = [
                a for a in state.friendly_aircraft
                if a.state == AircraftState.GROUNDED and a.id not in assigned
            ]
            to_launch = min(len(grounded), max(1, len(state.detected_threats)))
            for ac in grounded[:to_launch]:
                decisions.append(Decision(
                    type=DecisionType.LAUNCH,
                    aircraft_id=ac.id,
                ))
                assigned.add(ac.id)

        # Intercept threats
        for threat in state.detected_threats:
            interceptor = _nearest_available(state.friendly_aircraft, threat.position, assigned)
            if interceptor:
                decisions.append(Decision(
                    type=DecisionType.INTERCEPT,
                    aircraft_id=interceptor.id,
                    target_id=threat.id,
                ))
                assigned.add(interceptor.id)

        # Patrol unassigned airborne aircraft near friendly cities
        for ac in state.friendly_aircraft:
            if ac.id in assigned:
                continue
            if ac.state == AircraftState.AIRBORNE and ac.fuel_current > ac.fuel_capacity * 0.4:
                # Pick the nearest friendly city to patrol
                if state.friendly_cities:
                    closest_city = min(
                        state.friendly_cities,
                        key=lambda c: ac.position.distance_to(c.position),
                    )
                    decisions.append(Decision(
                        type=DecisionType.PATROL,
                        aircraft_id=ac.id,
                        position=closest_city.position,
                    ))
                    assigned.add(ac.id)

        # RTB low-fuel
        for ac in state.friendly_aircraft:
            if ac.id in assigned:
                continue
            if ac.state == AircraftState.AIRBORNE and ac.fuel_current < ac.fuel_capacity * 0.25:
                base = _nearest_base(state.friendly_bases, ac.position)
                if base:
                    decisions.append(Decision(
                        type=DecisionType.RTB,
                        aircraft_id=ac.id,
                        target_id=base.id,
                    ))
                    assigned.add(ac.id)

        return decisions

from __future__ import annotations

from ..entities.aircraft import AircraftState, AircraftType
from ..entities.attack_plan import AttackAction, AttackActionType, AttackPlan, AttackTarget
from ..entities.simulation import SimulationState
from ..ports.strategy import StrategyPort
from ..value_objects.decision import Decision, DecisionType
from ..value_objects.position import Position


# Map scenario target IDs to positions at runtime
def _resolve_target_position(target: AttackTarget | None, state: SimulationState) -> Position | None:
    if target is None:
        return None

    if target.type == "position" and target.x_km is not None and target.y_km is not None:
        return Position(target.x_km, target.y_km)

    if target.type == "city" and target.id:
        for city in state.enemy_cities:
            if city.id == target.id:
                return city.position
        # If not found in enemy cities, check friendly (attack plan sees "our" cities as enemy)
        for city in state.friendly_cities:
            if city.id == target.id:
                return city.position

    if target.type == "base" and target.id:
        for base in state.enemy_bases:
            if base.id == target.id:
                return base.position
        for base in state.friendly_bases:
            if base.id == target.id:
                return base.position

    return None


class AttackPlanStrategy(StrategyPort):
    """Executes a scripted attack plan. Actions fire at their designated tick.
    Between actions, aircraft continue current orders autonomously:
    - Fly toward target, engage if enemy in range
    - RTB when fuel < 15%
    """

    def __init__(self, plan: AttackPlan) -> None:
        self._plan = plan
        self._name = f"attack_plan:{plan.id}"

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._plan.description or f"Attack plan: {self._plan.name}"

    def decide(self, state: SimulationState) -> list[Decision]:
        decisions: list[Decision] = []
        assigned: set[str] = set()
        tick = state.tick

        # Auto RTB for critically low fuel (autonomous behavior between orders)
        for ac in state.friendly_aircraft:
            if ac.state == AircraftState.AIRBORNE and ac.fuel_current < ac.fuel_capacity * 0.15:
                nearest = min(state.friendly_bases,
                              key=lambda b: b.position.distance_to(ac.position))
                decisions.append(Decision(type=DecisionType.RTB,
                                          aircraft_id=ac.id, target_id=nearest.id))
                assigned.add(ac.id)

        # Auto intercept: airborne fighters engage detected threats
        for ac in state.friendly_aircraft:
            if (ac.state == AircraftState.AIRBORNE
                    and ac.id not in assigned
                    and ac.ammo_current > 0
                    and ac.type in (AircraftType.COMBAT_PLANE, AircraftType.UAV)):
                for threat in state.detected_threats:
                    if threat.position.distance_to(ac.position) < 100:
                        decisions.append(Decision(type=DecisionType.INTERCEPT,
                                                  aircraft_id=ac.id, target_id=threat.id))
                        assigned.add(ac.id)
                        break

        # Execute scripted actions for this tick
        tick_actions = [a for a in self._plan.actions if a.tick == tick]

        for action in tick_actions:
            target_pos = _resolve_target_position(action.target, state)

            # Find matching aircraft
            candidates = []
            for ac in state.friendly_aircraft:
                if ac.id in assigned or not ac.is_alive:
                    continue
                if action.aircraft_type != "all" and ac.type.value != action.aircraft_type:
                    continue
                if action.type == AttackActionType.LAUNCH and ac.state != AircraftState.GROUNDED:
                    continue
                if action.from_base and ac.assigned_base != action.from_base:
                    continue
                if action.type != AttackActionType.LAUNCH and ac.state not in (
                        AircraftState.GROUNDED, AircraftState.AIRBORNE):
                    continue
                candidates.append(ac)

            # Limit by count
            count = action.count if action.count > 0 else len(candidates)
            selected = candidates[:count]

            for ac in selected:
                if action.type == AttackActionType.LAUNCH:
                    decisions.append(Decision(
                        type=DecisionType.LAUNCH,
                        aircraft_id=ac.id,
                        position=target_pos,
                    ))
                elif action.type == AttackActionType.RTB:
                    base_id = None
                    if action.target and action.target.type == "nearest_base":
                        nearest = min(state.friendly_bases,
                                      key=lambda b: b.position.distance_to(ac.position))
                        base_id = nearest.id
                    elif action.target and action.target.id:
                        base_id = action.target.id
                    decisions.append(Decision(
                        type=DecisionType.RTB,
                        aircraft_id=ac.id,
                        target_id=base_id or ac.assigned_base,
                    ))
                elif action.type == AttackActionType.PATROL:
                    decisions.append(Decision(
                        type=DecisionType.PATROL,
                        aircraft_id=ac.id,
                        position=target_pos,
                    ))
                elif action.type == AttackActionType.INTERCEPT_ZONE:
                    decisions.append(Decision(
                        type=DecisionType.PATROL,
                        aircraft_id=ac.id,
                        position=target_pos,
                    ))
                elif action.type == AttackActionType.REGROUP:
                    decisions.append(Decision(
                        type=DecisionType.RTB,
                        aircraft_id=ac.id,
                        target_id=ac.assigned_base,
                    ))
                elif action.type == AttackActionType.HOLD:
                    decisions.append(Decision(
                        type=DecisionType.HOLD,
                        aircraft_id=ac.id,
                    ))
                assigned.add(ac.id)

        return decisions

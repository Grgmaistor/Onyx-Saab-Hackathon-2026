"""
Attack plan executor — Layer 3 attacker. Reads an AttackPlan (timeline of
actions) and emits Commands for the current tick.

Attackers control tempo, so their plan is mostly scheduled. Abort conditions
per action modulate Layer 2 pilot reflexes.
"""

from __future__ import annotations

from ..entities.aircraft import Aircraft, AircraftState, AircraftType
from ..entities.location import Location
from ..entities.simulation import SimulationState
from ..value_objects.attack_plan import (
    AttackAction,
    AttackActionType,
    AttackPlan,
    AttackTarget,
)
from ..value_objects.event import Event, EventType
from ..value_objects.position import Position
from .playbook_executor import Command


def execute_attack_plan(
    plan: AttackPlan,
    state: SimulationState,
    tick: int,
    already_tasked: set[str],
) -> tuple[list[Command], list[Event]]:
    """Execute any actions scheduled for this tick."""
    commands: list[Command] = []
    events: list[Event] = []

    tick_actions = [a for a in plan.actions if a.tick == tick]
    if not tick_actions:
        return commands, events

    for action in tick_actions:
        target_pos = _resolve_target_position(action.target, state)
        candidates = _select_candidates(action, state, already_tasked)

        count = action.count if action.count > 0 else len(candidates)
        selected = candidates[:count]

        for ac in selected:
            # Apply per-action abort threshold override to aircraft
            ac.abort_threshold_override = action.abort_conditions.p_success_threshold

            if action.type == AttackActionType.LAUNCH:
                commands.append(Command(
                    type="launch",
                    aircraft_id=ac.id,
                    position=target_pos,
                    from_base=ac.assigned_base,
                ))
            elif action.type == AttackActionType.PATROL:
                commands.append(Command(
                    type="patrol",
                    aircraft_id=ac.id,
                    position=target_pos,
                    from_base=ac.assigned_base,
                ))
            elif action.type == AttackActionType.RTB:
                commands.append(Command(
                    type="rtb",
                    aircraft_id=ac.id,
                    target_id=_resolve_rtb_base(action.target, ac, state),
                ))
            elif action.type == AttackActionType.INTERCEPT_ZONE:
                commands.append(Command(
                    type="patrol",
                    aircraft_id=ac.id,
                    position=target_pos,
                ))
            elif action.type == AttackActionType.REGROUP:
                commands.append(Command(
                    type="rtb",
                    aircraft_id=ac.id,
                    target_id=ac.assigned_base,
                ))
            elif action.type == AttackActionType.HOLD:
                commands.append(Command(
                    type="hold",
                    aircraft_id=ac.id,
                ))

            already_tasked.add(ac.id)

        events.append(Event(
            type=EventType.PLAYBOOK_TRIGGER_FIRED,  # attacker-side scheduled action
            tick=tick,
            payload={
                "source": "attack_plan",
                "action_type": action.type.value,
                "aircraft_type": action.aircraft_type,
                "count": len(selected),
                "from_base": action.from_base,
                "target": action.target.id if action.target else None,
            },
        ))

    return commands, events


def _select_candidates(
    action: AttackAction, state: SimulationState, already_tasked: set[str],
) -> list[Aircraft]:
    """Pick aircraft matching action filters (type, base, state requirement)."""
    candidates: list[Aircraft] = []
    for ac in state.friendly_aircraft:   # NB: from attacker's perspective "friendly"
        if ac.id in already_tasked or not ac.is_alive:
            continue
        if action.aircraft_type != "all" and ac.type.value != action.aircraft_type:
            continue
        if action.from_base and ac.assigned_base != action.from_base:
            continue

        if action.type == AttackActionType.LAUNCH:
            if ac.state != AircraftState.GROUNDED:
                continue
        else:
            if ac.state not in (AircraftState.GROUNDED, AircraftState.AIRBORNE, AircraftState.DAMAGED):
                continue

        candidates.append(ac)
    return candidates


def _resolve_target_position(
    target: AttackTarget | None, state: SimulationState,
) -> Position | None:
    if target is None:
        return None
    if target.x_km is not None and target.y_km is not None:
        return Position(target.x_km, target.y_km)

    if target.id:
        # Look across all locations on the defending side
        for loc in state.enemy_locations + state.friendly_locations:
            if loc.id == target.id:
                return loc.position
    return None


def _resolve_rtb_base(
    target: AttackTarget | None, aircraft: Aircraft, state: SimulationState,
) -> str | None:
    if target and target.type == "nearest_base":
        own_bases = [b for b in state.friendly_bases if b.side == aircraft.side]
        if own_bases:
            nearest = min(
                own_bases, key=lambda b: b.position.distance_to(aircraft.position),
            )
            return nearest.id
    if target and target.id:
        return target.id
    return aircraft.assigned_base

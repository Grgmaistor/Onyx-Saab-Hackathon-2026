from __future__ import annotations

from ..entities.aircraft import Aircraft, AircraftState
from ..entities.base import Base
from ..value_objects.decision import Decision, DecisionType
from ..value_objects.position import Position


def _find_base(bases: list[Base], base_id: str) -> Base | None:
    for b in bases:
        if b.id == base_id:
            return b
    return None


def _find_aircraft(aircraft_list: list[Aircraft], ac_id: str) -> Aircraft | None:
    for a in aircraft_list:
        if a.id == ac_id:
            return a
    return None


def execute_movements(
    friendly_aircraft: list[Aircraft],
    enemy_aircraft: list[Aircraft],
    decisions: list[Decision],
    friendly_bases: list[Base],
    tick_minutes: float,
) -> list[str]:
    events: list[str] = []
    all_aircraft = {a.id: a for a in friendly_aircraft + enemy_aircraft}

    for decision in decisions:
        ac = _find_aircraft(friendly_aircraft, decision.aircraft_id)
        if ac is None or not ac.is_alive:
            continue

        if decision.type == DecisionType.LAUNCH:
            if ac.state != AircraftState.GROUNDED:
                continue
            base = _find_base(friendly_bases, ac.assigned_base)
            if base and ac.id in base.current_aircraft:
                base.current_aircraft.remove(ac.id)
            ac.state = AircraftState.AIRBORNE
            if decision.position:
                ac.target_position = decision.position
            elif decision.target_id:
                target = all_aircraft.get(decision.target_id)
                if target:
                    ac.target_position = target.position
            events.append(f"{ac.id} launched from {ac.assigned_base}")

        elif decision.type == DecisionType.INTERCEPT:
            if ac.state not in (AircraftState.AIRBORNE, AircraftState.GROUNDED):
                continue
            if ac.state == AircraftState.GROUNDED:
                base = _find_base(friendly_bases, ac.assigned_base)
                if base and ac.id in base.current_aircraft:
                    base.current_aircraft.remove(ac.id)
                ac.state = AircraftState.AIRBORNE
                events.append(f"{ac.id} scrambled from {ac.assigned_base}")
            ac.target_id = decision.target_id
            target = all_aircraft.get(decision.target_id or "")
            if target:
                ac.target_position = target.position
            events.append(f"{ac.id} intercepting {decision.target_id}")

        elif decision.type == DecisionType.PATROL:
            if ac.state == AircraftState.GROUNDED:
                base = _find_base(friendly_bases, ac.assigned_base)
                if base and ac.id in base.current_aircraft:
                    base.current_aircraft.remove(ac.id)
                ac.state = AircraftState.AIRBORNE
                events.append(f"{ac.id} launched for patrol")
            if decision.position:
                ac.target_position = decision.position
            ac.target_id = None

        elif decision.type == DecisionType.RTB:
            if ac.state != AircraftState.AIRBORNE:
                continue
            target_base_id = decision.target_id or ac.assigned_base
            base = _find_base(friendly_bases, target_base_id)
            if base:
                ac.target_position = base.position
                ac.target_id = None
                ac.assigned_base = target_base_id
            events.append(f"{ac.id} returning to {target_base_id}")

        elif decision.type == DecisionType.RELOCATE:
            target_base_id = decision.target_id
            if not target_base_id:
                continue
            base = _find_base(friendly_bases, target_base_id)
            if base:
                if ac.state == AircraftState.GROUNDED:
                    old_base = _find_base(friendly_bases, ac.assigned_base)
                    if old_base and ac.id in old_base.current_aircraft:
                        old_base.current_aircraft.remove(ac.id)
                    ac.state = AircraftState.AIRBORNE
                ac.target_position = base.position
                ac.assigned_base = target_base_id
            events.append(f"{ac.id} relocating to {target_base_id}")

        elif decision.type == DecisionType.HOLD:
            ac.target_position = None
            ac.target_id = None

    # Move all airborne aircraft toward their targets
    for ac in friendly_aircraft + enemy_aircraft:
        if ac.state != AircraftState.AIRBORNE or not ac.is_alive:
            continue

        # Update intercept targets to current enemy position
        if ac.target_id:
            target = all_aircraft.get(ac.target_id)
            if target and target.is_alive:
                ac.target_position = target.position
            else:
                ac.target_id = None

        if ac.target_position is None:
            continue

        distance_this_tick = ac.speed_kmh * (tick_minutes / 60.0)
        distance_to_target = ac.position.distance_to(ac.target_position)
        actual_distance = min(distance_this_tick, distance_to_target)

        ac.position = ac.position.move_toward(ac.target_position, actual_distance)
        ac.fuel_current -= ac.fuel_burn_rate * actual_distance

        if ac.fuel_current <= 0:
            ac.fuel_current = 0
            ac.state = AircraftState.DESTROYED
            events.append(f"{ac.id} crashed — fuel exhausted")
            continue

        # Check arrival at base (RTB / RELOCATE)
        if distance_to_target <= 5.0:
            base = _find_base(
                friendly_bases if ac.side.value == friendly_bases[0].side.value else [],
                ac.assigned_base,
            )
            if base and ac.position.distance_to(base.position) <= 5.0:
                if len(base.current_aircraft) < base.max_aircraft_capacity:
                    ac.state = AircraftState.MAINTENANCE
                    ac.service_ticks_remaining = max(
                        1, int(ac.maintenance_time_minutes / tick_minutes)
                    )
                    base.current_aircraft.append(ac.id)
                    ac.target_position = None
                    ac.target_id = None
                    events.append(f"{ac.id} landed at {base.name}")

    return events

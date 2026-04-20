"""
Movement service. Moves airborne aircraft toward their target each tick.
Respects damage speed modifier. Fuel consumption deterministic.
"""

from __future__ import annotations

from ..entities.aircraft import Aircraft, AircraftState
from ..entities.location import Location
from ..value_objects.event import Event, EventType


def advance_aircraft(
    aircraft_list: list[Aircraft],
    friendly_bases: list[Location],
    enemy_bases: list[Location],
    tick_minutes: float,
    tick: int,
) -> list[Event]:
    """
    Move each airborne aircraft toward its target_position. Burn fuel. Detect
    arrival at base (RTB complete) and transition to MAINTENANCE.
    Detect fuel exhaustion -> DESTROYED.
    """
    events: list[Event] = []
    all_bases = friendly_bases + enemy_bases

    # Refresh intercept-by-id targets to the target's current position
    by_id = {a.id: a for a in aircraft_list}
    for ac in aircraft_list:
        if ac.target_id and ac.target_id in by_id:
            tgt = by_id[ac.target_id]
            if tgt.is_alive:
                ac.target_position = tgt.position
            else:
                ac.target_id = None

    for ac in aircraft_list:
        if ac.state not in (AircraftState.AIRBORNE, AircraftState.DAMAGED, AircraftState.ENGAGED):
            continue
        if not ac.is_alive:
            continue

        if ac.target_position is None:
            # Loiter: no forward motion; pilot still burns fuel
            ac.fuel_current -= ac.fuel_burn_rate * 5.0  # small idle burn
            if ac.fuel_current <= 0:
                ac.fuel_current = 0
                ac.state = AircraftState.DESTROYED
                events.append(Event(
                    type=EventType.AIRCRAFT_DESTROYED,
                    tick=tick,
                    payload={
                        "aircraft_id": ac.id,
                        "cause": "fuel_exhausted_loitering",
                        "side": ac.side.value,
                    },
                ))
            continue

        effective_speed = ac.effective_speed_kmh
        distance_this_tick = effective_speed * (tick_minutes / 60.0)
        distance_to_target = ac.position.distance_to(ac.target_position)
        actual_distance = min(distance_this_tick, distance_to_target)

        ac.position = ac.position.move_toward(ac.target_position, actual_distance)
        ac.fuel_current -= ac.fuel_burn_rate * actual_distance

        if ac.fuel_current <= 0:
            ac.fuel_current = 0
            ac.state = AircraftState.DESTROYED
            events.append(Event(
                type=EventType.AIRCRAFT_DESTROYED,
                tick=tick,
                payload={
                    "aircraft_id": ac.id,
                    "cause": "fuel_exhausted",
                    "side": ac.side.value,
                },
            ))
            continue

        # Arrival detection: if we reached target and target is a friendly base,
        # land (transition to MAINTENANCE for service)
        if actual_distance >= distance_to_target - 0.01:
            base = _landing_base(ac, all_bases)
            if base and base.is_operational and base.available_capacity > 0:
                # Land
                ac.state = (
                    AircraftState.REPAIRING if ac.damage_level.value in ("moderate", "heavy")
                    else AircraftState.MAINTENANCE
                )
                ac.service_ticks_remaining = max(
                    1, int(ac.maintenance_time_minutes / tick_minutes)
                )
                if ac.id not in base.current_aircraft:
                    base.current_aircraft.append(ac.id)
                ac.assigned_base = base.id
                ac.target_position = None
                ac.target_id = None

                events.append(Event(
                    type=EventType.LANDED,
                    tick=tick,
                    payload={
                        "aircraft_id": ac.id,
                        "base_id": base.id,
                        "base_name": base.name,
                        "damage_level": ac.damage_level.value,
                    },
                ))

    return events


def _landing_base(ac: Aircraft, all_bases: list[Location]) -> Location | None:
    """Find a friendly base the aircraft is currently AT, preferring assigned_base."""
    own_side_bases = [b for b in all_bases if b.side == ac.side]
    if not own_side_bases:
        return None

    # Within landing range of current position?
    LANDING_RANGE_KM = 5.0
    candidates = [
        b for b in own_side_bases
        if b.position.distance_to(ac.position) < LANDING_RANGE_KM
    ]
    if not candidates:
        return None

    # Prefer assigned_base if operational and in range
    for b in candidates:
        if b.id == ac.assigned_base and b.is_operational and b.available_capacity > 0:
            return b
    # Else nearest operational with capacity (landing redirect reflex)
    operational = [b for b in candidates if b.is_operational and b.available_capacity > 0]
    if not operational:
        return None
    return min(operational, key=lambda b: b.position.distance_to(ac.position))

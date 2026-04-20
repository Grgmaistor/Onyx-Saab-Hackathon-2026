"""
Strike resolver — handles the moment a striker aircraft arrives at its ground
target. Per user spec: deterministic hits, empty-magazine-on-arrival, auto RTB
after delivering.

No accuracy roll. If the aircraft has ammo and is within strike range of its
target, it delivers ALL remaining ammo in this tick.
"""

from __future__ import annotations

from ..entities.aircraft import Aircraft, AircraftState, AircraftType
from ..entities.location import Location
from ..value_objects.damage_model import WeaponType, AIRCRAFT_WEAPON_TYPE
from ..value_objects.event import Event, EventType


STRIKE_RANGE_KM = 10.0          # aircraft is "at target" within this range


def resolve_strikes(
    attackers: list[Aircraft],
    target_locations: list[Location],
    own_bases: list[Location],
    tick: int,
) -> tuple[list[Event], list[str]]:
    """
    For each airborne attacker with ammo and a target_position, check if it's
    within STRIKE_RANGE_KM of a location. If yes, deliver all remaining ammo.

    Returns structured events + list of aircraft IDs that should be flagged
    for destruction (parked aircraft destroyed at struck bases).

    Mutates: attackers (ammo depleted, auto-RTB setup), locations (damage).
    """
    events: list[Event] = []
    parked_to_destroy: list[str] = []

    for ac in attackers:
        if ac.state not in (AircraftState.AIRBORNE, AircraftState.DAMAGED):
            continue
        if not ac.is_alive:
            continue
        if ac.ammo_current <= 0:
            continue
        if ac.target_position is None:
            continue

        # Find a striking target at this position
        target_location = _find_location_at(ac, target_locations)
        if target_location is None:
            continue

        weapon_type = AIRCRAFT_WEAPON_TYPE.get(ac.type.value, WeaponType.MISSILES)
        weapons_delivered = ac.ammo_current
        ac.ammo_current = 0

        # Apply weapons to the location
        damage_events = target_location.apply_weapons(
            weapon_type=weapon_type,
            count=weapons_delivered,
            attacker_id=ac.id,
        )

        events.append(Event(
            type=EventType.WEAPONS_DELIVERED,
            tick=tick,
            payload={
                "attacker_id": ac.id,
                "attacker_type": ac.type.value,
                "attacker_side": ac.side.value,
                "target_id": target_location.id,
                "target_name": target_location.name,
                "target_archetype": target_location.archetype.value,
                "weapon_type": weapon_type.value,
                "weapons_delivered": weapons_delivered,
            },
        ))

        # Emit structured events for each damage outcome
        for ev in damage_events:
            ev_type_map = {
                "civilian_casualties": EventType.CIVILIAN_CASUALTIES,
                "destroy_parked_aircraft_request": EventType.PARKED_AIRCRAFT_DESTROYED,
                "launch_capacity_reduced": EventType.LAUNCH_CAPACITY_REDUCED,
                "refuel_rate_reduced": EventType.REFUEL_RATE_REDUCED,
                "launch_disabled": EventType.LAUNCH_DISABLED,
                "location_destroyed": EventType.LOCATION_DESTROYED,
                "casualty_multiplier_increased": EventType.CASUALTY_MULTIPLIER_INCREASED,
            }
            et = ev_type_map.get(ev["type"], EventType.WEAPONS_DELIVERED)

            # For parked-aircraft destruction: flag IDs for the sim engine to kill
            if ev["type"] == "destroy_parked_aircraft_request":
                count_to_kill = ev.get("count", 0)
                current = target_location.current_aircraft[:count_to_kill]
                parked_to_destroy.extend(current)
                ev["actual_destroyed"] = current
                ev["type"] = "parked_aircraft_destroyed"

            events.append(Event(
                type=et,
                tick=tick,
                payload={k: v for k, v in ev.items() if k != "type"},
            ))

        # If location was destroyed, all parked aircraft die
        if target_location.is_destroyed:
            parked_to_destroy.extend(target_location.current_aircraft)
            target_location.current_aircraft = []

        # Auto-RTB: mission complete. Redirect to the nearest friendly base.
        # Without this, the aircraft would loiter at the enemy target forever
        # (ammo==0 but no nearby enemy -> no pilot reflex fires).
        nearest_friendly_base = _nearest_operational(own_bases, ac)
        if nearest_friendly_base is not None:
            ac.target_position = nearest_friendly_base.position
            ac.assigned_base = nearest_friendly_base.id
        ac.target_id = None

    return events, parked_to_destroy


def _nearest_operational(bases: list[Location], ac: Aircraft) -> Location | None:
    """Nearest own-side operational base to `ac`."""
    candidates = [
        b for b in bases
        if b.side == ac.side and b.is_operational
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda b: b.position.distance_to(ac.position))


def _find_location_at(
    ac: Aircraft, locations: list[Location],
) -> Location | None:
    """Return the location this aircraft is currently at (within STRIKE_RANGE_KM)."""
    if ac.target_position is None:
        return None

    # Prefer a location matching the target_position explicitly
    for loc in locations:
        if loc.is_destroyed:
            continue
        dist = ac.position.distance_to(loc.position)
        if dist < STRIKE_RANGE_KM:
            return loc
    return None

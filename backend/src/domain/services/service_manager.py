"""
Base-side service: refuel, rearm, repair, fuel resupply. Respects location
damage-threshold multipliers for degraded bases.
"""

from __future__ import annotations

from ..entities.aircraft import Aircraft, AircraftState
from ..entities.location import Location
from ..value_objects.engagement_result import DamageLevel, EngagementParams
from ..value_objects.event import Event, EventType


def service_aircraft(
    bases: list[Location],
    aircraft_list: list[Aircraft],
    tick_minutes: float,
    tick: int,
    params: EngagementParams | None = None,
) -> list[Event]:
    """
    Progress any aircraft in service states: MAINTENANCE, REFUELING, REARMING,
    REPAIRING. When service is complete, transition through the chain and
    eventually land on GROUNDED.

    Refuel consumes base fuel storage. Refuel rate modulated by
    location.refuel_rate_multiplier (set by damage thresholds).

    Base fuel also regenerates per tick.
    """
    params = params or EngagementParams()
    events: list[Event] = []
    base_map = {b.id: b for b in bases}

    for ac in aircraft_list:
        if not ac.is_alive:
            continue

        if ac.state == AircraftState.REPAIRING:
            # Damaged aircraft: repair first, then service chain
            base = base_map.get(ac.assigned_base)
            if base and not base.is_operational:
                continue

            ac.service_ticks_remaining -= 1
            if ac.service_ticks_remaining <= 0:
                ac.damage_level = DamageLevel.NONE
                ac.speed_modifier = 1.0
                events.append(Event(
                    type=EventType.REPAIR_COMPLETE,
                    tick=tick,
                    payload={"aircraft_id": ac.id, "base_id": ac.assigned_base},
                ))
                # Transition to maintenance
                ac.state = AircraftState.MAINTENANCE
                ac.service_ticks_remaining = max(
                    1, int(ac.maintenance_time_minutes / tick_minutes)
                )

        elif ac.state == AircraftState.MAINTENANCE:
            ac.service_ticks_remaining -= 1
            if ac.service_ticks_remaining <= 0:
                # Move to refuel
                if ac.fuel_current < ac.fuel_capacity:
                    ac.state = AircraftState.REFUELING
                    ac.service_ticks_remaining = max(
                        1, int(ac.refuel_time_minutes / tick_minutes)
                    )
                elif ac.ammo_current < ac.ammo_capacity:
                    ac.state = AircraftState.REARMING
                    ac.service_ticks_remaining = max(
                        1, int(ac.rearm_time_minutes / tick_minutes)
                    )
                else:
                    ac.state = AircraftState.GROUNDED

        elif ac.state == AircraftState.REFUELING:
            base = base_map.get(ac.assigned_base)
            if base:
                fuel_per_tick = ac.fuel_capacity / max(
                    1, int(ac.refuel_time_minutes / tick_minutes)
                )
                # Damage-modulated rate
                fuel_per_tick *= base.refuel_rate_multiplier

                fuel_needed = ac.fuel_capacity - ac.fuel_current
                delivered = min(fuel_per_tick, fuel_needed, base.fuel_storage)
                ac.fuel_current += delivered
                base.fuel_storage -= delivered

            ac.service_ticks_remaining -= 1
            if ac.service_ticks_remaining <= 0 or ac.fuel_current >= ac.fuel_capacity:
                ac.fuel_current = min(ac.fuel_current, ac.fuel_capacity)
                events.append(Event(
                    type=EventType.REFUEL_COMPLETE,
                    tick=tick,
                    payload={"aircraft_id": ac.id, "base_id": ac.assigned_base},
                ))
                if ac.ammo_current < ac.ammo_capacity:
                    ac.state = AircraftState.REARMING
                    ac.service_ticks_remaining = max(
                        1, int(ac.rearm_time_minutes / tick_minutes)
                    )
                else:
                    ac.state = AircraftState.GROUNDED

        elif ac.state == AircraftState.REARMING:
            ac.service_ticks_remaining -= 1
            if ac.service_ticks_remaining <= 0:
                ac.ammo_current = ac.ammo_capacity
                events.append(Event(
                    type=EventType.REARM_COMPLETE,
                    tick=tick,
                    payload={"aircraft_id": ac.id, "base_id": ac.assigned_base},
                ))
                ac.state = AircraftState.GROUNDED

    # Base fuel resupply (damaged bases resupply slower)
    for base in bases:
        if not base.is_operational:
            continue
        if base.fuel_storage < base.fuel_storage_max:
            resupply = base.fuel_resupply_rate * base.refuel_rate_multiplier
            base.fuel_storage = min(base.fuel_storage_max, base.fuel_storage + resupply)

    return events


def kill_parked_aircraft(
    aircraft_ids: list[str],
    aircraft_list: list[Aircraft],
    tick: int,
) -> list[Event]:
    """Destroy aircraft that were parked at a struck/destroyed base."""
    events: list[Event] = []
    lookup = {a.id: a for a in aircraft_list}
    for aid in aircraft_ids:
        ac = lookup.get(aid)
        if ac is None or not ac.is_alive:
            continue
        ac.state = AircraftState.DESTROYED
        ac.damage_level = DamageLevel.DESTROYED
        events.append(Event(
            type=EventType.AIRCRAFT_DESTROYED,
            tick=tick,
            payload={
                "aircraft_id": ac.id,
                "cause": "parked_at_struck_base",
                "side": ac.side.value,
            },
        ))
    return events

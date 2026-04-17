from __future__ import annotations

from ..entities.aircraft import Aircraft, AircraftState
from ..entities.base import Base


def service_aircraft(
    bases: list[Base],
    aircraft: list[Aircraft],
    tick_minutes: float,
) -> list[str]:
    events: list[str] = []

    base_map = {b.id: b for b in bases}

    for ac in aircraft:
        if not ac.is_alive:
            continue

        if ac.state == AircraftState.MAINTENANCE:
            ac.service_ticks_remaining -= 1
            if ac.service_ticks_remaining <= 0:
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
                    events.append(f"{ac.id} ready at base")

        elif ac.state == AircraftState.REFUELING:
            base = base_map.get(ac.assigned_base)
            if base and base.fuel_storage > 0:
                fuel_needed = ac.fuel_capacity - ac.fuel_current
                fuel_per_tick = ac.fuel_capacity / max(
                    1, int(ac.refuel_time_minutes / tick_minutes)
                )
                fuel_delivered = min(fuel_per_tick, fuel_needed, base.fuel_storage)
                ac.fuel_current += fuel_delivered
                base.fuel_storage -= fuel_delivered

            ac.service_ticks_remaining -= 1
            if ac.service_ticks_remaining <= 0 or ac.fuel_current >= ac.fuel_capacity:
                ac.fuel_current = min(ac.fuel_current, ac.fuel_capacity)
                if ac.ammo_current < ac.ammo_capacity:
                    ac.state = AircraftState.REARMING
                    ac.service_ticks_remaining = max(
                        1, int(ac.rearm_time_minutes / tick_minutes)
                    )
                else:
                    ac.state = AircraftState.GROUNDED
                    events.append(f"{ac.id} refueled and ready")

        elif ac.state == AircraftState.REARMING:
            ac.service_ticks_remaining -= 1
            if ac.service_ticks_remaining <= 0:
                ac.ammo_current = ac.ammo_capacity
                ac.state = AircraftState.GROUNDED
                events.append(f"{ac.id} rearmed and ready")

    # Resupply bases
    for base in bases:
        if base.is_operational and base.fuel_storage < base.fuel_storage_max:
            base.fuel_storage = min(
                base.fuel_storage_max,
                base.fuel_storage + base.fuel_resupply_rate,
            )

    return events

from __future__ import annotations

from ..entities.aircraft import Aircraft, AircraftState, AircraftType
from ..entities.city import City

BOMBER_DAMAGE_RANGE_KM = 100.0
BOMBER_DAMAGE_PER_TICK = 0.02
CASUALTY_RATE = 0.1


def apply_city_damage(
    cities: list[City],
    enemy_aircraft: list[Aircraft],
    tick_minutes: float,
) -> list[str]:
    events: list[str] = []

    airborne_bombers = [
        a for a in enemy_aircraft
        if a.type == AircraftType.BOMBER
        and a.state == AircraftState.AIRBORNE
        and a.is_alive
    ]

    for city in cities:
        if city.is_destroyed:
            continue

        bombers_in_range = [
            b for b in airborne_bombers
            if b.position.distance_to(city.position) <= BOMBER_DAMAGE_RANGE_KM
        ]

        if not bombers_in_range:
            continue

        damage_increase = BOMBER_DAMAGE_PER_TICK * len(bombers_in_range)
        new_casualties = int(city.population * damage_increase * CASUALTY_RATE)

        city.damage_taken = min(1.0, city.damage_taken + damage_increase)
        city.casualties += new_casualties

        events.append(
            f"{city.name} under attack by {len(bombers_in_range)} bomber(s) — "
            f"damage {city.damage_taken:.1%}, casualties +{new_casualties}"
        )

        if city.is_destroyed:
            events.append(f"{city.name} has been DESTROYED")

    return events

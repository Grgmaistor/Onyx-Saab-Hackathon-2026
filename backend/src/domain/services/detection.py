from __future__ import annotations

from ..entities.aircraft import Aircraft, AircraftState
from ..entities.base import Base


def detect_threats(
    friendly_aircraft: list[Aircraft],
    friendly_bases: list[Base],
    enemy_aircraft: list[Aircraft],
    detection_range_km: float,
) -> list[Aircraft]:
    detected: list[Aircraft] = []
    seen_ids: set[str] = set()

    airborne_enemies = [
        a for a in enemy_aircraft
        if a.state == AircraftState.AIRBORNE and a.is_alive
    ]

    # Detection from bases
    for base in friendly_bases:
        if not base.is_operational:
            continue
        for enemy in airborne_enemies:
            if enemy.id not in seen_ids:
                dist = base.position.distance_to(enemy.position)
                if dist <= detection_range_km:
                    detected.append(enemy)
                    seen_ids.add(enemy.id)

    # Detection from airborne friendly aircraft (shorter range)
    air_detection = detection_range_km * 0.5
    for friendly in friendly_aircraft:
        if friendly.state != AircraftState.AIRBORNE or not friendly.is_alive:
            continue
        for enemy in airborne_enemies:
            if enemy.id not in seen_ids:
                dist = friendly.position.distance_to(enemy.position)
                if dist <= air_detection:
                    detected.append(enemy)
                    seen_ids.add(enemy.id)

    return detected

"""
Threat detection. Vectorized via NumPy distance matrices.

A defender detects an enemy aircraft when the enemy is within
`base_detection_range_km` of any operational base, OR within
`air_detection_range_km` of any airborne own aircraft.
"""

from __future__ import annotations

import numpy as np

from ..entities.aircraft import Aircraft, AircraftState
from ..entities.location import Location
from .geometry import (
    AIRBORNE_STATES,
    location_positions_array,
    pairwise_distances,
    positions_array,
)


def detect_threats(
    own_aircraft: list[Aircraft],
    own_bases: list[Location],
    enemy_aircraft: list[Aircraft],
    base_detection_range_km: float = 400.0,
    air_detection_range_km: float = 150.0,
) -> list[Aircraft]:
    """Return list of enemy aircraft detected by any own base or airborne unit."""

    # Filter to airborne, alive enemies (the only ones that can be detected)
    airborne_enemies = [
        a for a in enemy_aircraft
        if a.state in AIRBORNE_STATES and a.is_alive
    ]
    if not airborne_enemies:
        return []

    enemy_pos = positions_array(airborne_enemies)

    # Base radar detection
    operational_bases = [b for b in own_bases if b.is_operational]
    detected_mask = np.zeros(len(airborne_enemies), dtype=bool)

    if operational_bases:
        base_pos = location_positions_array(operational_bases)
        base_dists = pairwise_distances(base_pos, enemy_pos)  # (B, E)
        detected_mask |= (base_dists <= base_detection_range_km).any(axis=0)

    # Airborne-friendly detection (shorter range)
    airborne_own = [
        a for a in own_aircraft
        if a.state in AIRBORNE_STATES and a.is_alive
    ]
    if airborne_own:
        own_pos = positions_array(airborne_own)
        air_dists = pairwise_distances(own_pos, enemy_pos)   # (F, E)
        detected_mask |= (air_dists <= air_detection_range_km).any(axis=0)

    return [e for e, d in zip(airborne_enemies, detected_mask) if d]

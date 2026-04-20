"""
NumPy-accelerated geometry helpers.

Note on domain-layer dependencies: we treat NumPy as a math library (an
extension of stdlib's `math` for vector/matrix operations), not as
infrastructure. This is a deliberate, localized exception to the "domain has
zero external deps" rule — NumPy stays out of entities/value_objects and is
only used in performance-critical services (detection, engagement, reflexes).

All functions are pure: inputs are domain objects, outputs are numpy arrays or
indices. No I/O, no side effects.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

from ..entities.aircraft import Aircraft, AircraftState
from ..entities.location import Location


AIRBORNE_STATES = {
    AircraftState.AIRBORNE,
    AircraftState.DAMAGED,
    AircraftState.ENGAGED,
}


def positions_array(aircraft: Sequence[Aircraft]) -> np.ndarray:
    """(N, 2) float64 array of aircraft [x_km, y_km]. Empty array for N=0."""
    if not aircraft:
        return np.zeros((0, 2), dtype=np.float64)
    return np.array(
        [(a.position.x_km, a.position.y_km) for a in aircraft],
        dtype=np.float64,
    )


def location_positions_array(locations: Sequence[Location]) -> np.ndarray:
    """(N, 2) float64 array of location positions. Empty array for N=0."""
    if not locations:
        return np.zeros((0, 2), dtype=np.float64)
    return np.array(
        [(l.position.x_km, l.position.y_km) for l in locations],
        dtype=np.float64,
    )


def pairwise_distances(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Euclidean distance matrix between two sets of 2D points.

    a: (N, 2), b: (M, 2) → returns (N, M).
    Handles empty inputs: if N=0 or M=0, returns (N, M) shape with zeros.
    """
    if a.shape[0] == 0 or b.shape[0] == 0:
        return np.zeros((a.shape[0], b.shape[0]), dtype=np.float64)
    diff = a[:, None, :] - b[None, :, :]      # (N, M, 2)
    return np.sqrt(np.sum(diff * diff, axis=2))


def nearest_indices(
    queries: np.ndarray, targets: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """
    For each row in `queries`, find the nearest row in `targets`.

    Returns (nearest_idx, distances) where both are shape (N,).
    If targets is empty, returns (all -1, all inf) of length N.
    """
    if queries.shape[0] == 0:
        return np.zeros(0, dtype=np.int64), np.zeros(0, dtype=np.float64)
    if targets.shape[0] == 0:
        return (
            np.full(queries.shape[0], -1, dtype=np.int64),
            np.full(queries.shape[0], np.inf, dtype=np.float64),
        )
    dists = pairwise_distances(queries, targets)
    idx = np.argmin(dists, axis=1)
    nearest_d = dists[np.arange(len(idx)), idx]
    return idx, nearest_d


def airborne_mask(aircraft: Sequence[Aircraft]) -> np.ndarray:
    """Boolean mask of which aircraft are airborne and alive."""
    return np.array(
        [a.state in AIRBORNE_STATES and a.is_alive for a in aircraft],
        dtype=bool,
    )

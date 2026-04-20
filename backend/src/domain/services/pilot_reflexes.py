"""
Pilot reflex layer (Layer 2). See Development/Architecture/PILOT_REFLEXES.md.

Two entry points:
  * evaluate_reflexes(aircraft, state)           — single aircraft (legacy API)
  * evaluate_reflexes_bulk(aircraft_list, state) — vectorized over all aircraft

The bulk API uses NumPy distance matrices to replace O(N×M) nearest-enemy
scans with one O(N×M) array computation. Prefer the bulk version in the
simulation engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

import numpy as np

from ..entities.aircraft import Aircraft, AircraftState, AircraftType
from ..value_objects.engagement_result import DamageLevel
from .geometry import (
    AIRBORNE_STATES,
    location_positions_array,
    nearest_indices,
    pairwise_distances,
    positions_array,
)

if TYPE_CHECKING:
    from ..entities.location import Location
    from ..entities.simulation import SimulationState


class ReflexKind(str, Enum):
    DAMAGED_RTB = "damaged_rtb"
    BINGO_FUEL_RTB = "bingo_fuel_rtb"
    AMMO_DEPLETED_DISENGAGE = "ammo_depleted_disengage"
    OUTNUMBERED_BUGOUT = "outnumbered_bugout"
    MISSION_VIABILITY_ABORT = "mission_viability_abort"
    DETERRENCE_BREAK_OFF = "deterrence_break_off"
    LANDING_BASE_REDIRECT = "landing_base_redirect"
    NONE = "none"


@dataclass(frozen=True)
class ReflexAction:
    aircraft_id: str
    kind: ReflexKind
    p_success: float
    threshold: float
    action: str
    target_base_id: str | None
    rationale: dict
    overrides_commander: bool


def evaluate_reflexes_bulk(
    aircraft_list: list[Aircraft],
    state: "SimulationState",
) -> list[ReflexAction]:
    """
    Evaluate reflexes for every airborne aircraft in one pass. Returns a list
    of ReflexActions (same order as input, but only for aircraft that have a
    fired reflex — others omitted).

    Precomputes distance matrices once for the whole list.
    """
    airborne = [a for a in aircraft_list if a.is_airborne]
    if not airborne:
        return []

    # Split by side so we can look up each aircraft's own-side bases + enemy aircraft
    all_bases = [
        b for b in state.friendly_bases + state.enemy_bases
        if b.is_operational
    ]

    ac_pos = positions_array(airborne)
    base_pos = location_positions_array(all_bases)
    base_sides = np.array([b.side.value for b in all_bases])

    # Distance to each base (for nearest friendly-side base per aircraft)
    if len(all_bases) > 0:
        ac_to_base = pairwise_distances(ac_pos, base_pos)    # (N, B)
        sides = np.array([a.side.value for a in airborne])
        # Build per-aircraft mask of same-side bases
        same_side_mask = base_sides[None, :] == sides[:, None]  # (N, B)
        masked_distances = np.where(same_side_mask, ac_to_base, np.inf)
        nearest_base_idx = np.argmin(masked_distances, axis=1)
        # If no same-side base exists, nearest_base_idx points to something but
        # the value is inf; we'll check for that.
        nearest_base_d = masked_distances[np.arange(len(airborne)), nearest_base_idx]
    else:
        nearest_base_idx = np.full(len(airborne), -1, dtype=np.int64)
        nearest_base_d = np.full(len(airborne), np.inf)

    # All airborne aircraft (for nearest-enemy lookup)
    all_airborne = [
        a for a in state.all_aircraft
        if a.state in AIRBORNE_STATES and a.is_alive
    ]
    all_air_pos = positions_array(all_airborne)
    all_air_sides = np.array([a.side.value for a in all_airborne])

    if len(all_airborne) > 0:
        ac_to_air = pairwise_distances(ac_pos, all_air_pos)  # (N, M)
        # For each aircraft, mask to only enemy-side airborne
        own_sides = np.array([a.side.value for a in airborne])
        enemy_mask = all_air_sides[None, :] != own_sides[:, None]   # (N, M)
        masked_enemy_d = np.where(enemy_mask, ac_to_air, np.inf)
        nearest_enemy_idx = np.argmin(masked_enemy_d, axis=1)
        nearest_enemy_d = masked_enemy_d[np.arange(len(airborne)), nearest_enemy_idx]
    else:
        nearest_enemy_idx = np.full(len(airborne), -1, dtype=np.int64)
        nearest_enemy_d = np.full(len(airborne), np.inf)

    results: list[ReflexAction] = []
    for i, ac in enumerate(airborne):
        base_id = None
        if nearest_base_d[i] != np.inf and nearest_base_idx[i] >= 0:
            base_id = all_bases[int(nearest_base_idx[i])].id
        nearest_enemy = None
        if nearest_enemy_d[i] != np.inf and nearest_enemy_idx[i] >= 0:
            nearest_enemy = all_airborne[int(nearest_enemy_idx[i])]

        action = _evaluate_one(
            ac,
            state,
            base_id=base_id,
            nearest_enemy=nearest_enemy,
            nearest_enemy_distance=float(nearest_enemy_d[i]),
        )
        if action is not None:
            results.append(action)
    return results


def evaluate_reflexes(
    aircraft: Aircraft,
    state: "SimulationState",
) -> ReflexAction | None:
    """Single-aircraft variant kept for compatibility. Prefer bulk in hot paths."""
    if not aircraft.is_airborne:
        return None

    base = _nearest_friendly_base(aircraft, state)
    base_id = base.id if base else None
    nearest = _nearest_enemy(aircraft, state)
    nearest_d = (
        nearest.position.distance_to(aircraft.position) if nearest else float("inf")
    )
    return _evaluate_one(aircraft, state, base_id=base_id, nearest_enemy=nearest, nearest_enemy_distance=nearest_d)


def _evaluate_one(
    aircraft: Aircraft,
    state: "SimulationState",
    base_id: str | None,
    nearest_enemy: Aircraft | None,
    nearest_enemy_distance: float,
) -> ReflexAction | None:
    """Core decision table. Returns first reflex that fires, or None."""
    params = aircraft.reflex_params

    # 1. DAMAGED_RTB
    if aircraft.damage_level in (DamageLevel.MODERATE, DamageLevel.HEAVY):
        if base_id:
            return ReflexAction(
                aircraft_id=aircraft.id,
                kind=ReflexKind.DAMAGED_RTB,
                p_success=0.0,
                threshold=0.0,
                action="RTB",
                target_base_id=base_id,
                rationale={"damage_level": aircraft.damage_level.value},
                overrides_commander=True,
            )

    # 2. BINGO_FUEL_RTB
    bingo = params["bingo_fuel_threshold"]
    if aircraft.fuel_fraction < bingo:
        if base_id:
            return ReflexAction(
                aircraft_id=aircraft.id,
                kind=ReflexKind.BINGO_FUEL_RTB,
                p_success=0.0,
                threshold=bingo,
                action="RTB",
                target_base_id=base_id,
                rationale={"fuel_fraction": aircraft.fuel_fraction, "bingo": bingo},
                overrides_commander=True,
            )

    # 3. AMMO_DEPLETED_DISENGAGE
    if aircraft.ammo_current == 0 and nearest_enemy is not None and nearest_enemy_distance < 100.0:
        if base_id:
            return ReflexAction(
                aircraft_id=aircraft.id,
                kind=ReflexKind.AMMO_DEPLETED_DISENGAGE,
                p_success=0.0,
                threshold=0.0,
                action="RTB",
                target_base_id=base_id,
                rationale={"ammo_current": 0},
                overrides_commander=True,
            )

    # 4. OUTNUMBERED_BUGOUT (still O(N) but cheap for small N)
    if _is_outnumbered_in_combat(aircraft, state, params["bugout_ratio"]):
        if base_id:
            return ReflexAction(
                aircraft_id=aircraft.id,
                kind=ReflexKind.OUTNUMBERED_BUGOUT,
                p_success=0.0,
                threshold=params["bugout_ratio"],
                action="RTB",
                target_base_id=base_id,
                rationale={"bugout_ratio": params["bugout_ratio"]},
                overrides_commander=True,
            )

    # 5. MISSION_VIABILITY_ABORT
    if aircraft.target_position is not None:
        p_success = _p_success_from_inputs(
            aircraft, nearest_enemy, nearest_enemy_distance,
        )
        threshold = aircraft.abort_threshold()
        if p_success < threshold:
            action = params["abort_action"]
            if action != "CONTINUE" and base_id:
                return ReflexAction(
                    aircraft_id=aircraft.id,
                    kind=ReflexKind.MISSION_VIABILITY_ABORT,
                    p_success=p_success,
                    threshold=threshold,
                    action=action,
                    target_base_id=base_id,
                    rationale={
                        "p_success": round(p_success, 3),
                        "threshold": threshold,
                        "aircraft_type": aircraft.type.value,
                    },
                    overrides_commander=True,
                )

        # 6. DETERRENCE_BREAK_OFF (questionable band + close threat)
        if threshold <= p_success < threshold + 0.10:
            if (
                nearest_enemy is not None
                and nearest_enemy_distance < 150.0
                and aircraft.type in (AircraftType.BOMBER, AircraftType.UAV)
            ):
                if base_id:
                    return ReflexAction(
                        aircraft_id=aircraft.id,
                        kind=ReflexKind.DETERRENCE_BREAK_OFF,
                        p_success=p_success,
                        threshold=threshold,
                        action=params["abort_action"],
                        target_base_id=base_id,
                        rationale={"p_success": round(p_success, 3), "preemptive": True},
                        overrides_commander=True,
                    )

    return None


def compute_p_success(aircraft: Aircraft, state: "SimulationState") -> float:
    """Kept as public API for tests / debug. Uses legacy per-aircraft lookups."""
    nearest = _nearest_enemy(aircraft, state)
    dist = nearest.position.distance_to(aircraft.position) if nearest else float("inf")
    return _p_success_from_inputs(aircraft, nearest, dist)


def _p_success_from_inputs(
    aircraft: Aircraft,
    nearest_enemy: Aircraft | None,
    nearest_enemy_distance: float,
) -> float:
    if aircraft.target_position is not None:
        dist_to_target = aircraft.position.distance_to(aircraft.target_position)
        remaining_range = aircraft.fuel_current / max(aircraft.fuel_burn_rate, 0.0001)
        target_reachable = max(0.0, min(1.0, remaining_range / max(dist_to_target, 1.0)))
    else:
        target_reachable = 0.5

    if nearest_enemy is not None and nearest_enemy_distance < float("inf"):
        threat_proximity = 1.0 - max(0.0, min(1.0, nearest_enemy_distance / 400.0))
        matchup_advantage = aircraft.combat_matchups.get(nearest_enemy.type.value, 0.5)
    else:
        threat_proximity = 0.0
        matchup_advantage = 0.7

    ammo_ready = aircraft.ammo_current / max(aircraft.ammo_capacity, 1)
    bingo = aircraft.reflex_params["bingo_fuel_threshold"]
    fuel_margin = max(
        0.0,
        min(1.0, (aircraft.fuel_fraction - bingo) / max(1.0 - bingo, 0.01)),
    )

    t = aircraft.type
    if t == AircraftType.BOMBER:
        return (
            0.40 * target_reachable
            + 0.35 * (1.0 - threat_proximity)
            + 0.15 * matchup_advantage
            + 0.10 * fuel_margin
        )
    elif t == AircraftType.COMBAT_PLANE:
        return (
            0.40 * matchup_advantage
            + 0.25 * ammo_ready
            + 0.20 * fuel_margin
            + 0.15 * target_reachable
        )
    elif t == AircraftType.UAV:
        return (
            0.30 * (1.0 - threat_proximity)
            + 0.25 * target_reachable
            + 0.20 * matchup_advantage
            + 0.15 * ammo_ready
            + 0.10 * fuel_margin
        )
    else:
        return (
            0.50 * target_reachable
            + 0.25 * ammo_ready
            + 0.25 * (1.0 - threat_proximity)
        )


# ---- legacy helpers (for single-aircraft API) ----

def _nearest_friendly_base(aircraft, state):
    all_bases = state.friendly_bases + state.enemy_bases
    same_side = [b for b in all_bases if b.side == aircraft.side and b.is_operational]
    if not same_side:
        return None
    return min(same_side, key=lambda b: b.position.distance_to(aircraft.position))


def _nearest_enemy(aircraft, state):
    enemies = [
        a for a in state.all_aircraft
        if a.side != aircraft.side and a.is_airborne and a.is_alive
    ]
    if not enemies:
        return None
    return min(enemies, key=lambda a: a.position.distance_to(aircraft.position))


def _is_outnumbered_in_combat(aircraft, state, bugout_ratio):
    close_range_km = 80.0
    nearby_friendly = sum(
        1 for a in state.all_aircraft
        if a.side == aircraft.side
        and a.is_airborne
        and a.is_alive
        and a.position.distance_to(aircraft.position) < close_range_km
    )
    nearby_enemy = sum(
        1 for a in state.all_aircraft
        if a.side != aircraft.side
        and a.is_airborne
        and a.is_alive
        and a.position.distance_to(aircraft.position) < close_range_km
    )
    if nearby_enemy == 0:
        return False
    return nearby_friendly < (nearby_enemy / bugout_ratio)

"""
Multi-step BVR engagement resolution. Replaces the single-roll combat model.
Range-finding phase is vectorized; per-pair resolution is per-pair (inherently
sequential due to side-effects on aircraft state).
"""

from __future__ import annotations

import random
import uuid

import numpy as np

from ..entities.aircraft import Aircraft, AircraftState, AircraftType
from ..value_objects.engagement_result import (
    DamageLevel,
    EngagementOutcome,
    EngagementParams,
    EngagementResult,
)
from ..value_objects.event import Event, EventType
from .geometry import AIRBORNE_STATES, pairwise_distances, positions_array


def resolve_engagements(
    friendly: list[Aircraft],
    enemy: list[Aircraft],
    engagement_range_km: float,
    rng: random.Random,
    tick: int,
    params: EngagementParams | None = None,
) -> tuple[list[EngagementResult], list[Event]]:
    """
    Find pairs of airborne friendly/enemy aircraft within range via vectorized
    distance matrix, then resolve each pair through multi-round BVR exchange.

    Each aircraft participates in at most one engagement per tick.
    """
    params = params or EngagementParams()
    results: list[EngagementResult] = []
    events: list[Event] = []

    airborne_friendly = [
        a for a in friendly
        if a.state in AIRBORNE_STATES and a.is_alive
    ]
    airborne_enemy = [
        a for a in enemy
        if a.state in AIRBORNE_STATES and a.is_alive
    ]

    if not airborne_friendly or not airborne_enemy:
        return results, events

    # Vectorized range check
    fa_pos = positions_array(airborne_friendly)
    ea_pos = positions_array(airborne_enemy)
    dist_matrix = pairwise_distances(fa_pos, ea_pos)      # (F, E)
    in_range = dist_matrix <= engagement_range_km         # (F, E) bool

    # Greedy pairing: for each friendly, pick nearest in-range enemy not yet engaged
    engaged: set[str] = set()
    # Sort friendly by the minimum in-range distance (closest engagements first)
    # to avoid long-range pairings stealing a close enemy from a short-range one
    priority_order = np.argsort(
        np.where(in_range.any(axis=1),
                 dist_matrix.min(axis=1, initial=np.inf, where=in_range),
                 np.inf)
    )

    for fi in priority_order:
        attacker = airborne_friendly[int(fi)]
        if attacker.id in engaged:
            continue
        if attacker.ammo_current == 0:
            # Cannot initiate, may still be paired as defender
            continue
        # Candidates for this attacker: enemies in range, not yet engaged
        cands = np.where(in_range[fi])[0]
        cands = [int(j) for j in cands if airborne_enemy[int(j)].id not in engaged]
        if not cands:
            continue
        # Pick closest
        closest_j = min(cands, key=lambda j: dist_matrix[fi, j])
        defender = airborne_enemy[closest_j]

        if attacker.ammo_current == 0 and defender.ammo_current == 0:
            continue

        result = _resolve_one(attacker, defender, rng, params, tick)
        results.append(result)
        engaged.add(attacker.id)
        engaged.add(defender.id)

        events.append(Event(
            type=EventType.ENGAGEMENT,
            tick=tick,
            payload={
                "engagement_id": result.engagement_id,
                "attacker_id": attacker.id,
                "attacker_type": attacker.type.value,
                "attacker_side": attacker.side.value,
                "defender_id": defender.id,
                "defender_type": defender.type.value,
                "defender_side": defender.side.value,
                "rounds": result.rounds_fought,
                "missiles_fired": {
                    "attacker": result.missiles_fired_attacker,
                    "defender": result.missiles_fired_defender,
                },
                "outcomes": {
                    "attacker": result.attacker_outcome.value,
                    "defender": result.defender_outcome.value,
                },
                "damage": {
                    "attacker": result.attacker_damage.value,
                    "defender": result.defender_damage.value,
                },
                "position_km": [attacker.position.x_km, attacker.position.y_km],
            },
        ))

    return results, events


def _resolve_one(
    attacker: Aircraft,
    defender: Aircraft,
    rng: random.Random,
    params: EngagementParams,
    tick: int,
) -> EngagementResult:
    """Multi-round BVR exchange between two aircraft."""
    eng_id = "eng-" + uuid.uuid4().hex[:8]
    atk_fired = 0
    def_fired = 0
    atk_outcome = EngagementOutcome.DISENGAGED
    def_outcome = EngagementOutcome.DISENGAGED
    atk_damage = DamageLevel.NONE
    def_damage = DamageLevel.NONE
    rounds_fought = 0

    for round_num in range(params.max_rounds):
        rounds_fought = round_num + 1

        if attacker.ammo_current > 0:
            salvo = min(params.missiles_per_salvo, attacker.ammo_current)
            attacker.ammo_current -= salvo
            atk_fired += salvo

            eff_pk = _effective_pk(params, attacker, defender)
            p_hit = 1.0 - (1.0 - eff_pk) ** salvo
            if rng.random() < p_hit:
                damage = _roll_damage(rng, params)
                def_damage = damage
                def_outcome = _outcome_from_damage(damage)
                _apply_damage_to_aircraft(defender, damage, params)
                if damage == DamageLevel.DESTROYED:
                    atk_outcome = EngagementOutcome.EVADED
                    return EngagementResult(
                        engagement_id=eng_id, tick=tick,
                        attacker_id=attacker.id, defender_id=defender.id,
                        attacker_outcome=atk_outcome, defender_outcome=def_outcome,
                        attacker_damage=atk_damage, defender_damage=def_damage,
                        missiles_fired_attacker=atk_fired, missiles_fired_defender=def_fired,
                        rounds_fought=rounds_fought,
                    )

        if defender.state != AircraftState.DESTROYED and defender.ammo_current > 0:
            salvo = min(params.missiles_per_salvo, defender.ammo_current)
            defender.ammo_current -= salvo
            def_fired += salvo

            eff_pk = _effective_pk(params, defender, attacker)
            p_hit = 1.0 - (1.0 - eff_pk) ** salvo
            if rng.random() < p_hit:
                damage = _roll_damage(rng, params)
                atk_damage = damage
                atk_outcome = _outcome_from_damage(damage)
                _apply_damage_to_aircraft(attacker, damage, params)
                if damage == DamageLevel.DESTROYED:
                    def_outcome = EngagementOutcome.EVADED
                    return EngagementResult(
                        engagement_id=eng_id, tick=tick,
                        attacker_id=attacker.id, defender_id=defender.id,
                        attacker_outcome=atk_outcome, defender_outcome=def_outcome,
                        attacker_damage=atk_damage, defender_damage=def_damage,
                        missiles_fired_attacker=atk_fired, missiles_fired_defender=def_fired,
                        rounds_fought=rounds_fought,
                    )

        if _should_disengage(attacker, params) or _should_disengage(defender, params):
            break

    if atk_damage == DamageLevel.NONE and atk_outcome != EngagementOutcome.EVADED:
        atk_outcome = EngagementOutcome.EVADED if atk_fired == 0 else EngagementOutcome.DISENGAGED
    if def_damage == DamageLevel.NONE and def_outcome != EngagementOutcome.EVADED:
        def_outcome = EngagementOutcome.EVADED if def_fired == 0 else EngagementOutcome.DISENGAGED

    return EngagementResult(
        engagement_id=eng_id, tick=tick,
        attacker_id=attacker.id, defender_id=defender.id,
        attacker_outcome=atk_outcome, defender_outcome=def_outcome,
        attacker_damage=atk_damage, defender_damage=def_damage,
        missiles_fired_attacker=atk_fired, missiles_fired_defender=def_fired,
        rounds_fought=rounds_fought,
    )


def _effective_pk(params: EngagementParams, shooter: Aircraft, target: Aircraft) -> float:
    base = params.pk_optimal_range
    matchup = shooter.combat_matchups.get(target.type.value, 0.5)
    blended = 0.5 * base + 0.5 * matchup
    blended -= params.cm_effectiveness
    blended -= params.maneuver_effectiveness
    return max(0.05, min(0.95, blended))


def _roll_damage(rng: random.Random, params: EngagementParams) -> DamageLevel:
    roll = rng.random()
    if roll < params.p_hard_kill:
        return DamageLevel.DESTROYED
    if roll < params.p_hard_kill + params.p_mission_kill:
        return DamageLevel.HEAVY
    if roll < params.p_hard_kill + params.p_mission_kill + params.p_damage_rtb:
        return DamageLevel.MODERATE
    return DamageLevel.LIGHT


def _outcome_from_damage(damage: DamageLevel) -> EngagementOutcome:
    return {
        DamageLevel.DESTROYED: EngagementOutcome.HARD_KILL,
        DamageLevel.HEAVY: EngagementOutcome.MISSION_KILL,
        DamageLevel.MODERATE: EngagementOutcome.DAMAGED_RTB,
        DamageLevel.LIGHT: EngagementOutcome.LIGHT_DAMAGE,
    }[damage]


def _apply_damage_to_aircraft(
    aircraft: Aircraft, damage: DamageLevel, params: EngagementParams,
) -> None:
    aircraft.damage_level = damage
    if damage == DamageLevel.DESTROYED:
        aircraft.state = AircraftState.DESTROYED
        return
    if damage == DamageLevel.HEAVY:
        aircraft.state = AircraftState.DAMAGED
        aircraft.speed_modifier = 0.6
    elif damage == DamageLevel.MODERATE:
        aircraft.state = AircraftState.DAMAGED
        aircraft.speed_modifier = 0.8
    elif damage == DamageLevel.LIGHT:
        aircraft.speed_modifier = 0.95


def _should_disengage(aircraft: Aircraft, params: EngagementParams) -> bool:
    if aircraft.state == AircraftState.DESTROYED:
        return True
    if aircraft.fuel_fraction < params.fuel_disengage_threshold:
        return True
    if aircraft.ammo_current <= params.ammo_disengage_threshold:
        return True
    return False

"""
Main simulation engine. Deterministic given (attack_plan_id, defense_playbook_id,
settings_id) — RNG seeded from the triple. Pure Python, no external dependencies,
no LLM calls during the tick loop.

Tick phases (per Development/SIMULATION.md + revised architecture):

  1. DETECT       - enemy aircraft detected by defender sensors
  2. REFLEXES     - Layer 2 pilot autonomous decisions
  3. ATTACK CMD   - Attacker executes scheduled plan actions
  4. DEFENSE CMD  - Defender executes playbook (triggers + standing orders)
  5. APPLY CMDS   - Apply all commands (launch, intercept, RTB, patrol, hold, relocate)
  6. MOVE         - Aircraft physics (move, burn fuel, land)
  7. ENGAGE       - Multi-step BVR engagement resolution
  8. STRIKE       - Strikers empty magazines on targets at arrival
  9. KILL PARKED  - Destroy parked aircraft at damaged/destroyed bases
 10. SERVICE      - Refuel, rearm, repair, base resupply
 11. RECORD       - Snapshot for replay log
 12. CHECK        - Termination conditions
"""

from __future__ import annotations

import hashlib
import random
import uuid
from datetime import datetime, timezone

from ..entities.aircraft import (
    Aircraft,
    AircraftState,
    AircraftType,
    Side,
    create_aircraft,
)
from ..entities.location import Location
from ..entities.simulation import (
    SimulationConfig,
    SimulationState,
    SimulationStatus,
    SimulationTick,
)
from ..value_objects.attack_plan import AttackPlan
from ..value_objects.damage_model import LocationArchetype
from ..value_objects.defense_playbook import DefensePlaybook
from ..value_objects.engagement_result import DamageLevel, EngagementParams
from ..value_objects.event import Event, EventType
from ..value_objects.match_result import MatchResult, SimulationOutcome
from ..value_objects.metrics import SimulationMetrics
from ..value_objects.position import Position
from ..value_objects.settings import Settings
from .attack_plan_executor import execute_attack_plan
from .detection import detect_threats
from .engagement_engine import resolve_engagements
from .fitness import compute_fitness
from .movement import advance_aircraft
from .pilot_reflexes import evaluate_reflexes_bulk
from .playbook_executor import Command, ExecutorState, execute_playbook
from .service_manager import kill_parked_aircraft, service_aircraft
from .strike_resolver import resolve_strikes


def run_simulation(
    settings: Settings,
    attack_plan: AttackPlan,
    defense_playbook: DefensePlaybook,
    defender_side: Side = Side.NORTH,
    live_commander=None,                   # optional callable(tick, state, history) -> dict
) -> MatchResult:
    """
    Run one full simulation deterministically.
    RNG seeded from (attack_plan_id, defense_playbook_id, settings_id).
    """
    seed = _compute_deterministic_seed(
        attack_plan.plan_id, defense_playbook.playbook_id, settings.settings_id,
    )
    rng = random.Random(seed)

    # ==== Build initial world state ====
    attacker_side = Side.SOUTH if defender_side == Side.NORTH else Side.NORTH
    friendly_bases, friendly_cities = _build_locations(settings, defender_side)
    enemy_bases, enemy_cities = _build_locations(settings, attacker_side)

    friendly_aircraft = _build_aircraft(
        settings, defender_side, friendly_bases,
    )
    enemy_aircraft = _build_aircraft(
        settings, attacker_side, enemy_bases,
    )

    executor_state = ExecutorState()
    engagement_params = _parse_engagement_params(settings)

    max_ticks = settings.max_ticks
    tick_minutes = settings.tick_minutes

    event_log: list[SimulationTick] = []
    all_events: list[Event] = []       # flat for fitness/analysis
    outcome = SimulationOutcome.UNDECIDED

    # ==== Tick 0 snapshot ====
    all_ac = friendly_aircraft + enemy_aircraft
    all_locs = friendly_bases + enemy_bases + friendly_cities + enemy_cities
    t0_events = [Event(
        type=EventType.SIMULATION_STARTED,
        tick=0,
        payload={
            "defender_side": defender_side.value,
            "attack_plan_id": attack_plan.plan_id,
            "defense_playbook_id": defense_playbook.playbook_id,
            "settings_id": settings.settings_id,
        },
    )]
    event_log.append(_record(0, all_ac, all_locs, t0_events))

    # ==== Main loop ====
    for tick in range(1, max_ticks + 1):
        tick_events: list[Event] = []

        # 1. DETECT — defender sees attackers
        detected = detect_threats(
            own_aircraft=friendly_aircraft,
            own_bases=friendly_bases,
            enemy_aircraft=enemy_aircraft,
            base_detection_range_km=400.0,
            air_detection_range_km=150.0,
        )
        # Attacker also detects defenders (symmetric)
        detected_attacker = detect_threats(
            own_aircraft=enemy_aircraft,
            own_bases=enemy_bases,
            enemy_aircraft=friendly_aircraft,
            base_detection_range_km=400.0,
            air_detection_range_km=150.0,
        )

        friendly_state = SimulationState(
            tick=tick,
            friendly_aircraft=friendly_aircraft,
            enemy_aircraft=enemy_aircraft,
            friendly_bases=friendly_bases,
            enemy_bases=enemy_bases,
            friendly_cities=friendly_cities,
            enemy_cities=enemy_cities,
            detected_threats=detected,
        )
        attacker_state = SimulationState(
            tick=tick,
            friendly_aircraft=enemy_aircraft,
            enemy_aircraft=friendly_aircraft,
            friendly_bases=enemy_bases,
            enemy_bases=friendly_bases,
            friendly_cities=enemy_cities,
            enemy_cities=friendly_cities,
            detected_threats=detected_attacker,
        )

        # 2. REFLEXES — Layer 2 autonomous decisions for all airborne aircraft
        reflex_tasked: set[str] = set()
        reflex_commands: list[Command] = []
        ac_by_id = {a.id: a for a in friendly_aircraft + enemy_aircraft}

        # Bulk-evaluate reflexes in one pass (vectorized nearest-enemy lookups)
        friendly_reflexes = evaluate_reflexes_bulk(friendly_aircraft, friendly_state)
        enemy_reflexes = evaluate_reflexes_bulk(enemy_aircraft, attacker_state)

        for reflex in friendly_reflexes + enemy_reflexes:
            ac = ac_by_id.get(reflex.aircraft_id)
            if ac is None:
                continue
            reflex_tasked.add(reflex.aircraft_id)
            if reflex.action in ("RTB", "DISENGAGE_RTB", "JETTISON_WEAPONS_RTB"):
                if reflex.action == "JETTISON_WEAPONS_RTB":
                    ac.ammo_current = 0
                reflex_commands.append(Command(
                    type="rtb",
                    aircraft_id=ac.id,
                    target_id=reflex.target_base_id,
                ))
            tick_events.append(Event(
                type=EventType.PILOT_REFLEX,
                tick=tick,
                payload={
                    "aircraft_id": reflex.aircraft_id,
                    "aircraft_type": ac.type.value,
                    "side": ac.side.value,
                    "reflex": reflex.kind.value,
                    "action": reflex.action,
                    "p_success": reflex.p_success,
                    "threshold": reflex.threshold,
                    "rationale": reflex.rationale,
                },
            ))

        # 3. ATTACK COMMANDS — attacker's plan actions for this tick
        attacker_tasked: set[str] = set(reflex_tasked)
        attack_commands, attack_events = execute_attack_plan(
            plan=attack_plan,
            state=attacker_state,
            tick=tick,
            already_tasked=attacker_tasked,
        )
        tick_events.extend(attack_events)

        # 4. DEFENSE COMMANDS — playbook triggers + standing orders
        defender_tasked: set[str] = set(reflex_tasked)
        defense_commands, defense_events = execute_playbook(
            playbook=defense_playbook,
            state=friendly_state,
            executor_state=executor_state,
            tick=tick,
            already_tasked=defender_tasked,
        )
        tick_events.extend(defense_events)

        # Optional: live commander can add/override commands
        if live_commander is not None:
            llm_commands = live_commander(tick, friendly_state, tick_events)
            if llm_commands:
                defense_commands.extend(llm_commands)
                tick_events.append(Event(
                    type=EventType.LLM_COMMAND,
                    tick=tick,
                    payload={"count": len(llm_commands)},
                ))

        # 5. APPLY COMMANDS
        _apply_commands(reflex_commands + defense_commands, friendly_aircraft, friendly_bases)
        _apply_commands(attack_commands, enemy_aircraft, enemy_bases)

        # 6. MOVE
        move_events = advance_aircraft(
            aircraft_list=friendly_aircraft + enemy_aircraft,
            friendly_bases=friendly_bases,
            enemy_bases=enemy_bases,
            tick_minutes=tick_minutes,
            tick=tick,
        )
        tick_events.extend(move_events)

        # 7. ENGAGE — multi-step BVR
        _, eng_events = resolve_engagements(
            friendly=friendly_aircraft,
            enemy=enemy_aircraft,
            engagement_range_km=engagement_params.pk_optimal_range * 100 + 50,  # ~95km default
            rng=rng,
            tick=tick,
            params=engagement_params,
        )
        tick_events.extend(eng_events)

        # 8. STRIKE — strikers that arrived at targets empty their magazines.
        # Pass own_bases so the striker can be redirected home after delivery.
        strike_events, parked_killed = resolve_strikes(
            attackers=enemy_aircraft,
            target_locations=friendly_bases + friendly_cities,
            own_bases=enemy_bases,
            tick=tick,
        )
        tick_events.extend(strike_events)
        strike_events_f, parked_killed_f = resolve_strikes(
            attackers=friendly_aircraft,
            target_locations=enemy_bases + enemy_cities,
            own_bases=friendly_bases,
            tick=tick,
        )
        tick_events.extend(strike_events_f)

        # 9. KILL PARKED
        parked_events = kill_parked_aircraft(
            parked_killed + parked_killed_f,
            friendly_aircraft + enemy_aircraft,
            tick,
        )
        tick_events.extend(parked_events)

        # 10. SERVICE
        svc_events_f = service_aircraft(
            bases=friendly_bases,
            aircraft_list=friendly_aircraft,
            tick_minutes=tick_minutes,
            tick=tick,
            params=engagement_params,
        )
        svc_events_e = service_aircraft(
            bases=enemy_bases,
            aircraft_list=enemy_aircraft,
            tick_minutes=tick_minutes,
            tick=tick,
            params=engagement_params,
        )
        tick_events.extend(svc_events_f)
        tick_events.extend(svc_events_e)

        # 11. RECORD
        all_events.extend(tick_events)
        event_log.append(_record(tick, all_ac, all_locs, tick_events))

        # 12. CHECK termination
        term = _check_termination(
            friendly_cities, enemy_cities,
            friendly_aircraft, enemy_aircraft,
            tick, max_ticks,
        )
        if term is not None:
            outcome = term
            tick_events.append(Event(
                type=EventType.SIMULATION_ENDED,
                tick=tick,
                payload={"outcome": outcome.value},
            ))
            break

    # ==== Compute metrics + result ====
    metrics = _compute_metrics(
        event_log=all_events,
        friendly_aircraft=friendly_aircraft,
        enemy_aircraft=enemy_aircraft,
        friendly_bases=friendly_bases,
        friendly_cities=friendly_cities,
    )
    fitness = compute_fitness(metrics, outcome)

    match_id = MatchResult.compute_id(
        attack_plan.plan_id, defense_playbook.playbook_id, settings.settings_id,
    )
    return MatchResult(
        match_id=match_id,
        settings_id=settings.settings_id,
        attack_plan_id=attack_plan.plan_id,
        pattern_id=attack_plan.pattern_id or "",
        defense_playbook_id=defense_playbook.playbook_id,
        outcome=outcome,
        fitness_score=fitness,
        metrics=metrics,
        event_log=[t.to_dict() for t in event_log],
        created_at=datetime.now(timezone.utc).isoformat(),
    )


# =======================================================================
# Setup helpers
# =======================================================================

def _compute_deterministic_seed(
    attack_plan_id: str, defense_playbook_id: str, settings_id: str,
) -> int:
    key = f"{attack_plan_id}|{defense_playbook_id}|{settings_id}"
    hashed = hashlib.sha256(key.encode()).digest()
    return int.from_bytes(hashed[:8], "big")


def _build_locations(
    settings: Settings, side: Side,
) -> tuple[list[Location], list[Location]]:
    """Read scenario JSON to construct bases + cities for one side."""
    bases: list[Location] = []
    cities: list[Location] = []
    scenario = settings.scenario
    side_key = side.value

    for b in scenario.get("bases", {}).get(side_key, []):
        pos = b["position"]
        archetype_str = b.get("archetype", "air_base")
        archetype = LocationArchetype(archetype_str)
        fuel = b.get("fuel_storage", 5000)
        bases.append(Location(
            id=b["id"],
            name=b["name"],
            side=side,
            position=Position(pos[0], pos[1]),
            archetype=archetype,
            max_aircraft_capacity=b.get("max_aircraft_capacity", 12),
            fuel_storage=fuel,
            fuel_storage_max=fuel,
            fuel_resupply_rate=b.get("fuel_resupply_rate", 500),
        ))

    for c in scenario.get("cities", {}).get(side_key, []):
        pos = c["position"]
        archetype = (
            LocationArchetype.CAPITAL
            if c.get("is_capital", False)
            else LocationArchetype.MAJOR_CITY
        )
        cities.append(Location(
            id=c["id"],
            name=c["name"],
            side=side,
            position=Position(pos[0], pos[1]),
            archetype=archetype,
            population=c.get("population", 100000),
        ))

    return bases, cities


def _build_aircraft(
    settings: Settings, side: Side, bases: list[Location],
) -> list[Aircraft]:
    """Instantiate aircraft from settings resource allocation."""
    aircraft_list: list[Aircraft] = []
    resources = (
        settings.defender_resources if side == Side.NORTH
        else settings.attacker_resources
    )
    # resources shape: {"base_id": {"combat_plane": N, ...}, ...}
    # Or legacy list form: [{"type":"combat_plane","count":N,"base":"..."}]

    base_map = {b.id: b for b in bases}
    counters: dict[str, int] = {}

    if isinstance(resources, dict):
        for base_id, type_counts in resources.items():
            base = base_map.get(base_id)
            if not base:
                continue
            for ac_type_str, count in type_counts.items():
                ac_type = AircraftType(ac_type_str)
                for _ in range(count):
                    counters[ac_type_str] = counters.get(ac_type_str, 0) + 1
                    ac_id = f"{side.value[0]}-{ac_type_str[:2]}-{counters[ac_type_str]:02d}"
                    ac = create_aircraft(
                        ac_id, ac_type, side,
                        Position(base.position.x_km, base.position.y_km),
                        base_id,
                    )
                    aircraft_list.append(ac)
                    if ac.id not in base.current_aircraft:
                        base.current_aircraft.append(ac.id)
    elif isinstance(resources, list):
        for entry in resources:
            base = base_map.get(entry.get("base", ""))
            if not base:
                continue
            ac_type = AircraftType(entry["type"])
            for _ in range(entry.get("count", 1)):
                counters[entry["type"]] = counters.get(entry["type"], 0) + 1
                ac_id = f"{side.value[0]}-{entry['type'][:2]}-{counters[entry['type']]:02d}"
                ac = create_aircraft(
                    ac_id, ac_type, side,
                    Position(base.position.x_km, base.position.y_km),
                    entry["base"],
                )
                aircraft_list.append(ac)
                if ac.id not in base.current_aircraft:
                    base.current_aircraft.append(ac.id)

    return aircraft_list


def _parse_engagement_params(settings: Settings) -> EngagementParams:
    ep = settings.engagement_params or {}
    return EngagementParams(
        pk_optimal_range=ep.get("pk_optimal_range", 0.45),
        pk_max_range=ep.get("pk_max_range", 0.15),
        pk_wvr=ep.get("pk_wvr", 0.65),
        missiles_per_salvo=ep.get("missiles_per_salvo", 2),
        max_rounds=ep.get("max_rounds", 3),
        cm_effectiveness=ep.get("cm_effectiveness", 0.15),
        ecm_effectiveness=ep.get("ecm_effectiveness", 0.20),
        maneuver_effectiveness=ep.get("maneuver_effectiveness", 0.10),
        p_hard_kill=ep.get("p_hard_kill", 0.25),
        p_mission_kill=ep.get("p_mission_kill", 0.35),
        p_damage_rtb=ep.get("p_damage_rtb", 0.30),
        p_light_damage=ep.get("p_light_damage", 0.10),
    )


# =======================================================================
# Command application
# =======================================================================

def _apply_commands(
    commands: list[Command], aircraft_list: list[Aircraft], bases: list[Location],
) -> None:
    lookup = {a.id: a for a in aircraft_list}
    base_map = {b.id: b for b in bases}

    for cmd in commands:
        ac = lookup.get(cmd.aircraft_id)
        if ac is None or not ac.is_alive:
            continue

        if cmd.type == "launch":
            if ac.state != AircraftState.GROUNDED:
                continue
            # Check base launch capacity (damage-based)
            base = base_map.get(ac.assigned_base)
            if base and (not base.is_operational or base.launch_capacity_multiplier <= 0.05):
                continue
            if base and ac.id in base.current_aircraft:
                base.current_aircraft.remove(ac.id)
            ac.state = AircraftState.AIRBORNE
            ac.target_position = cmd.position
            ac.target_id = cmd.target_id

        elif cmd.type == "rtb":
            target_base_id = cmd.target_id or ac.assigned_base
            base = base_map.get(target_base_id)
            if base:
                ac.target_position = base.position
                ac.target_id = None
                ac.assigned_base = target_base_id

        elif cmd.type == "patrol":
            if ac.state == AircraftState.GROUNDED:
                base = base_map.get(ac.assigned_base)
                if base and base.is_operational and ac.id in base.current_aircraft:
                    base.current_aircraft.remove(ac.id)
                ac.state = AircraftState.AIRBORNE
            ac.target_position = cmd.position
            ac.target_id = None

        elif cmd.type == "hold":
            ac.target_position = None
            ac.target_id = None

        elif cmd.type == "relocate":
            target_base_id = cmd.target_id
            if target_base_id:
                base = base_map.get(target_base_id)
                if base:
                    ac.target_position = base.position
                    ac.assigned_base = target_base_id


# =======================================================================
# Recording & termination
# =======================================================================

def _record(
    tick: int,
    aircraft_list: list[Aircraft],
    locations: list[Location],
    events: list[Event],
) -> SimulationTick:
    return SimulationTick(
        tick=tick,
        aircraft_states=[a.to_dict() for a in aircraft_list],
        location_states=[loc.to_dict() for loc in locations],
        events=[e.to_dict() for e in events],
    )


def _check_termination(
    friendly_cities: list[Location],
    enemy_cities: list[Location],
    friendly_aircraft: list[Aircraft],
    enemy_aircraft: list[Aircraft],
    current_tick: int,
    max_ticks: int,
) -> SimulationOutcome | None:
    # Capital loss = game over
    for c in friendly_cities:
        if c.is_capital and c.is_destroyed:
            return SimulationOutcome.LOSS
    for c in enemy_cities:
        if c.is_capital and c.is_destroyed:
            return SimulationOutcome.WIN

    if not any(a.is_alive for a in friendly_aircraft):
        return SimulationOutcome.LOSS
    if not any(a.is_alive for a in enemy_aircraft):
        return SimulationOutcome.WIN

    if current_tick >= max_ticks:
        return SimulationOutcome.TIMEOUT

    return None


# =======================================================================
# Metrics computation
# =======================================================================

def _compute_metrics(
    event_log: list[Event],
    friendly_aircraft: list[Aircraft],
    enemy_aircraft: list[Aircraft],
    friendly_bases: list[Location],
    friendly_cities: list[Location],
) -> SimulationMetrics:
    total_casualties = sum(c.casualties for c in friendly_cities)
    capital_survived = all(
        not c.is_destroyed for c in friendly_cities if c.is_capital
    )
    cities_defended = sum(
        1 for c in friendly_cities if not c.is_destroyed and c.casualty_multiplier < 1.5
    )
    bases_lost = sum(1 for b in friendly_bases if b.is_destroyed)
    bases_remaining = sum(1 for b in friendly_bases if not b.is_destroyed)

    aircraft_lost = sum(1 for a in friendly_aircraft if not a.is_alive)
    aircraft_remaining = sum(1 for a in friendly_aircraft if a.is_alive)
    aircraft_damaged_in_repair = sum(
        1 for a in friendly_aircraft
        if a.state == AircraftState.REPAIRING and a.is_alive
    )

    # Derive from event log
    time_to_first_casualty: int | None = None
    missiles_fired = 0
    missiles_hit = 0
    engagements = 0
    engagements_won = 0
    sorties_flown = 0
    deterred = 0
    weapons_jettisoned = 0
    mission_kills = 0
    parked_destroyed = 0
    strike_attempts_by_enemy = 0
    strikes_delivered_by_enemy = 0

    for ev in event_log:
        p = ev.payload
        if ev.type == EventType.CIVILIAN_CASUALTIES and time_to_first_casualty is None:
            time_to_first_casualty = ev.tick
        if ev.type == EventType.ENGAGEMENT:
            engagements += 1
            missiles_fired += (
                p["missiles_fired"]["attacker"] + p["missiles_fired"]["defender"]
            )
            # "attacker" here is whoever initiated; determine friendly side from payload
            # Winning = enemy outcome is HARD_KILL or MISSION_KILL
            if p["outcomes"]["defender"] in ("hard_kill", "mission_kill"):
                if p["attacker_side"] in ("north",):  # friendly is defender side
                    engagements_won += 1
        if ev.type == EventType.LAUNCH:
            sorties_flown += 1
        if ev.type == EventType.PILOT_REFLEX:
            if p.get("reflex") in ("mission_viability_abort", "deterrence_break_off"):
                if p.get("side") != "north":  # enemy was deterred
                    deterred += 1
                if p.get("action") == "JETTISON_WEAPONS_RTB":
                    weapons_jettisoned += 1
        if ev.type == EventType.WEAPONS_DELIVERED:
            if p.get("attacker_side") != "north":
                strikes_delivered_by_enemy += 1
        if ev.type == EventType.AIRCRAFT_DESTROYED and p.get("cause") == "parked_at_struck_base":
            if p.get("side") == "north":
                parked_destroyed += 1

    # Air denial score: enemy strike sorties that didn't deliver
    strike_attempts_by_enemy = strikes_delivered_by_enemy + deterred
    air_denial_score = (
        deterred / strike_attempts_by_enemy if strike_attempts_by_enemy > 0 else 1.0
    )

    fuel_efficiency = (
        sum(a.fuel_current for a in friendly_aircraft if a.is_alive)
        / max(sum(a.fuel_capacity for a in friendly_aircraft if a.is_alive), 1.0)
    )
    engagement_win_rate = engagements_won / max(engagements, 1)

    return SimulationMetrics(
        total_civilian_casualties=total_casualties,
        time_to_first_casualty=time_to_first_casualty,
        cities_defended=cities_defended,
        capital_survived=capital_survived,
        aircraft_lost=aircraft_lost,
        aircraft_remaining=aircraft_remaining,
        aircraft_damaged_in_repair=aircraft_damaged_in_repair,
        bases_lost=bases_lost,
        bases_remaining=bases_remaining,
        parked_aircraft_destroyed=parked_destroyed,
        total_engagements=engagements,
        engagements_won=engagements_won,
        engagement_win_rate=engagement_win_rate,
        missiles_fired=missiles_fired,
        missiles_hit=missiles_hit,
        enemy_sorties_deterred=deterred,
        enemy_weapons_jettisoned=weapons_jettisoned,
        enemy_mission_kills=mission_kills,
        air_denial_score=air_denial_score,
        sorties_flown=sorties_flown,
        fuel_efficiency=fuel_efficiency,
        response_time_avg=0.0,
        total_ticks=len(event_log),
    )

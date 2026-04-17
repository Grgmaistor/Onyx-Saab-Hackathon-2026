from __future__ import annotations

import random
import uuid

from ..entities.aircraft import Aircraft, AircraftState, AircraftType, Side, create_aircraft
from ..entities.base import Base
from ..entities.city import City
from ..entities.simulation import (
    SimulationConfig, SimulationOutcome, SimulationResult, SimulationState, SimulationTick,
)
from ..ports.strategy import StrategyPort
from ..value_objects.position import Position
from .combat_resolver import resolve_engagements
from .damage import apply_city_damage
from .detection import detect_threats
from .fuel_manager import service_aircraft
from .metrics import compute_metrics
from .movement import execute_movements


def _build_aircraft(scenario: dict, side: str, bases_map: dict[str, Base]) -> list[Aircraft]:
    aircraft: list[Aircraft] = []
    side_enum = Side(side)
    counters: dict[str, int] = {}
    for entry in scenario.get("starting_aircraft", {}).get(side, []):
        ac_type = AircraftType(entry["type"])
        base = bases_map.get(entry["base"])
        if not base:
            continue
        tk = ac_type.value
        for _ in range(entry["count"]):
            counters[tk] = counters.get(tk, 0) + 1
            ac_id = f"{side[0]}-{tk[:2]}-{counters[tk]:02d}"
            ac = create_aircraft(ac_id, ac_type, side_enum,
                                 Position(base.position.x_km, base.position.y_km), entry["base"])
            aircraft.append(ac)
            if ac.id not in base.current_aircraft:
                base.current_aircraft.append(ac.id)
    return aircraft


def _build_bases(scenario: dict, side: str) -> list[Base]:
    bases: list[Base] = []
    side_enum = Side(side)
    for b in scenario.get("bases", {}).get(side, []):
        pos = b["position"]
        fuel = b.get("fuel_storage", 5000)
        bases.append(Base(
            id=b["id"], name=b["name"], side=side_enum,
            position=Position(pos[0], pos[1]),
            max_aircraft_capacity=b.get("max_aircraft_capacity", 12),
            fuel_storage=fuel, fuel_storage_max=fuel,
            fuel_resupply_rate=b.get("fuel_resupply_rate", 100)))
    return bases


def _build_cities(scenario: dict, side: str) -> list[City]:
    cities: list[City] = []
    side_enum = Side(side)
    for c in scenario.get("cities", {}).get(side, []):
        pos = c["position"]
        cities.append(City(
            id=c["id"], name=c["name"], side=side_enum,
            position=Position(pos[0], pos[1]),
            population=c.get("population", 100000),
            is_capital=c.get("is_capital", False),
            defense_value=c.get("defense_value", 0.5)))
    return cities


def _record(tick, all_ac, all_bases, all_cities, battles, decisions, events):
    return SimulationTick(
        tick=tick, aircraft_states=[a.to_dict() for a in all_ac],
        base_states=[b.to_dict() for b in all_bases],
        city_states=[c.to_dict() for c in all_cities],
        battles=battles, decisions_made=decisions, events=list(events))


def _check_end(fc, ec, fa, ea, tick, mx):
    for c in fc:
        if c.is_capital and c.is_destroyed:
            return SimulationOutcome.LOSS
    for c in ec:
        if c.is_capital and c.is_destroyed:
            return SimulationOutcome.WIN
    if not [a for a in fa if a.is_alive]:
        return SimulationOutcome.LOSS
    if not [a for a in ea if a.is_alive]:
        return SimulationOutcome.WIN
    if tick >= mx:
        return SimulationOutcome.TIMEOUT
    return None


def run_simulation(scenario: dict, strategy: StrategyPort,
                   enemy_strategy: StrategyPort, config: SimulationConfig) -> SimulationResult:
    rng = random.Random(config.seed)
    sim_id = f"sim-{uuid.uuid4().hex[:8]}"
    fs = config.side.value
    es = "south" if fs == "north" else "north"

    fb = _build_bases(scenario, fs)
    eb = _build_bases(scenario, es)
    fa = _build_aircraft(scenario, fs, {b.id: b for b in fb})
    ea = _build_aircraft(scenario, es, {b.id: b for b in eb})
    fc = _build_cities(scenario, fs)
    ec = _build_cities(scenario, es)

    matchups = scenario.get("combat_matchups")
    if matchups:
        for ac in fa + ea:
            tm = matchups.get(ac.type.value)
            if tm:
                ac.combat_matchups = dict(tm)

    log: list[SimulationTick] = []
    outcome = SimulationOutcome.UNDECIDED
    all_ac = fa + ea
    all_b = fb + eb
    all_c = fc + ec

    log.append(_record(0, all_ac, all_b, all_c, [], [],
                        [f"Simulation started. Controlling {fs.upper()} side."]))

    for tick in range(1, config.max_ticks + 1):
        evts, btls, decs = [], [], []

        det = detect_threats(fa, fb, ea, config.detection_range_km)
        state_f = SimulationState(tick=tick, friendly_aircraft=fa, enemy_aircraft=ea,
                                   friendly_bases=fb, enemy_bases=eb, friendly_cities=fc,
                                   enemy_cities=ec, active_battles=[], detected_threats=det)
        fd = strategy.decide(state_f)
        for d in fd:
            decs.append({"side": fs, "type": d.type.value, "aircraft_id": d.aircraft_id, "target_id": d.target_id})

        edet = detect_threats(ea, eb, fa, config.detection_range_km)
        state_e = SimulationState(tick=tick, friendly_aircraft=ea, enemy_aircraft=fa,
                                   friendly_bases=eb, enemy_bases=fb, friendly_cities=ec,
                                   enemy_cities=fc, active_battles=[], detected_threats=edet)
        ed = enemy_strategy.decide(state_e)
        for d in ed:
            decs.append({"side": es, "type": d.type.value, "aircraft_id": d.aircraft_id, "target_id": d.target_id})

        evts.extend(execute_movements(fa, ea, fd, fb, config.tick_minutes))
        evts.extend(execute_movements(ea, fa, ed, eb, config.tick_minutes))

        battles, cevts = resolve_engagements(fa, ea, config.engagement_range_km, rng, tick)
        evts.extend(cevts)
        btls.extend([b.to_dict() for b in battles])

        evts.extend(apply_city_damage(fc, ea, config.tick_minutes))
        evts.extend(apply_city_damage(ec, fa, config.tick_minutes))
        evts.extend(service_aircraft(fb, fa, config.tick_minutes))
        evts.extend(service_aircraft(eb, ea, config.tick_minutes))

        log.append(_record(tick, all_ac, all_b, all_c, btls, decs, evts))

        res = _check_end(fc, ec, fa, ea, tick, config.max_ticks)
        if res is not None:
            outcome = res
            break

    ft = log[-1]
    metrics = compute_metrics(log, ft.aircraft_states, ft.city_states, ft.base_states, fs)
    return SimulationResult(simulation_id=sim_id, batch_id=None, config=config,
                            outcome=outcome, total_ticks=len(log) - 1,
                            event_log=log, metrics=metrics)

"""
Playbook executor — Layer 3 defender. Reads a DefensePlaybook JSON each tick,
evaluates standing orders + triggers + constraints, emits Decision-like
commands for the simulation to apply.

Uses a dispatcher pattern: string condition/action names mapped to Python
handler functions. New conditions/actions can be added by registering new
handlers without schema changes.

Published vocabulary (what the LLM can use):

CONDITIONS:
  - "enemy_aircraft_detected" — enemy threats detected this tick
    params: type?, within_km_of_asset?, asset_types?
  - "force_ratio_below" — friendly:enemy ratio below threshold
    params: ratio
  - "asset_health_below" — location health below a threshold
    params: asset_id?, archetype?, health_fraction
  - "airborne_friendly_count_below" — less than N friendly airborne
    params: count

ACTIONS:
  - "scramble_intercept" — launch N aircraft to intercept threats
    params: count, aircraft_type?, from_base?, intercept_target?
  - "commit_reserve" — launch fraction of grounded reserve
    params: fraction
  - "assign_cap" — send N aircraft to patrol a zone
    params: count, aircraft_type, zone
  - "rtb_all_with_damage" — recall all damaged airborne
  - "reassign_landing_base" — redirect RTB to nearest operational
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from ..entities.aircraft import Aircraft, AircraftState, AircraftType
from ..entities.location import Location
from ..entities.simulation import SimulationState
from ..value_objects.defense_playbook import (
    Constraints,
    DefensePlaybook,
    StandingOrder,
    Trigger,
)
from ..value_objects.event import Event, EventType
from ..value_objects.position import Position


@dataclass
class Command:
    """A unit-level order produced by the playbook."""
    type: str                         # "launch" | "intercept" | "patrol" | "rtb" | "hold" | "relocate"
    aircraft_id: str
    target_id: str | None = None
    position: Position | None = None
    from_base: str | None = None


@dataclass
class ExecutorState:
    """Persistent per-simulation state for the executor."""
    trigger_cooldowns: dict[str, int] = field(default_factory=dict)
    fired_triggers_this_tick: set[str] = field(default_factory=set)


def execute_playbook(
    playbook: DefensePlaybook,
    state: SimulationState,
    executor_state: ExecutorState,
    tick: int,
    already_tasked: set[str],
) -> tuple[list[Command], list[Event]]:
    """
    Run the playbook against current state. Returns commands for aircraft not
    already tasked (by pilot reflexes, typically).

    Order:
    1. Enforce constraints (compute allowed commit count)
    2. Evaluate triggers (sorted by priority)
    3. Maintain standing orders (fill gaps)
    """
    commands: list[Command] = []
    events: list[Event] = []
    executor_state.fired_triggers_this_tick.clear()

    # Decrement cooldowns
    for name in list(executor_state.trigger_cooldowns.keys()):
        executor_state.trigger_cooldowns[name] -= 1
        if executor_state.trigger_cooldowns[name] <= 0:
            del executor_state.trigger_cooldowns[name]

    # Compute reserve budget
    alive_friendly = [a for a in state.friendly_aircraft if a.is_alive]
    max_committed = int(len(alive_friendly) * (1.0 - playbook.constraints.reserve_fraction))
    currently_airborne = sum(
        1 for a in alive_friendly if a.is_airborne and a.id not in already_tasked
    )

    # ==== Triggers (priority order) ====
    for trigger in sorted(playbook.triggers, key=lambda t: -t.priority):
        if trigger.name in executor_state.trigger_cooldowns:
            continue
        if _evaluate_condition(trigger.when, state):
            trigger_commands, trigger_events = _execute_action(
                trigger.action, trigger.name, state, already_tasked, playbook.constraints,
            )
            commands.extend(trigger_commands)
            events.append(Event(
                type=EventType.PLAYBOOK_TRIGGER_FIRED,
                tick=tick,
                payload={
                    "trigger_name": trigger.name,
                    "commands_issued": len(trigger_commands),
                },
            ))
            events.extend(trigger_events)
            executor_state.fired_triggers_this_tick.add(trigger.name)
            if trigger.cooldown_ticks > 0:
                executor_state.trigger_cooldowns[trigger.name] = trigger.cooldown_ticks

            for c in trigger_commands:
                already_tasked.add(c.aircraft_id)

    # ==== Standing orders (maintain patrols, alerts) ====
    for order in sorted(playbook.standing_orders, key=lambda o: -o.priority):
        order_commands = _maintain_standing_order(
            order, state, already_tasked, playbook.constraints,
        )
        commands.extend(order_commands)
        for c in order_commands:
            already_tasked.add(c.aircraft_id)
        if order_commands:
            events.append(Event(
                type=EventType.STANDING_ORDER_MAINTAINED,
                tick=tick,
                payload={
                    "order_name": order.name,
                    "commands_issued": len(order_commands),
                },
            ))

    return commands, events


# =======================================================================
# CONDITION HANDLERS (registered by name in the vocabulary above)
# =======================================================================

def _evaluate_condition(condition: dict, state: SimulationState) -> bool:
    cond_type = condition.get("condition", "")

    if cond_type == "enemy_aircraft_detected":
        return _check_enemy_detected(condition, state)
    if cond_type == "force_ratio_below":
        return _check_force_ratio(condition, state)
    if cond_type == "asset_health_below":
        return _check_asset_health(condition, state)
    if cond_type == "airborne_friendly_count_below":
        return _check_airborne_count(condition, state)
    return False


def _check_enemy_detected(cond: dict, state: SimulationState) -> bool:
    filt = cond.get("filter", {})
    enemy_type = filt.get("type")
    within_km = filt.get("within_km_of_asset")
    asset_types = filt.get("asset_types", [])

    for threat in state.detected_threats:
        if enemy_type and threat.type.value != enemy_type:
            continue
        if within_km:
            target_locations = _assets_by_type(state.friendly_locations, asset_types)
            if any(
                loc.position.distance_to(threat.position) <= within_km
                for loc in target_locations
            ):
                return True
        else:
            return True
    return False


def _check_force_ratio(cond: dict, state: SimulationState) -> bool:
    threshold = cond.get("ratio", 1.0)
    friendly = len([a for a in state.friendly_aircraft if a.is_alive and a.is_airborne])
    enemy = len([a for a in state.enemy_aircraft if a.is_alive and a.is_airborne])
    if enemy == 0:
        return False
    return (friendly / enemy) < threshold


def _check_asset_health(cond: dict, state: SimulationState) -> bool:
    asset_id = cond.get("asset_id")
    archetype = cond.get("archetype")
    threshold = cond.get("health_fraction", 0.5)

    candidates = state.friendly_locations
    if asset_id:
        candidates = [loc for loc in candidates if loc.id == asset_id]
    if archetype:
        candidates = [loc for loc in candidates if loc.archetype.value == archetype]

    for loc in candidates:
        # Heuristic: health fraction = 1 - weighted_hits_fraction
        # Simpler: use is_destroyed / casualty_multiplier as proxy
        if loc.is_destroyed:
            return True
        if loc.casualty_multiplier > 1.5:
            return True
    return False


def _check_airborne_count(cond: dict, state: SimulationState) -> bool:
    threshold = cond.get("count", 2)
    airborne = sum(1 for a in state.friendly_aircraft if a.is_alive and a.is_airborne)
    return airborne < threshold


def _assets_by_type(locations: list[Location], asset_types: list[str]) -> list[Location]:
    if not asset_types:
        return locations
    return [loc for loc in locations if loc.archetype.value in asset_types]


# =======================================================================
# ACTION HANDLERS
# =======================================================================

def _execute_action(
    action: dict,
    trigger_name: str,
    state: SimulationState,
    already_tasked: set[str],
    constraints: Constraints,
) -> tuple[list[Command], list[Event]]:
    atype = action.get("type", "")

    if atype == "scramble_intercept":
        return _action_scramble_intercept(action, state, already_tasked, constraints), []
    if atype == "commit_reserve":
        return _action_commit_reserve(action, state, already_tasked, constraints), []
    if atype == "assign_cap":
        return _action_assign_cap(action, state, already_tasked, constraints), []
    if atype == "rtb_all_with_damage":
        return _action_rtb_damaged(action, state, already_tasked), []
    return [], []


def _action_scramble_intercept(
    action: dict,
    state: SimulationState,
    already_tasked: set[str],
    constraints: Constraints,
) -> list[Command]:
    count = int(action.get("count", 1))
    aircraft_type = action.get("aircraft_type", "combat_plane")
    prioritize_types: list[str] = action.get("prioritize_types", [])
    commands: list[Command] = []

    ready = [
        a for a in state.friendly_aircraft
        if a.state == AircraftState.GROUNDED
        and a.id not in already_tasked
        and a.is_alive
        and a.fuel_fraction >= constraints.min_fuel_to_launch_fraction
        and (aircraft_type == "any" or a.type.value == aircraft_type)
    ]

    # Also consider already-airborne fighters (redirect them to the new threat)
    airborne_free = [
        a for a in state.friendly_aircraft
        if a.state == AircraftState.AIRBORNE
        and a.id not in already_tasked
        and a.is_alive
        and a.ammo_current > 0
        and (aircraft_type == "any" or a.type.value == aircraft_type)
    ]

    threats = list(state.detected_threats)
    if not threats:
        return []

    # Sort threats: prioritize types first (e.g., bomber over drone), then by
    # proximity to any friendly asset (capital > city > base)
    def _asset_proximity(t):
        min_d = float("inf")
        for loc in state.friendly_locations:
            if loc.is_destroyed:
                continue
            d = loc.position.distance_to(t.position)
            if d < min_d:
                min_d = d
        return min_d

    def _type_priority(t):
        if not prioritize_types:
            return 0
        try:
            return -(len(prioritize_types) - prioritize_types.index(t.type.value))
        except ValueError:
            return 1   # not in prioritize_types -> lower priority

    threats.sort(key=lambda t: (_type_priority(t), _asset_proximity(t)))

    assigned_here: set[str] = set()
    # For each priority threat, send nearest available interceptor
    for threat in threats[:count]:
        # Best candidate: prefer grounded (fresh fuel/ammo) closer to threat
        candidates = [a for a in ready if a.id not in assigned_here] + \
                     [a for a in airborne_free if a.id not in assigned_here]
        if not candidates:
            break
        nearest = min(candidates, key=lambda a: a.position.distance_to(threat.position))
        assigned_here.add(nearest.id)
        commands.append(Command(
            type="launch" if nearest.state == AircraftState.GROUNDED else "patrol",
            aircraft_id=nearest.id,
            target_id=threat.id,
            position=threat.position,
            from_base=nearest.assigned_base,
        ))

    return commands


def _action_commit_reserve(
    action: dict,
    state: SimulationState,
    already_tasked: set[str],
    constraints: Constraints,
) -> list[Command]:
    fraction = float(action.get("fraction", 0.5))
    commands: list[Command] = []

    ready = [
        a for a in state.friendly_aircraft
        if a.state == AircraftState.GROUNDED
        and a.id not in already_tasked
        and a.is_alive
        and a.fuel_fraction >= constraints.min_fuel_to_launch_fraction
    ]
    n = int(len(ready) * fraction)
    threats = list(state.detected_threats)

    for i in range(min(n, len(ready))):
        ac = ready[i]
        if threats:
            threat = threats[i % len(threats)]
            commands.append(Command(
                type="launch",
                aircraft_id=ac.id,
                target_id=threat.id,
                position=threat.position,
                from_base=ac.assigned_base,
            ))
        else:
            # No threat — patrol near capital
            capitals = [c for c in state.friendly_cities if c.is_capital]
            patrol_pos = capitals[0].position if capitals else (
                state.friendly_bases[0].position if state.friendly_bases else None
            )
            if patrol_pos:
                commands.append(Command(
                    type="patrol",
                    aircraft_id=ac.id,
                    position=patrol_pos,
                    from_base=ac.assigned_base,
                ))

    return commands


def _action_assign_cap(
    action: dict,
    state: SimulationState,
    already_tasked: set[str],
    constraints: Constraints,
) -> list[Command]:
    count = int(action.get("count", 2))
    aircraft_type = action.get("aircraft_type", "combat_plane")
    zone = action.get("zone", {})

    patrol_pos = _resolve_zone_center(zone, state)
    if patrol_pos is None:
        return []

    ready_or_airborne = [
        a for a in state.friendly_aircraft
        if a.is_alive
        and a.id not in already_tasked
        and (aircraft_type == "any" or a.type.value == aircraft_type)
        and a.state in (AircraftState.GROUNDED, AircraftState.AIRBORNE)
    ]

    # Pick closest `count` aircraft
    ready_or_airborne.sort(key=lambda a: a.position.distance_to(patrol_pos))
    chosen = ready_or_airborne[:count]

    return [
        Command(
            type="patrol" if a.state == AircraftState.AIRBORNE else "launch",
            aircraft_id=a.id,
            position=patrol_pos,
            from_base=a.assigned_base,
        )
        for a in chosen
    ]


def _action_rtb_damaged(
    action: dict,
    state: SimulationState,
    already_tasked: set[str],
) -> list[Command]:
    # Pilot reflexes already handle this; no-op, but kept as a valid vocabulary action
    return []


# =======================================================================
# STANDING ORDER MAINTENANCE
# =======================================================================

def _maintain_standing_order(
    order: StandingOrder,
    state: SimulationState,
    already_tasked: set[str],
    constraints: Constraints,
) -> list[Command]:
    """Keep `count` aircraft of `aircraft_type` active in `zone`."""
    if order.type not in ("patrol", "ready_alert"):
        return []

    zone_center = _resolve_zone_center(order.zone, state)
    if zone_center is None:
        return []

    # How many aircraft are currently patrolling this zone?
    ZONE_RADIUS = order.zone.get("radius_km", 120) if order.zone.get("type") == "circle" else 100
    on_station = [
        a for a in state.friendly_aircraft
        if a.is_airborne and a.is_alive
        and a.position.distance_to(zone_center) < ZONE_RADIUS
        and (order.aircraft_type == "any" or a.type.value == order.aircraft_type)
    ]
    gap = order.count - len(on_station)
    if gap <= 0:
        return []

    # Launch additional aircraft to fill the gap
    ready = [
        a for a in state.friendly_aircraft
        if a.state == AircraftState.GROUNDED
        and a.id not in already_tasked
        and a.is_alive
        and a.fuel_fraction >= constraints.min_fuel_to_launch_fraction
        and (order.aircraft_type == "any" or a.type.value == order.aircraft_type)
        and (order.base is None or a.assigned_base == order.base)
    ]
    ready.sort(key=lambda a: a.position.distance_to(zone_center))

    return [
        Command(
            type="launch",
            aircraft_id=a.id,
            position=zone_center,
            from_base=a.assigned_base,
        )
        for a in ready[:gap]
    ]


# =======================================================================
# ZONE RESOLUTION (free-form JSON with type discriminator)
# =======================================================================

def _resolve_zone_center(zone: dict, state: SimulationState) -> Position | None:
    if not zone:
        return None
    ztype = zone.get("type", "")

    if ztype == "circle":
        center = zone.get("center")
        if isinstance(center, str):
            # Named asset
            loc = _find_location_by_id(center, state)
            return loc.position if loc else None
        if isinstance(center, list) and len(center) >= 2:
            return Position(center[0], center[1])
        center_xy = zone.get("center_xy")
        if isinstance(center_xy, list) and len(center_xy) >= 2:
            return Position(center_xy[0], center_xy[1])

    if ztype == "point":
        pos = zone.get("position")
        if isinstance(pos, list) and len(pos) >= 2:
            return Position(pos[0], pos[1])

    if ztype == "line":
        frm = zone.get("from", [])
        to = zone.get("to", [])
        if len(frm) >= 2 and len(to) >= 2:
            # Midpoint as patrol anchor
            return Position((frm[0] + to[0]) / 2, (frm[1] + to[1]) / 2)

    if ztype == "base_defense":
        base_id = zone.get("base", "")
        loc = _find_location_by_id(base_id, state)
        return loc.position if loc else None

    return None


def _find_location_by_id(asset_id: str, state: SimulationState) -> Location | None:
    for loc in state.friendly_locations + state.enemy_locations:
        if loc.id == asset_id:
            return loc
    return None

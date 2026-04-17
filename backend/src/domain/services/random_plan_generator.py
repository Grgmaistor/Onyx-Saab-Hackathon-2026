from __future__ import annotations

import random
import uuid
from datetime import datetime, timezone

from ..entities.attack_plan import (
    AttackAction, AttackActionType, AttackPlan, AttackPlanSource, AttackTarget,
)

# South side bases and north side targets (default attacker = south)
SOUTH_BASES = ["firewatch_station", "southern_redoubt", "spear_point_base"]
NORTH_TARGETS = {
    "cities": [
        {"id": "arktholm", "x_km": 418.3, "y_km": 95.0, "is_capital": True},
        {"id": "valbrek", "x_km": 1423.3, "y_km": 213.3},
        {"id": "nordvik", "x_km": 140.0, "y_km": 323.3},
    ],
    "bases": [
        {"id": "northern_vanguard", "x_km": 198.3, "y_km": 335.0},
        {"id": "highridge_command", "x_km": 838.3, "y_km": 75.0},
        {"id": "boreal_watch_post", "x_km": 1158.3, "y_km": 385.0},
    ],
}
AIRCRAFT_TYPES = ["bomber", "combat_plane", "uav", "drone_swarm"]


def _random_target(rng: random.Random) -> AttackTarget:
    pool = NORTH_TARGETS["cities"] + NORTH_TARGETS["bases"]
    t = rng.choice(pool)
    return AttackTarget(
        type="city" if "is_capital" in t or t["id"] in ["arktholm", "valbrek", "nordvik"] else "base",
        id=t["id"],
        x_km=t["x_km"],
        y_km=t["y_km"],
    )


def generate_random_plan(seed: int | None = None) -> AttackPlan:
    rng = random.Random(seed)
    plan_id = f"rnd-{uuid.uuid4().hex[:8]}"

    # Decide attack style
    num_waves = rng.randint(2, 6)
    actions: list[AttackAction] = []

    current_tick = rng.randint(1, 15)

    for wave in range(num_waves):
        # Pick a target for this wave
        target = _random_target(rng)

        # Pick aircraft types and counts for this wave
        num_types = rng.randint(1, 3)
        selected_types = rng.sample(AIRCRAFT_TYPES, min(num_types, len(AIRCRAFT_TYPES)))

        for ac_type in selected_types:
            base = rng.choice(SOUTH_BASES)
            count = rng.randint(1, 6)

            actions.append(AttackAction(
                tick=current_tick,
                type=AttackActionType.LAUNCH,
                aircraft_type=ac_type,
                count=count,
                from_base=base,
                target=target,
            ))

        # Sometimes add a regroup between waves
        if rng.random() < 0.3 and wave < num_waves - 1:
            regroup_tick = current_tick + rng.randint(20, 50)
            actions.append(AttackAction(
                tick=regroup_tick,
                type=AttackActionType.RTB,
                aircraft_type="all",
                target=AttackTarget(type="nearest_base"),
            ))

        # Gap between waves
        current_tick += rng.randint(30, 120)

    # Maybe a final all-out push
    if rng.random() < 0.4:
        capital_target = AttackTarget(type="city", id="arktholm", x_km=418.3, y_km=95.0)
        actions.append(AttackAction(
            tick=current_tick,
            type=AttackActionType.LAUNCH,
            aircraft_type="all",
            count=0,
            from_base=None,
            target=capital_target,
        ))

    # Describe the plan
    target_names = list({a.target.id for a in actions if a.target and a.target.id})
    desc = f"Random {num_waves}-wave attack targeting {', '.join(target_names[:3])}"

    return AttackPlan(
        id=plan_id,
        name=f"Random Plan #{seed or rng.randint(1,9999)}",
        source=AttackPlanSource.RANDOM,
        description=desc,
        actions=sorted(actions, key=lambda a: a.tick),
        created_at=datetime.now(timezone.utc).isoformat(),
        tags=["random", f"waves:{num_waves}"],
    )


def generate_random_plans(count: int, base_seed: int = 1) -> list[AttackPlan]:
    return [generate_random_plan(seed=base_seed + i) for i in range(count)]

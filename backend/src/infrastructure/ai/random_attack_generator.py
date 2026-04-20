"""Random attack plan generator (no LLM) — for seeding libraries quickly."""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timezone

from src.domain.value_objects.attack_plan import (
    AbortConditions,
    AttackAction,
    AttackActionType,
    AttackPlan,
    AttackPlanSource,
    AttackTarget,
)
from src.domain.value_objects.settings import Settings


def generate_random_plan(settings: Settings, seed: int | None = None) -> AttackPlan:
    rng = random.Random(seed)
    plan_id = f"rnd-{uuid.uuid4().hex[:8]}"

    # Who is attacker? South by convention
    attacker_bases = settings.scenario.get("bases", {}).get("south", [])
    attacker_resources = settings.attacker_resources  # dict of {base_id: {type: count}}
    defender_targets: list[tuple[str, str]] = []      # (id, type)

    for c in settings.scenario.get("cities", {}).get("north", []):
        defender_targets.append((c["id"], "city"))
    for b in settings.scenario.get("bases", {}).get("north", []):
        defender_targets.append((b["id"], "base"))

    if not attacker_bases or not defender_targets:
        return AttackPlan(
            plan_id=plan_id,
            settings_id=settings.settings_id,
            pattern_id=None,
            name="Random Plan (empty scenario)",
            description="",
            source=AttackPlanSource.RANDOM,
            actions=[],
            tags=["random"],
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    # Track available units per base per type
    available: dict[str, dict[str, int]] = {
        bid: dict(types) for bid, types in attacker_resources.items()
    }

    num_waves = rng.randint(2, 5)
    current_tick = rng.randint(1, 10)
    actions: list[AttackAction] = []

    for _wave in range(num_waves):
        target_id, target_type = rng.choice(defender_targets)

        # Pick 1-3 aircraft types to participate in this wave
        types_this_wave = rng.sample(
            ["bomber", "combat_plane", "uav", "drone_swarm"],
            k=rng.randint(1, 3),
        )
        for ac_type in types_this_wave:
            # Find a base with this type available
            candidate_bases = [
                b for b, types in available.items()
                if types.get(ac_type, 0) > 0
            ]
            if not candidate_bases:
                continue
            base = rng.choice(candidate_bases)
            max_avail = available[base][ac_type]
            count = rng.randint(1, min(max_avail, 4))
            available[base][ac_type] -= count

            actions.append(AttackAction(
                tick=current_tick,
                type=AttackActionType.LAUNCH,
                aircraft_type=ac_type,
                count=count,
                from_base=base,
                target=AttackTarget(type=target_type, id=target_id),
                abort_conditions=AbortConditions(
                    p_success_threshold=rng.uniform(0.25, 0.45),
                    jettison_weapons_on_abort=True,
                ),
            ))
        current_tick += rng.randint(25, 90)

    desc = f"{num_waves}-wave random attack"
    return AttackPlan(
        plan_id=plan_id,
        settings_id=settings.settings_id,
        pattern_id=None,
        name=f"Random Plan #{seed or rng.randint(1, 9999)}",
        description=desc,
        source=AttackPlanSource.RANDOM,
        actions=sorted(actions, key=lambda a: a.tick),
        tags=["random", f"waves:{num_waves}"],
        created_at=datetime.now(timezone.utc).isoformat(),
    )

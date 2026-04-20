from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

from ..value_objects.attack_pattern import AttackPattern
from ..value_objects.attack_plan import AttackPlan, AttackActionType


def extract_pattern(plan: AttackPlan) -> AttackPattern:
    """
    Deterministic pattern extraction from an attack plan. Two plans with the
    same tactical shape produce the same pattern_id and therefore share
    knowledge-base lessons.
    """
    # ==== Force composition (total by aircraft type across all launches) ====
    forces: Counter[str] = Counter()
    targets_hit: list[str] = []
    bases_used: list[str] = []
    launch_ticks: list[int] = []

    for action in plan.actions:
        if action.type == AttackActionType.LAUNCH:
            if action.aircraft_type != "all":
                forces[action.aircraft_type] += max(1, action.count)
            if action.target and action.target.id:
                targets_hit.append(action.target.id)
            if action.from_base:
                bases_used.append(action.from_base)
            launch_ticks.append(action.tick)

    # ==== Wave count: cluster launches by tick gaps >= 30 ticks apart ====
    wave_count = _count_waves(launch_ticks, gap_threshold=30)

    # ==== Feature tags ====
    tags: list[str] = []
    total_aircraft = sum(forces.values())
    if wave_count >= 3:
        tags.append("multi_wave")
    elif wave_count == 1:
        tags.append("single_wave")
    else:
        tags.append("dual_wave")

    # Force composition dominance
    if total_aircraft > 0:
        if forces.get("bomber", 0) / total_aircraft >= 0.35:
            tags.append("bomber_heavy")
        if forces.get("drone_swarm", 0) / total_aircraft >= 0.40:
            tags.append("drone_heavy")
        if forces.get("combat_plane", 0) / total_aircraft >= 0.35:
            tags.append("escorted")
        if forces.get("uav", 0) / total_aircraft >= 0.30:
            tags.append("uav_heavy")

    # Target profile
    capital_hits = sum(1 for t in targets_hit if "capital" in t.lower() or t in ("arktholm", "meridia"))
    unique_targets = set(targets_hit)
    if capital_hits >= max(1, len(targets_hit) * 0.5):
        target_profile = "capital_primary"
    elif len(unique_targets) >= 3:
        target_profile = "distributed"
    elif any("base" in t or t in ("northern_vanguard", "highridge_command", "boreal_watch_post") for t in targets_hit):
        target_profile = "counter_air"
    else:
        target_profile = "city_focus"

    tags.append(target_profile)

    # Base diversity tag
    if len(set(bases_used)) >= 2:
        tags.append("multi_base_origin")

    # ==== Canonical description (short human-readable summary) ====
    forces_desc = ", ".join(f"{c} {t}" for t, c in forces.most_common())
    desc = (
        f"{wave_count}-wave attack ({total_aircraft} aircraft: {forces_desc}) "
        f"targeting {target_profile.replace('_', ' ')}"
    )

    # ==== Compute deterministic pattern_id ====
    pattern_id = AttackPattern.compute_id(
        settings_id=plan.settings_id,
        feature_tags=tags,
        force_composition=dict(forces),
        target_profile=target_profile,
        wave_count=wave_count,
    )

    return AttackPattern(
        pattern_id=pattern_id,
        settings_id=plan.settings_id,
        canonical_description=desc,
        feature_tags=tags,
        force_composition=dict(forces),
        target_profile=target_profile,
        wave_count=wave_count,
        first_seen_at=datetime.now(timezone.utc).isoformat(),
    )


def _count_waves(ticks: list[int], gap_threshold: int = 30) -> int:
    """Cluster a sorted list of launch ticks into waves by gap threshold."""
    if not ticks:
        return 0
    sorted_ticks = sorted(ticks)
    waves = 1
    prev = sorted_ticks[0]
    for t in sorted_ticks[1:]:
        if t - prev >= gap_threshold:
            waves += 1
        prev = t
    return waves

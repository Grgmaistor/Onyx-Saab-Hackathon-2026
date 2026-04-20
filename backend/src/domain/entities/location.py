from __future__ import annotations

from dataclasses import dataclass, field

from .aircraft import Side
from ..value_objects.damage_model import (
    AIRCRAFT_WEAPON_TYPE,
    DamageThreshold,
    LocationArchetype,
    LocationEffect,
    LocationEffectType,
    WeaponType,
    default_thresholds,
)
from ..value_objects.position import Position


@dataclass
class Location:
    """
    Unified entity for cities, capitals, and air bases. Behavior differs by
    archetype: thresholds, effects on damage.

    Thresholds are checked after weapons are applied via `apply_weapons()`.
    Returns list of structured event dicts describing what happened.
    """
    id: str
    name: str
    side: Side
    position: Position
    archetype: LocationArchetype
    population: int = 0                 # initial; decreases with casualties

    # Air-base fields (ignored for cities/capital)
    max_aircraft_capacity: int = 0
    fuel_storage: float = 0.0
    fuel_storage_max: float = 0.0
    fuel_resupply_rate: float = 0.0
    current_aircraft: list[str] = field(default_factory=list)

    # Damage tracking (all archetypes)
    weapon_hits: dict[str, int] = field(default_factory=dict)    # weapon_type → count
    fired_one_shot_thresholds: set[str] = field(default_factory=set)
    casualties: int = 0
    casualty_multiplier: float = 1.0
    launch_capacity_multiplier: float = 1.0
    refuel_rate_multiplier: float = 1.0
    is_destroyed: bool = False
    is_launch_disabled: bool = False
    thresholds: list[DamageThreshold] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.thresholds:
            self.thresholds = default_thresholds(self.archetype)

    # ==== Queries ====
    @property
    def is_operational(self) -> bool:
        """Can this location currently service aircraft operations?"""
        return not self.is_destroyed and not self.is_launch_disabled

    @property
    def is_capital(self) -> bool:
        return self.archetype == LocationArchetype.CAPITAL

    @property
    def is_city(self) -> bool:
        return self.archetype in (LocationArchetype.CAPITAL, LocationArchetype.MAJOR_CITY)

    @property
    def is_base(self) -> bool:
        return self.archetype in (LocationArchetype.AIR_BASE, LocationArchetype.FORWARD_BASE)

    @property
    def available_capacity(self) -> int:
        if not self.is_operational:
            return 0
        return max(0, self.max_aircraft_capacity - len(self.current_aircraft))

    # ==== Damage application ====
    def apply_weapons(
        self,
        weapon_type: WeaponType,
        count: int,
        attacker_id: str = "",
    ) -> list[dict]:
        """
        Apply `count` hits of `weapon_type` to this location.
        Returns list of structured event dicts describing damage effects.

        For an already-destroyed location, returns empty list (no further damage).
        """
        if self.is_destroyed:
            return []

        wt_key = weapon_type.value
        old_count = self.weapon_hits.get(wt_key, 0)
        new_count = old_count + count
        self.weapon_hits[wt_key] = new_count

        events: list[dict] = []

        # Evaluate all thresholds for this weapon type
        for threshold in self.thresholds:
            if threshold.weapon_type != weapon_type:
                continue
            if threshold.requires_not_destroyed and self.is_destroyed:
                continue

            if threshold.repeatable:
                # Fire once per full multiple crossed this tick
                old_mult = old_count // threshold.threshold_count
                new_mult = new_count // threshold.threshold_count
                fires = new_mult - old_mult
                for _ in range(fires):
                    events.extend(self._apply_effects(threshold, attacker_id))
            else:
                # One-shot: fire only if just crossed and not already fired
                if threshold.name in self.fired_one_shot_thresholds:
                    continue
                if new_count >= threshold.threshold_count:
                    events.extend(self._apply_effects(threshold, attacker_id))
                    self.fired_one_shot_thresholds.add(threshold.name)

        return events

    def _apply_effects(self, threshold: DamageThreshold, attacker_id: str) -> list[dict]:
        """Apply a threshold's effects, return event dicts."""
        events: list[dict] = []
        for effect in threshold.effects:
            event = self._apply_single_effect(effect, threshold, attacker_id)
            if event:
                events.append(event)
        return events

    def _apply_single_effect(
        self,
        effect: LocationEffect,
        threshold: DamageThreshold,
        attacker_id: str,
    ) -> dict | None:
        et = effect.type
        params = effect.params

        if et == LocationEffectType.KILL_CIVILIANS:
            base_count = params.get("count", 0)
            count = int(base_count * self.casualty_multiplier)
            count = min(count, max(0, self.population - self.casualties))
            self.casualties += count
            return {
                "type": "civilian_casualties",
                "location_id": self.id,
                "location_name": self.name,
                "casualties": count,
                "cumulative_casualties": self.casualties,
                "weapon_type": threshold.weapon_type.value,
                "threshold": threshold.name,
                "attacker_id": attacker_id,
            }

        if et == LocationEffectType.DESTROY_PARKED_AIRCRAFT:
            # Signal only — the simulation engine handles actual aircraft state
            count = params.get("count", 0)
            return {
                "type": "destroy_parked_aircraft_request",
                "location_id": self.id,
                "location_name": self.name,
                "count": count,
                "weapon_type": threshold.weapon_type.value,
                "threshold": threshold.name,
                "attacker_id": attacker_id,
            }

        if et == LocationEffectType.REDUCE_LAUNCH_CAPACITY:
            mult = params.get("multiplier", 0.5)
            self.launch_capacity_multiplier *= mult
            return {
                "type": "launch_capacity_reduced",
                "location_id": self.id,
                "location_name": self.name,
                "new_multiplier": self.launch_capacity_multiplier,
                "weapon_type": threshold.weapon_type.value,
                "threshold": threshold.name,
            }

        if et == LocationEffectType.HALT_REFUEL:
            mult = params.get("multiplier", 0.0)
            self.refuel_rate_multiplier *= mult
            return {
                "type": "refuel_rate_reduced",
                "location_id": self.id,
                "location_name": self.name,
                "new_multiplier": self.refuel_rate_multiplier,
                "weapon_type": threshold.weapon_type.value,
                "threshold": threshold.name,
            }

        if et == LocationEffectType.DISABLE_LAUNCH:
            self.is_launch_disabled = True
            return {
                "type": "launch_disabled",
                "location_id": self.id,
                "location_name": self.name,
                "weapon_type": threshold.weapon_type.value,
                "threshold": threshold.name,
            }

        if et == LocationEffectType.DESTROY_LOCATION:
            self.is_destroyed = True
            self.is_launch_disabled = True
            return {
                "type": "location_destroyed",
                "location_id": self.id,
                "location_name": self.name,
                "archetype": self.archetype.value,
                "weapon_type": threshold.weapon_type.value,
                "threshold": threshold.name,
                "cumulative_casualties": self.casualties,
            }

        if et == LocationEffectType.INCREASE_CASUALTY_MULTIPLIER:
            mult = params.get("multiplier", 1.2)
            self.casualty_multiplier *= mult
            return {
                "type": "casualty_multiplier_increased",
                "location_id": self.id,
                "location_name": self.name,
                "new_multiplier": self.casualty_multiplier,
                "threshold": threshold.name,
            }

        return None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "side": self.side.value,
            "position": [self.position.x_km, self.position.y_km],
            "archetype": self.archetype.value,
            "population": self.population,
            "casualties": self.casualties,
            "is_destroyed": self.is_destroyed,
            "is_launch_disabled": self.is_launch_disabled,
            "is_operational": self.is_operational,
            "casualty_multiplier": round(self.casualty_multiplier, 3),
            "launch_capacity_multiplier": round(self.launch_capacity_multiplier, 3),
            "refuel_rate_multiplier": round(self.refuel_rate_multiplier, 3),
            "weapon_hits": dict(self.weapon_hits),
            "fuel_storage": round(self.fuel_storage, 1),
            "max_aircraft_capacity": self.max_aircraft_capacity,
            "aircraft_count": len(self.current_aircraft),
        }

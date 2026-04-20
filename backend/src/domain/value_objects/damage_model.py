from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class WeaponType(str, Enum):
    BULLETS = "bullets"       # cannon rounds; cannot destroy structures
    MISSILES = "missiles"     # guided munitions; can destroy structures
    BOMBS = "bombs"           # heavy ordnance; most destructive
    DRONES = "drones"         # kamikaze one-way munitions


class LocationArchetype(str, Enum):
    CAPITAL = "capital"
    MAJOR_CITY = "major_city"
    AIR_BASE = "air_base"
    FORWARD_BASE = "forward_base"


class LocationEffectType(str, Enum):
    KILL_CIVILIANS = "kill_civilians"
    DESTROY_PARKED_AIRCRAFT = "destroy_parked_aircraft"
    REDUCE_LAUNCH_CAPACITY = "reduce_launch_capacity"
    DISABLE_LAUNCH = "disable_launch"
    HALT_REFUEL = "halt_refuel"
    DESTROY_LOCATION = "destroy_location"
    INCREASE_CASUALTY_MULTIPLIER = "increase_casualty_multiplier"


@dataclass(frozen=True)
class LocationEffect:
    type: LocationEffectType
    params: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"type": self.type.value, "params": self.params}


@dataclass(frozen=True)
class DamageThreshold:
    """
    A checkpoint that fires effects when cumulative weapon hits reach a count.

    Repeatable thresholds fire every `threshold_count` hits (e.g., every
    500 bullets destroys 1 parked aircraft).

    One-shot thresholds fire exactly once when reached (e.g., after 5 missiles,
    the base is destroyed).
    """
    name: str
    weapon_type: WeaponType
    threshold_count: int
    repeatable: bool
    effects: list[LocationEffect]
    requires_not_destroyed: bool = True

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "weapon_type": self.weapon_type.value,
            "threshold_count": self.threshold_count,
            "repeatable": self.repeatable,
            "effects": [e.to_dict() for e in self.effects],
            "requires_not_destroyed": self.requires_not_destroyed,
        }


# ==== Weapon delivery per aircraft type ====
# When a striker reaches its ground target, each ammo unit delivers one weapon
# of this type to the target.
AIRCRAFT_WEAPON_TYPE: dict[str, WeaponType] = {
    "bomber": WeaponType.BOMBS,
    "uav": WeaponType.MISSILES,
    "drone_swarm": WeaponType.DRONES,
    "combat_plane": WeaponType.MISSILES,  # rare — only if ordered to ground strike
}


# ==== Default threshold profiles per archetype ====
# All numbers configurable per Settings.engagement_params.damage_model.

def capital_thresholds() -> list[DamageThreshold]:
    """
    Capital can be damaged by ALL weapon types.
    All weapons kill civilians (repeatable).
    Missiles and bombs eventually destroy the capital (one-shot).
    Bullets and drones never fully destroy (too small).
    """
    return [
        # Repeatable civilian casualties
        DamageThreshold(
            "capital_bullets_civilians",
            WeaponType.BULLETS, 100, True,
            [LocationEffect(LocationEffectType.KILL_CIVILIANS, {"count": 50})],
        ),
        DamageThreshold(
            "capital_missile_civilians",
            WeaponType.MISSILES, 1, True,
            [LocationEffect(LocationEffectType.KILL_CIVILIANS, {"count": 500})],
        ),
        DamageThreshold(
            "capital_bomb_civilians",
            WeaponType.BOMBS, 1, True,
            [LocationEffect(LocationEffectType.KILL_CIVILIANS, {"count": 5000})],
        ),
        DamageThreshold(
            "capital_drone_civilians",
            WeaponType.DRONES, 1, True,
            [LocationEffect(LocationEffectType.KILL_CIVILIANS, {"count": 100})],
        ),

        # One-shot escalation — casualty multiplier increases
        DamageThreshold(
            "capital_infrastructure_degraded_missiles",
            WeaponType.MISSILES, 10, False,
            [LocationEffect(LocationEffectType.INCREASE_CASUALTY_MULTIPLIER, {"multiplier": 1.2})],
        ),
        DamageThreshold(
            "capital_infrastructure_degraded_bombs",
            WeaponType.BOMBS, 3, False,
            [LocationEffect(LocationEffectType.INCREASE_CASUALTY_MULTIPLIER, {"multiplier": 1.2})],
        ),
        DamageThreshold(
            "capital_near_collapse_missiles",
            WeaponType.MISSILES, 25, False,
            [LocationEffect(LocationEffectType.INCREASE_CASUALTY_MULTIPLIER, {"multiplier": 2.0})],
        ),
        DamageThreshold(
            "capital_near_collapse_bombs",
            WeaponType.BOMBS, 8, False,
            [LocationEffect(LocationEffectType.INCREASE_CASUALTY_MULTIPLIER, {"multiplier": 2.0})],
        ),

        # One-shot destruction (game-loss condition)
        DamageThreshold(
            "capital_destroyed_missiles",
            WeaponType.MISSILES, 40, False,
            [LocationEffect(LocationEffectType.DESTROY_LOCATION)],
        ),
        DamageThreshold(
            "capital_destroyed_bombs",
            WeaponType.BOMBS, 12, False,
            [LocationEffect(LocationEffectType.DESTROY_LOCATION)],
        ),
    ]


def major_city_thresholds() -> list[DamageThreshold]:
    """
    Major cities: similar to capital but smaller scale, lower destruction threshold.
    Destruction is a big metric hit but not a loss condition.
    """
    return [
        # Civilian casualties (repeatable)
        DamageThreshold(
            "city_bullets_civilians",
            WeaponType.BULLETS, 100, True,
            [LocationEffect(LocationEffectType.KILL_CIVILIANS, {"count": 30})],
        ),
        DamageThreshold(
            "city_missile_civilians",
            WeaponType.MISSILES, 1, True,
            [LocationEffect(LocationEffectType.KILL_CIVILIANS, {"count": 300})],
        ),
        DamageThreshold(
            "city_bomb_civilians",
            WeaponType.BOMBS, 1, True,
            [LocationEffect(LocationEffectType.KILL_CIVILIANS, {"count": 3000})],
        ),
        DamageThreshold(
            "city_drone_civilians",
            WeaponType.DRONES, 1, True,
            [LocationEffect(LocationEffectType.KILL_CIVILIANS, {"count": 60})],
        ),

        # One-shot destruction
        DamageThreshold(
            "city_destroyed_missiles",
            WeaponType.MISSILES, 15, False,
            [LocationEffect(LocationEffectType.DESTROY_LOCATION)],
        ),
        DamageThreshold(
            "city_destroyed_bombs",
            WeaponType.BOMBS, 5, False,
            [LocationEffect(LocationEffectType.DESTROY_LOCATION)],
        ),
    ]


def air_base_thresholds() -> list[DamageThreshold]:
    """
    Air base: mainstream military target.
    - Bullets CANNOT destroy the base itself but CAN damage parked aircraft
    - Missiles/bombs destroy parked aircraft and eventually the base
    - When base is destroyed: cannot launch/land, parked aircraft destroyed
    """
    return [
        # Repeatable — parked aircraft damage
        DamageThreshold(
            "airbase_bullets_parked",
            WeaponType.BULLETS, 500, True,
            [LocationEffect(LocationEffectType.DESTROY_PARKED_AIRCRAFT, {"count": 1})],
        ),
        DamageThreshold(
            "airbase_missile_parked",
            WeaponType.MISSILES, 1, True,
            [LocationEffect(LocationEffectType.DESTROY_PARKED_AIRCRAFT, {"count": 2})],
        ),
        DamageThreshold(
            "airbase_bomb_parked",
            WeaponType.BOMBS, 1, True,
            [LocationEffect(LocationEffectType.DESTROY_PARKED_AIRCRAFT, {"count": 5})],
        ),
        DamageThreshold(
            "airbase_drone_parked",
            WeaponType.DRONES, 3, True,
            [LocationEffect(LocationEffectType.DESTROY_PARKED_AIRCRAFT, {"count": 1})],
        ),

        # One-shot capability degradation
        DamageThreshold(
            "airbase_launch_halved_missiles",
            WeaponType.MISSILES, 3, False,
            [LocationEffect(LocationEffectType.REDUCE_LAUNCH_CAPACITY, {"multiplier": 0.5}),
             LocationEffect(LocationEffectType.HALT_REFUEL, {"multiplier": 0.5})],
        ),
        DamageThreshold(
            "airbase_launch_halved_bombs",
            WeaponType.BOMBS, 1, False,
            [LocationEffect(LocationEffectType.REDUCE_LAUNCH_CAPACITY, {"multiplier": 0.5}),
             LocationEffect(LocationEffectType.HALT_REFUEL, {"multiplier": 0.5})],
        ),

        # One-shot destruction (base inactive, all parked aircraft destroyed)
        DamageThreshold(
            "airbase_destroyed_missiles",
            WeaponType.MISSILES, 5, False,
            [LocationEffect(LocationEffectType.DISABLE_LAUNCH),
             LocationEffect(LocationEffectType.DESTROY_LOCATION)],
        ),
        DamageThreshold(
            "airbase_destroyed_bombs",
            WeaponType.BOMBS, 2, False,
            [LocationEffect(LocationEffectType.DISABLE_LAUNCH),
             LocationEffect(LocationEffectType.DESTROY_LOCATION)],
        ),
    ]


def forward_base_thresholds() -> list[DamageThreshold]:
    """Forward base: smaller than air base, easier to knock out."""
    return [
        DamageThreshold(
            "fwdbase_bullets_parked",
            WeaponType.BULLETS, 500, True,
            [LocationEffect(LocationEffectType.DESTROY_PARKED_AIRCRAFT, {"count": 1})],
        ),
        DamageThreshold(
            "fwdbase_missile_parked",
            WeaponType.MISSILES, 1, True,
            [LocationEffect(LocationEffectType.DESTROY_PARKED_AIRCRAFT, {"count": 2})],
        ),
        DamageThreshold(
            "fwdbase_bomb_parked",
            WeaponType.BOMBS, 1, True,
            [LocationEffect(LocationEffectType.DESTROY_PARKED_AIRCRAFT, {"count": 3})],
        ),
        DamageThreshold(
            "fwdbase_drone_parked",
            WeaponType.DRONES, 2, True,
            [LocationEffect(LocationEffectType.DESTROY_PARKED_AIRCRAFT, {"count": 1})],
        ),
        DamageThreshold(
            "fwdbase_launch_halved_missiles",
            WeaponType.MISSILES, 2, False,
            [LocationEffect(LocationEffectType.REDUCE_LAUNCH_CAPACITY, {"multiplier": 0.5})],
        ),
        DamageThreshold(
            "fwdbase_destroyed_missiles",
            WeaponType.MISSILES, 3, False,
            [LocationEffect(LocationEffectType.DISABLE_LAUNCH),
             LocationEffect(LocationEffectType.DESTROY_LOCATION)],
        ),
        DamageThreshold(
            "fwdbase_destroyed_bombs",
            WeaponType.BOMBS, 2, False,
            [LocationEffect(LocationEffectType.DISABLE_LAUNCH),
             LocationEffect(LocationEffectType.DESTROY_LOCATION)],
        ),
    ]


def default_thresholds(archetype: LocationArchetype) -> list[DamageThreshold]:
    """Get default thresholds for a location archetype."""
    return {
        LocationArchetype.CAPITAL: capital_thresholds(),
        LocationArchetype.MAJOR_CITY: major_city_thresholds(),
        LocationArchetype.AIR_BASE: air_base_thresholds(),
        LocationArchetype.FORWARD_BASE: forward_base_thresholds(),
    }[archetype]

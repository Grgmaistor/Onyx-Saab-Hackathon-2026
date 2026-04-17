# Implementation Guide: Deterrence and Air Denial Mechanics

## Overview

Add mechanics that model how fighter presence deters enemy operations without direct combat. This reflects real-world doctrine where most interceptions don't result in engagement, and a defender can "win" by preventing the attacker from reaching targets.

**Research basis**: `research/air_defense_intercept_doctrine.md`, `research/engagement_outcomes.md`

## Key Concepts

### What is Air Denial?

Air denial means preventing the enemy from freely operating in your airspace, without necessarily achieving air superiority. The defender achieves this by:
- **CAP presence**: Armed fighters on patrol force attackers to allocate escorts, reroute, or abort
- **Interception deterrence**: Meeting enemy aircraft with fighters causes mission abort even without shots fired
- **Attrition threat**: Making each enemy sortie risky enough that sustained operations become unsustainable

### Why This Matters for the Simulation

Currently, the simulation assumes:
- If aircraft meet, they fight
- "Winning" means destroying enemy aircraft
- Strategy success = kill count

In reality:
- Most interceptions don't lead to combat
- "Winning" means preventing the enemy from achieving objectives (bombing cities)
- A bomber that jettisons its payload to evade a fighter is a defensive success, even with zero kills

## Architecture

All changes in domain layer (pure, no external dependencies).

### New/Modified Files

```
backend/src/domain/
  value_objects/
    deterrence.py              # NEW - deterrence zone, effects
  services/
    deterrence_calculator.py   # NEW - compute deterrence effects
    combat_resolver.py         # MODIFY - add pre-engagement deterrence check
  entities/
    simulation.py              # MODIFY - add deterrence tracking to SimulationState
```

## Implementation Steps

### Step 1: Deterrence Value Object

#### `deterrence.py`

```python
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class DeterrenceZone:
    """A zone of fighter influence that affects enemy behavior."""
    center_x: float
    center_y: float
    radius_km: float
    strength: float              # 0.0 to 1.0, based on number/type of defenders
    defender_count: int
    primary_type: str            # Most common defender type in zone

@dataclass(frozen=True)
class DeterrenceEffect:
    """The effect of deterrence on a specific enemy aircraft."""
    aircraft_id: str
    deterrence_strength: float   # 0.0 to 1.0
    action: str                  # "proceed", "reroute", "abort", "jettison_weapons"
```

### Step 2: Deterrence Calculator (Domain Service)

#### `deterrence_calculator.py`

This is a pure function that computes deterrence effects each tick.

```python
from __future__ import annotations
import math
from random import Random

def compute_deterrence_zones(friendly_aircraft, friendly_bases) -> list[DeterrenceZone]:
    """
    Compute zones of deterrence based on friendly aircraft positions.
    
    Each airborne fighter creates a deterrence zone around it.
    Overlapping zones combine for stronger deterrence.
    Bases with grounded aircraft provide a weaker "potential" deterrence.
    """
    zones = []
    
    for ac in friendly_aircraft:
        if ac.state == AircraftState.AIRBORNE and ac.ammo_current > 0:
            # Airborne armed fighter creates strong deterrence
            radius = _deterrence_radius(ac.type)
            strength = _deterrence_strength(ac.type, ac.ammo_current, ac.fuel_current / ac.fuel_capacity)
            zones.append(DeterrenceZone(
                center_x=ac.position.x_km,
                center_y=ac.position.y_km,
                radius_km=radius,
                strength=strength,
                defender_count=1,
                primary_type=ac.type.value,
            ))
    
    # Merge overlapping zones (optional, simplifies computation)
    return _merge_overlapping_zones(zones)


def _deterrence_radius(aircraft_type: AircraftType) -> float:
    """Deterrence radius in km, based on aircraft speed and weapon range."""
    return {
        AircraftType.COMBAT_PLANE: 150.0,   # Fast, BVR-capable
        AircraftType.UAV: 80.0,             # Slower, shorter weapon range
        AircraftType.DRONE_SWARM: 40.0,     # Short range
        AircraftType.BOMBER: 50.0,          # Limited A2A capability
    }.get(aircraft_type, 100.0)


def _deterrence_strength(aircraft_type, ammo, fuel_fraction) -> float:
    """Deterrence strength 0.0-1.0 based on aircraft capability."""
    base = {
        AircraftType.COMBAT_PLANE: 0.8,
        AircraftType.UAV: 0.3,
        AircraftType.DRONE_SWARM: 0.2,
        AircraftType.BOMBER: 0.15,
    }.get(aircraft_type, 0.5)
    
    # Reduce if low ammo or fuel
    if ammo == 0:
        base *= 0.1  # Unarmed aircraft has almost no deterrence
    if fuel_fraction < 0.2:
        base *= 0.5  # Low fuel = likely leaving soon
    
    return min(base, 1.0)


def apply_deterrence(
    enemy_aircraft: list,
    deterrence_zones: list[DeterrenceZone],
    rng: Random,
) -> list[DeterrenceEffect]:
    """
    For each enemy aircraft, check if it's in a deterrence zone.
    If so, roll to see if it's deterred based on zone strength.
    
    Deterrence effects:
    - Bombers are most affected (they're the ones with objectives to abort)
    - Combat planes are least affected (they're there to fight)
    - Cumulative deterrence from multiple defenders increases effect
    
    Returns list of DeterrenceEffect for affected aircraft.
    """
    effects = []
    
    for enemy in enemy_aircraft:
        if enemy.state != AircraftState.AIRBORNE:
            continue
        
        # Find the strongest deterrence zone this aircraft is in
        max_deterrence = 0.0
        for zone in deterrence_zones:
            dist = math.sqrt(
                (enemy.position.x_km - zone.center_x) ** 2
                + (enemy.position.y_km - zone.center_y) ** 2
            )
            if dist < zone.radius_km:
                # Deterrence decreases with distance from center
                proximity_factor = 1.0 - (dist / zone.radius_km)
                effective = zone.strength * proximity_factor
                max_deterrence = max(max_deterrence, effective)
        
        if max_deterrence <= 0:
            effects.append(DeterrenceEffect(enemy.id, 0.0, "proceed"))
            continue
        
        # Type-specific deterrence sensitivity
        sensitivity = {
            AircraftType.BOMBER: 1.5,          # Bombers are very sensitive to deterrence
            AircraftType.DRONE_SWARM: 0.8,     # Swarms are somewhat expendable
            AircraftType.UAV: 1.0,             # Moderate sensitivity
            AircraftType.COMBAT_PLANE: 0.5,    # Fighters are least deterred
        }.get(enemy.type, 1.0)
        
        adjusted_deterrence = min(max_deterrence * sensitivity, 0.95)
        
        # Roll for deterrence effect
        roll = rng.random()
        if roll < adjusted_deterrence * 0.3:
            # Strong deterrence: abort mission entirely
            action = "abort"
        elif roll < adjusted_deterrence * 0.6:
            # Medium deterrence: jettison weapons, evade
            action = "jettison_weapons" if enemy.type == AircraftType.BOMBER else "reroute"
        elif roll < adjusted_deterrence * 0.8:
            # Light deterrence: reroute around zone
            action = "reroute"
        else:
            # Not deterred this tick
            action = "proceed"
        
        effects.append(DeterrenceEffect(enemy.id, adjusted_deterrence, action))
    
    return effects
```

### Step 3: Integrate into Tick Loop

Add deterrence computation between the DETECT and DECIDE phases:

```
TICK N:
  1. DETECT     Scan for enemy aircraft
  2. DETER      Compute deterrence zones, apply to enemy   <-- NEW
  3. DECIDE     Strategy evaluates state
  4. MOVE       Aircraft travel
  5. ENGAGE     Resolve combats (only for non-deterred aircraft)
  6. DAMAGE     Cities under attack (reduced by deterrence)
  7. SERVICE    Refuel/rearm
  8. RECORD     Snapshot state
  9. CHECK      Termination conditions
```

### Step 4: Handle Deterrence Effects

When an enemy aircraft is deterred:

- **"abort"**: Enemy aircraft turns around and heads back to base. Remove from active threats. This is the strongest defensive success.
- **"jettison_weapons"**: Bomber drops payload (wasted, no city damage) and evades. Effectively a mission kill without combat.
- **"reroute"**: Enemy aircraft changes heading to avoid deterrence zone. Increases fuel consumption, delays arrival. May cause the attack to fail due to fuel.
- **"proceed"**: No effect, enemy continues as planned.

### Step 5: New Metrics

Add to `SimulationMetrics`:

```python
# Deterrence metrics
enemy_sorties_deterred: int          # How many enemy missions aborted/rerouted
enemy_weapons_jettisoned: int        # How many enemy bombers forced to jettison
air_denial_score: float              # Fraction of enemy sorties that failed to reach targets
deterrence_efficiency: float         # Deterred sorties per friendly sortie flown
```

### Step 6: Strategy Awareness

Strategies should be able to see deterrence zone information in `SimulationState` so they can position patrols for maximum deterrence:

```python
# Add to SimulationState
deterrence_zones: list[DeterrenceZone]  # Current friendly deterrence coverage
```

## Testing

1. `test_deterrence_zone_created_for_airborne_fighter` -- Airborne armed fighter produces a zone
2. `test_no_deterrence_from_unarmed_aircraft` -- Aircraft with 0 ammo has near-zero deterrence
3. `test_bomber_more_sensitive_to_deterrence` -- Bombers deterred at lower strength than fighters
4. `test_deterrence_decreases_with_distance` -- Zone edge has lower effect than center
5. `test_deterred_bomber_aborts_mission` -- Seed RNG to get "abort", verify bomber turns back
6. `test_deterrence_prevents_city_damage` -- Deterred bomber does not damage city
7. `test_multiple_defenders_increase_deterrence` -- Overlapping zones are stronger

## Simplified Version (If Time-Constrained)

Minimal implementation:
1. Skip zone computation -- just check distance between friendly fighters and enemy bombers
2. If a friendly combat_plane is within 150km of an enemy bomber, roll P=0.3 for the bomber to abort
3. Track "deterred" count as a metric

This gives the core deterrence behavior in ~30 lines of code.

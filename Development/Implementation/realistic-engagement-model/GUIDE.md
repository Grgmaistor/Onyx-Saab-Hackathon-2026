# Implementation Guide: Realistic Engagement Model

## Overview

Replace the current binary kill/destroyed engagement model with a multi-step probabilistic engagement that reflects real-world BVR air combat. This is the highest-impact change for simulation realism.

**Research basis**: `research/engagement_outcomes.md`, `research/air_defense_intercept_doctrine.md`, `research/combat_probabilities.md`

## What Changes

### Current Model (Replace)
- Two aircraft meet within `engagement_range_km` (50km)
- Single random roll against `combat_matchups` probability matrix
- Loser is instantly DESTROYED
- Winner loses 1 ammo

### New Model (Implement)

An engagement is a **multi-round BVR exchange** with detection, missile shots, evasion, damage assessment, and disengagement decisions.

## Architecture

All new code follows hexagonal architecture. Domain layer only.

### New/Modified Files

```
backend/src/domain/
  value_objects/
    engagement_result.py       # NEW - replaces simple CombatResult
    damage_state.py            # NEW - aircraft damage tracking
  services/
    combat_resolver.py         # MODIFY - replace single-roll with multi-step
    engagement_engine.py       # NEW - the core engagement resolution logic
  entities/
    aircraft.py                # MODIFY - add damage_level, add DAMAGED state
```

## Domain Changes

### 1. New Value Objects

#### `engagement_result.py`

```python
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class EngagementOutcome(str, Enum):
    HARD_KILL = "hard_kill"           # Aircraft destroyed
    MISSION_KILL = "mission_kill"     # Aircraft damaged, combat-ineffective, RTB
    DAMAGED_RTB = "damaged_rtb"       # Aircraft damaged but flyable, RTB for repair
    EVADED = "evaded"                 # Missile missed, aircraft evaded
    DISENGAGED = "disengaged"         # Broke off engagement (fuel/ammo/tactical)
    DETERRED = "deterred"             # Enemy turned back without shots fired
    NO_ENGAGEMENT = "no_engagement"   # Detection without engagement (ROE, range)

@dataclass(frozen=True)
class EngagementResult:
    attacker_id: str
    defender_id: str
    attacker_outcome: EngagementOutcome
    defender_outcome: EngagementOutcome
    missiles_fired_attacker: int
    missiles_fired_defender: int
    rounds_fought: int                # How many BVR exchange rounds
    collateral_damage: float          # Damage to nearby city if applicable
```

#### `damage_state.py`

```python
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class DamageLevel(str, Enum):
    NONE = "none"
    LIGHT = "light"           # Hours to repair, may continue mission
    MODERATE = "moderate"     # Mission kill, RTB, 12-72 hours repair
    HEAVY = "heavy"           # RTB only, days to weeks repair
    DESTROYED = "destroyed"   # Aircraft lost

@dataclass(frozen=True)
class DamageState:
    level: DamageLevel
    speed_reduction: float       # 0.0 to 0.5 (fraction of speed lost)
    weapons_operational: bool    # Can still fire weapons?
    repair_time_minutes: float   # Minutes to repair at base (0 if none)
```

### 2. Aircraft Entity Changes

Add to `Aircraft` dataclass:

```python
# New fields
damage_level: DamageLevel = DamageLevel.NONE
speed_modifier: float = 1.0        # Multiplied by speed_kmh for effective speed
repair_time_remaining: float = 0.0  # Minutes of repair remaining at base
```

Add new state to `AircraftState`:

```python
class AircraftState(str, Enum):
    # ... existing states ...
    DAMAGED = "damaged"          # Airborne but damaged, reduced capability
    REPAIRING = "repairing"      # At base, undergoing battle damage repair
```

### 3. Engagement Engine (Core Logic)

Create `engagement_engine.py` as a pure domain service:

```python
def resolve_engagement(
    attacker: Aircraft,
    defender: Aircraft,
    rng: Random,
    engagement_params: EngagementParams,
) -> EngagementResult:
    """
    Multi-step BVR engagement resolution.
    
    Steps:
    1. Detection advantage (who detects first)
    2. For each round (max 3 rounds):
       a. Attacker fires missile salvo
       b. Defender attempts evasion + countermeasures
       c. Roll for hit/miss
       d. If hit: roll for damage severity
       e. Defender returns fire (if able)
       f. Both sides assess: continue or disengage?
    3. Return engagement result with outcomes for both sides
    """
```

### 4. Engagement Parameters

```python
@dataclass(frozen=True)
class EngagementParams:
    # Base Pk by range
    pk_optimal_range: float = 0.45     # Base Pk at optimal BVR range
    pk_max_range: float = 0.15         # Base Pk at maximum range
    pk_wvr: float = 0.65              # Base Pk within visual range
    
    # Salvo
    missiles_per_salvo: int = 2        # Shoot-shoot doctrine
    max_rounds: int = 3                # Max BVR exchange rounds before disengage
    
    # Countermeasure modifiers (reduce Pk)
    cm_effectiveness: float = 0.15     # Chaff/flare Pk reduction
    ecm_effectiveness: float = 0.20    # EW suite Pk reduction (if equipped)
    maneuver_effectiveness: float = 0.10  # Defensive maneuver Pk reduction
    
    # Damage distribution (given a hit)
    p_hard_kill: float = 0.25          # Hit -> destroyed
    p_mission_kill: float = 0.35       # Hit -> combat-ineffective
    p_damage_rtb: float = 0.30        # Hit -> damaged, flyable
    p_light_damage: float = 0.10      # Hit -> minor, may continue
    
    # Repair times
    light_repair_minutes: float = 240.0      # 4 hours
    moderate_repair_minutes: float = 1440.0  # 24 hours
    heavy_repair_minutes: float = 7200.0     # 5 days
    
    # Disengagement triggers
    fuel_disengage_threshold: float = 0.20   # RTB if fuel below this
    ammo_disengage_threshold: int = 0        # RTB if ammo at this level
```

## Implementation Steps

### Step 1: Create value objects
Create `engagement_result.py` and `damage_state.py` in `domain/value_objects/`.
These are frozen dataclasses with no external dependencies.

### Step 2: Update Aircraft entity
Add `damage_level`, `speed_modifier`, `repair_time_remaining` fields.
Add `DAMAGED` and `REPAIRING` states to `AircraftState`.
Ensure backward compatibility -- default values mean existing code still works.

### Step 3: Create engagement engine
Create `engagement_engine.py` in `domain/services/`.
Implement `resolve_engagement()` as a pure function.
Use the simulation's seeded `rng` instance (never `random.random()`).

### Step 4: Modify combat resolver
Update `combat_resolver.py` to call the new engagement engine instead of the single-roll model.
The `resolve_engagements()` function signature can remain the same but returns `list[EngagementResult]` instead of `list[CombatResult]`.

### Step 5: Update SERVICE phase in tick loop
Add handling for `REPAIRING` state in the service phase.
Aircraft in `REPAIRING` state progress toward repair completion based on `repair_time_remaining`.
When repair completes, aircraft transitions to `GROUNDED` and is available for sorties.

### Step 6: Update SimulationTick recording
Include engagement details in the tick event log (missiles fired, rounds fought, outcomes).

### Step 7: Update termination conditions
`MISSION_KILL` and `DAMAGED_RTB` should NOT count as "destroyed" for termination.
Only `HARD_KILL` (via `DamageLevel.DESTROYED`) counts toward "all aircraft destroyed" check.

## Engagement Resolution Algorithm

```
resolve_engagement(attacker, defender, rng, params):
    missiles_fired_a = 0
    missiles_fired_d = 0
    
    for round in range(params.max_rounds):
        # --- Attacker fires ---
        if attacker.ammo_current > 0:
            salvo = min(params.missiles_per_salvo, attacker.ammo_current)
            missiles_fired_a += salvo
            attacker.ammo_current -= salvo
            
            # Calculate effective Pk per missile
            base_pk = params.pk_optimal_range  # Simplification: use optimal range
            effective_pk = base_pk - params.cm_effectiveness - params.maneuver_effectiveness
            effective_pk = clamp(effective_pk, 0.05, 0.95)
            
            # Salvo resolution: P(at least one hit) = 1 - (1-pk)^n
            p_hit = 1.0 - (1.0 - effective_pk) ** salvo
            
            if rng.random() < p_hit:
                # Hit! Determine damage severity
                roll = rng.random()
                if roll < params.p_hard_kill:
                    defender -> DESTROYED
                    return result
                elif roll < params.p_hard_kill + params.p_mission_kill:
                    defender -> MISSION_KILL (RTB, moderate repair)
                    # Defender may still return fire this round
                elif roll < params.p_hard_kill + params.p_mission_kill + params.p_damage_rtb:
                    defender -> DAMAGED (RTB, light-moderate repair)
                else:
                    defender -> LIGHT DAMAGE (may continue)
        
        # --- Defender returns fire (if able) ---
        # Mirror logic for defender shooting at attacker
        
        # --- Disengagement check ---
        # If either side is damaged, low fuel, or out of ammo: disengage
        if should_disengage(attacker) or should_disengage(defender):
            break
    
    # If max rounds reached without kill: mutual disengage
    return EngagementResult(...)
```

## Impact on Existing Strategies

The three existing strategies (defensive, aggressive, balanced) will work without modification because:
- They issue `INTERCEPT` decisions, not direct engagement commands
- The engagement engine handles what happens when aircraft meet
- RTB logic is already based on fuel thresholds

However, strategies should eventually be updated to consider:
- Damaged aircraft that RTB (don't re-intercept with them)
- Aircraft in `REPAIRING` state (not available for launch)
- Mission kills that remove bombers from the threat (success without destruction)

## Testing

### Domain unit tests (`tests/domain/test_engagement_engine.py`)

1. `test_engagement_hard_kill_destroys_aircraft` -- Seed RNG to guarantee hard kill, verify DESTROYED state
2. `test_engagement_mission_kill_rtb` -- Verify mission-killed aircraft transitions to RTB
3. `test_engagement_both_miss` -- All missiles miss, both disengage, both survive
4. `test_engagement_ammo_depleted_disengage` -- Aircraft with 0 ammo cannot fire, must disengage
5. `test_engagement_fuel_disengage` -- Low fuel triggers disengagement before max rounds
6. `test_engagement_damage_reduces_speed` -- Damaged aircraft has reduced speed_modifier
7. `test_repair_time_progression` -- Aircraft in REPAIRING state progresses toward completion
8. `test_engagement_deterministic_with_seed` -- Same seed produces same result

## Simplified Version (If Time-Constrained)

If full implementation is too complex for hackathon timeline, a simplified version:

1. Keep single-round engagement but add **outcome distribution**:
   - Roll combat_matchups probability as before
   - If "attacker wins": roll damage severity (25% kill, 35% mission-kill, 30% damage, 10% light)
   - If "defender wins": same damage distribution
2. Add `DAMAGED` and `REPAIRING` states
3. Skip multi-round BVR mechanics

This gives 80% of the realism improvement with 30% of the implementation effort.

# Pilot Reflexes — Layer 2 Autonomous Aircraft Behavior

This document specifies **what every aircraft in the simulation can decide on its own**, independent of the commander (playbook or LLM). These are reflexes: deterministic functions of the aircraft's own state + nearby observables.

## Why this layer exists

Pre-scripting every decision fails. If an attacking bomber gets intercepted far from target, it should abort — not because a script told it to, but because that's what pilots do. The commander shouldn't have to encode this; it's baked into how aircraft behave.

Pilot reflexes produce **emergent deterrence**: when defender fighters arrive near an incoming bomber, the bomber aborts on its own. The defense playbook only had to place the fighters there; the deterrence effect emerges automatically.

## The decision contract

Every tick, for every airborne aircraft, the simulation runs this sequence **before the commander's orders are applied**:

```
1. Safety reflexes (non-negotiable, override commander):
   a. Fuel below BINGO → RTB immediately
   b. Under missile attack → execute defensive maneuver
   c. Structural failure / critical damage → emergency RTB or crash

2. Mission-viability reflexes (aircraft's own judgement):
   d. Compute P(success)
   e. If P(success) < abort threshold → abort mission per aircraft type

3. Engagement reflexes (during combat only):
   f. Ammo depleted → disengage, RTB
   g. Wingman down + outnumbered → bug out
   h. Losing engagement badly → disengage

4. Commander's orders apply to remaining aircraft.
```

Commander (playbook/LLM) only sees aircraft whose reflexes haven't already taken control.

## Complete catalog of reflexes

Each reflex: a named function, inputs from aircraft state, deterministic output.

### 1. `bingo_fuel_rtb`

**Fires when:** `fuel_current / fuel_capacity < BINGO_THRESHOLD` (default 0.18)

**Action:** Set target to nearest operational friendly base. State → AIRBORNE (unchanged), but new target position. Commander cannot reassign until aircraft lands and fuel is replenished.

**Why:** Real pilots have non-negotiable fuel reserves for return trip. Below bingo = crash risk.

**Tunable per aircraft type:**
- combat_plane: 0.18
- bomber: 0.22 (heavier, burns more in emergency)
- uav: 0.15
- drone_swarm: 0.10 (one-way munitions bias)

### 2. `mission_viability_abort`

**Fires when:** `P(mission_success)` drops below abort threshold.

**Computation of P(mission_success):**

For an **attacking** aircraft (heading to hit target):
```
target_reachable_score = clamp(remaining_range / distance_to_target, 0, 1)
threat_proximity_score = 1 - clamp(distance_to_nearest_enemy / 400km, 0, 1)
matchup_advantage     = combat_matchup[my_type][nearest_enemy_type]  # 0 to 1
ammo_ready_score      = ammo_current / ammo_capacity
fuel_margin_score     = clamp((fuel_fraction - BINGO) / (1 - BINGO), 0, 1)

# Aircraft-type-specific weighting
if type == BOMBER:
    # Bombers most sensitive to threat proximity (they can't dogfight)
    p_success = 0.40 * target_reachable
              + 0.35 * (1 - threat_proximity_score)
              + 0.15 * matchup_advantage
              + 0.10 * fuel_margin

elif type == COMBAT_PLANE:
    # Fighters less deterred, more willing to engage
    p_success = 0.40 * matchup_advantage
              + 0.25 * ammo_ready
              + 0.20 * fuel_margin
              + 0.15 * target_reachable

elif type == UAV:
    # Mid-tier: sensitive to fighter presence but can still strike
    p_success = 0.30 * (1 - threat_proximity)
              + 0.25 * target_reachable
              + 0.20 * matchup_advantage
              + 0.15 * ammo_ready
              + 0.10 * fuel_margin

elif type == DRONE_SWARM:
    # One-way munitions: only abort on extreme hopelessness
    p_success = 0.50 * target_reachable
              + 0.25 * ammo_ready
              + 0.25 * (1 - threat_proximity)
```

**Abort thresholds (below which aircraft aborts):**
- combat_plane: 0.25 (fighters press the attack)
- bomber: 0.40 (bombers are cautious)
- uav: 0.35
- drone_swarm: 0.15 (near-zero abort — they're cheap)

**Action when aborting:**
- bomber: JETTISON_WEAPONS + RTB (drops payload, flees — this is the "deterrence" outcome)
- combat_plane: DISENGAGE + RTB (refuel/rearm)
- uav: RTB (preserves expensive platform)
- drone_swarm: CONTINUE (almost never aborts in practice)

### 3. `defensive_evasion`

**Fires when:** Aircraft detects a missile launched at it within the current tick.

**Action:** Reduces the effective Pk of the incoming missile (attacker's hit probability against this aircraft) by `MANEUVER_EFFECTIVENESS`:
- combat_plane: -0.15 Pk (aggressive evasion + countermeasures)
- bomber: -0.08 Pk (less agile, relies on chaff/flares)
- uav: -0.05 Pk (limited evasion capability)
- drone_swarm: 0 (no meaningful evasion)

**Secondary effect:** Aircraft's own offensive maneuver is disrupted — any missile it fires this tick has Pk reduced by 0.10 (disturbed shot).

**No state change:** Aircraft doesn't abort; it just evades the specific threat.

### 4. `ammo_depleted_disengage`

**Fires when:** `ammo_current == 0` AND aircraft is within engagement range of an enemy.

**Action:** Break off combat, set target to nearest friendly base. Cannot be reassigned to combat until rearmed.

**Why:** A fighter with no missiles cannot contribute to an engagement and is a liability.

### 5. `outnumbered_bugout`

**Fires when:** `friendly_count_in_engagement < enemy_count_in_engagement / BUGOUT_RATIO` where BUGOUT_RATIO = 2.0 for combat_plane, 1.2 for bomber.

**Action:** Disengage, RTB. Aircraft that already fired this tick commit to landing; don't return fire next tick.

**Why:** A lone fighter vs 3 enemies has disastrous odds. Real ROE says break and extend.

### 6. `damaged_rtb`

**Fires when:** Aircraft has taken any non-light damage (DamageLevel.MODERATE or HEAVY).

**Action:** Set target to nearest friendly base, speed reduced per damage level. Cannot be reassigned. Enters MAINTENANCE → REPAIRING state upon landing.

**Why:** Damaged aircraft are combat-ineffective and need repair.

### 7. `deterrence_break_off`

**Fires when:** Aircraft is an attacker AND P(mission_success) from rule #2 is in a narrow "questionable" band (between abort threshold and abort threshold + 0.10) AND it's close enough to an enemy fighter zone that continuing would almost certainly trigger rule #2 next tick.

**Action:** Same as rule #2 but preemptive — aircraft chooses to retreat rather than be forced into a fight.

**Why:** Gives us realistic "turned back at sight" outcomes (the NATO QRA scenario — most interceptions end with the aircraft turning around without combat).

**This is the rule that produces the "no engagement" outcome most common in real-world data.**

### 8. `landing_base_redirect`

**Fires when:** Aircraft RTB'ing reaches `distance_to_home_base < 50km` AND `home_base.is_operational == False` OR `home_base.aircraft_count >= home_base.max_capacity`.

**Action:** Re-target to nearest operational friendly base with capacity.

**Why:** Aircraft don't crash because home base is saturated — they divert. This is the one reflex that explicitly involves the controller: the aircraft *decides to divert*, but the controller's playbook can override with a preferred destination (rule: `landing_redirect_override` trigger).

## What pilots CANNOT do (stays with commander)

These remain commander decisions (playbook triggers or LLM):
- Deciding **when** to launch (timing)
- Deciding **which** targets to attack
- Deciding **force composition** for a mission
- Deciding to **commit reserves** vs hold
- Deciding **patrol zones** and CAP rotation
- Deciding **rules of engagement** (weapons-free, weapons-tight)

## Why these reflex boundaries

The research in [research/engagement_outcomes.md](../../research/engagement_outcomes.md) and [research/air_defense_intercept_doctrine.md](../../research/air_defense_intercept_doctrine.md) shows:

- **Most interceptions end without combat** (NATO QRA: 300-570 scrambles/year, 0 combats). This is captured by rule #7.
- **Damage is 4-14x more common than kills** (NATO RTO studies). Captured by multi-step engagement engine + rule #6.
- **Bingo fuel is non-negotiable** (universal pilot doctrine). Rule #1.
- **Pilots disengage when outnumbered 2:1** (BFM doctrine). Rule #5.
- **Bombers jettison weapons when chased** (standard evasion). Rule #2 + type-specific abort action.

## Implementation location

```
backend/src/domain/services/pilot_reflexes.py
```

Pure function, no external dependencies. Runs every tick for every aircraft before the commander's orders are processed. Uses the seeded RNG from the simulation.

## Testability

Every reflex has unit tests specifying:
- Input state → expected output decision
- Boundary cases (exact threshold, tied priorities)
- Determinism with seeded RNG

See `backend/tests/domain/test_pilot_reflexes.py` (to be written).

## Order of evaluation

Reflexes are checked in this order per tick per aircraft. First one that fires takes effect:

1. `damaged_rtb` (highest priority — safety)
2. `bingo_fuel_rtb`
3. `ammo_depleted_disengage`
4. `outnumbered_bugout`
5. `mission_viability_abort`
6. `deterrence_break_off`
7. `defensive_evasion` (does not override others; runs as a modifier)
8. `landing_base_redirect` (only applies to aircraft already RTB-ing)

Commander's orders apply only to aircraft where **no reflex (1-6) has taken over** this tick.

## Logging

Every reflex that fires produces a structured event in the tick's event log:

```json
{
  "tick": 45,
  "aircraft_id": "s-bo-02",
  "reflex": "mission_viability_abort",
  "p_success": 0.28,
  "threshold": 0.40,
  "action": "JETTISON_WEAPONS+RTB",
  "rationale": "threat_proximity=0.72, target_reachable=0.21"
}
```

This is critical: the **LLM reviewing match results can see why aircraft behaved as they did**, without having to infer from outcomes alone.

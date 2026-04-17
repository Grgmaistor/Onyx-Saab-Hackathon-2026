# Implementation Guide: Updated Aircraft Parameters

## Overview

Update all aircraft type defaults and combat matchup probabilities to use research-backed values. This is a straightforward data update with no architectural changes.

**Research basis**: `research/aircraft_performance.md`, `research/combat_probabilities.md`, `research/base_logistics.md`

## What Changes

### Aircraft Type Defaults

Update `_TYPE_DEFAULTS` (or equivalent) in `backend/src/domain/entities/aircraft.py`.

#### Current Values -> New Values

| Parameter | Type | Current | New | Rationale |
|---|---|---|---|---|
| **Combat Plane** | | | | |
| speed_kmh | | 900 | **950** | Gripen cruise ~950 (see aircraft_performance.md) |
| fuel_capacity | | 800 | **3400** | Gripen E ~4200kg, F-16 ~3249kg, composite 3400kg |
| fuel_burn_rate | | 1.2 | **1.26** | 1200 kg/h / 950 km/h = 1.26 kg/km |
| refuel_time_minutes | | 60 | **10** | Gripen 10-min turnaround (SAAB published spec) |
| ammo_capacity | | 6 | 6 | No change - 4-6 AAMs typical |
| rearm_time_minutes | | 40 | **15** | Gripen A2A rearm in <10 min, allow 15 |
| maintenance_time_minutes | | 45 | **30** | Gripen optimized for rapid turnaround |
| **Bomber** | | | | |
| speed_kmh | | 600 | **750** | Su-34/F-15E cruise ~900, reduced for loaded |
| fuel_capacity | | 1200 | **9000** | Su-34 ~12100kg, F-15E ~5858-10100kg |
| fuel_burn_rate | | 2.0 | **3.73** | 2800 kg/h / 750 km/h |
| refuel_time_minutes | | 90 | **30** | Larger tanks but modern refueling systems |
| ammo_capacity | | 12 | **8** | Strike munitions, not individual bombs |
| rearm_time_minutes | | 60 | **45** | Complex ordnance loading |
| maintenance_time_minutes | | 60 | 60 | No change |
| **UAV** | | | | |
| speed_kmh | | 250 | **300** | MQ-9 Reaper ~300 km/h cruise |
| fuel_capacity | | 300 | **1500** | MQ-9 ~1769kg internal |
| fuel_burn_rate | | 0.5 | **0.20** | Turboprop efficiency: 60 kg/h / 300 km/h |
| refuel_time_minutes | | 45 | **30** | Ground handling for UAV |
| ammo_capacity | | 4 | 4 | No change - 4 guided munitions |
| rearm_time_minutes | | 30 | **20** | Smaller munitions, fewer hardpoints |
| maintenance_time_minutes | | 30 | **45** | Pre-flight checks still needed |
| **Drone Swarm** | | | | |
| speed_kmh | | 150 | **180** | Switchblade/Shahed ~185 km/h |
| fuel_capacity | | 100 | **200** | Abstract energy units for swarm |
| fuel_burn_rate | | 0.8 | **1.0** | Linear depletion model |
| refuel_time_minutes | | 30 | **60** | Battery recharge/fuel replenishment |
| ammo_capacity | | 20 | **15** | Attack-capable drones per swarm unit |
| rearm_time_minutes | | 20 | **30** | Replace expended drone elements |
| maintenance_time_minutes | | 15 | **20** | Simple systems, minimal inspection |

### Combat Matchup Probabilities

Update `combat_matchups` in `scenario/boreal_passage.json` AND any default values in aircraft.py.

#### Current Matrix -> New Matrix

**Current:**
|  | Drone Swarm | UAV | Combat Plane | Bomber |
|---|---|---|---|---|
| **Drone Swarm** | 0.50 | 0.55 | 0.20 | 0.65 |
| **UAV** | 0.45 | 0.50 | 0.25 | 0.60 |
| **Combat Plane** | 0.80 | 0.75 | 0.50 | 0.70 |
| **Bomber** | 0.35 | 0.40 | 0.30 | 0.50 |

**New (research-backed):**
|  | Drone Swarm | UAV | Combat Plane | Bomber |
|---|---|---|---|---|
| **Drone Swarm** | 0.50 | **0.60** | **0.15** | **0.70** |
| **UAV** | **0.40** | 0.50 | **0.10** | **0.55** |
| **Combat Plane** | **0.85** | **0.90** | 0.50 | **0.75** |
| **Bomber** | 0.30 | 0.45 | 0.25 | 0.50 |

**Key changes:**
- Combat Plane vs UAV: 0.75 -> **0.90** (MQ-9 Reaper loss data shows UAVs near-defenseless against fighters)
- UAV vs Combat Plane: 0.25 -> **0.10** (inverse of above)
- Drone Swarm vs Combat Plane: 0.20 -> **0.15** (Ukraine interception data: 85-97% success)
- Drone Swarm vs Bomber: 0.65 -> **0.70** (CNAS data: swarms excel against large slow targets)
- Drone Swarm vs UAV: 0.55 -> **0.60** (numerical advantage against single UAV)

### Base Parameters

Update base capacities in `scenario/boreal_passage.json` based on `research/base_logistics.md`.

The current base values are reasonable for the simulation scale. Consider these adjustments:

| Base | Current Capacity | Suggested | Current Fuel | Suggested |
|---|---|---|---|---|
| Northern Vanguard | 12 | 12 | 5000 | **15000** |
| Highridge Command | 15 | 15 | 8000 | **25000** |
| Boreal Watch Post | 6 | **8** | 2000 | **5000** |
| Firewatch Station | 12 | 12 | 5000 | **15000** |
| Southern Redoubt | 15 | 15 | 8000 | **25000** |
| Spear Point Base | 8 | 8 | 3000 | **8000** |

**Rationale**: With the new fuel_capacity values (3400 for combat plane vs old 800), bases need proportionally more fuel storage. One combat plane sortie now consumes ~3400 fuel units vs the old ~800. Scale base fuel storage up ~3-5x to maintain the same number of sorties before depletion.

Also adjust `fuel_resupply_rate` proportionally:

| Base | Current Rate | Suggested Rate |
|---|---|---|
| Northern Vanguard | 100 | **500** |
| Highridge Command | 150 | **750** |
| Boreal Watch Post | 50 | **250** |
| Firewatch Station | 100 | **500** |
| Southern Redoubt | 150 | **750** |
| Spear Point Base | 75 | **375** |

### Scenario Detection Range

Current: `detection_range_km: 200`

Research shows ground-based radar detects fighter-sized targets at 390-515 km. Consider updating to:

```json
"detection_range_km": 400
```

This is more realistic and affects strategy design -- longer warning time means more time to scramble and intercept.

## Files to Modify

1. **`backend/src/domain/entities/aircraft.py`**
   - Update `_TYPE_DEFAULTS` dict or equivalent with new values
   - No structural changes needed

2. **`scenario/boreal_passage.json`**
   - Update `combat_matchups` matrix
   - Update base `fuel_storage` and `fuel_resupply_rate`
   - Optionally update `detection_range_km`

3. **`Development/DOMAIN.md`**
   - Update "Aircraft Types -- Default Stats" table
   - Update "Combat Matchup Probabilities" table
   - Update "Base Capacities -- Defaults" table
   - Add note referencing research sources

## Important: Unit System Consistency

The current codebase uses abstract "fuel units" and "fuel burn rate per km". The new research values are in **kg**. Before updating, verify how the simulation engine consumes fuel:

```python
# Current model (from SIMULATION.md):
fuel_consumed = fuel_burn_rate * distance_km
```

If `fuel_burn_rate` is in kg/km and `fuel_capacity` is in kg, the math works directly. But verify that `fuel_storage` at bases is in the same units. The base `fuel_storage` must be scaled to match the aircraft fuel system.

**Quick check**: A combat plane with 3400 fuel capacity and 1.26 burn rate has a range of 3400/1.26 = ~2700 km. In the theater (1667x1300 km), a round trip across the strait (~800km) would consume ~1008 fuel units = ~30% of capacity. This seems reasonable.

## Testing

1. Run a single simulation with old values, record metrics
2. Update to new values
3. Run the same simulation (same seed), compare:
   - Does the combat plane now have realistic range? (should cross strait and return)
   - Does refueling take 10 minutes (2 ticks at 5 min/tick)?
   - Do base fuel supplies last a reasonable number of sorties?
   - Does the combat matchup change affect win rates?
4. Run a batch comparison: old params vs new params across 100 seeds

## Simplified Version

If full parameter update causes simulation balance issues:
1. Start with ONLY the combat matchup probability update (smallest change, biggest impact on realism)
2. Then update refuel/rearm/maintenance times
3. Then update fuel capacity and burn rates (requires base fuel rebalancing)
4. Speed changes last (affects timing of all engagements)

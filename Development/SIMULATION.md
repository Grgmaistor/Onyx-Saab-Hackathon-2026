# Simulation Engine

## Overview

The simulation engine is the core of the project. It runs discrete time-step simulations of the Boreal Passage air combat scenario, evaluating different strategic decision patterns across thousands of parallel runs.

## Simulation as a Pure Function

Every simulation is a **pure function**:

```python
def run_simulation(config: ScenarioConfig, strategy: StrategyPort, seed: int) -> SimulationResult:
    """
    Deterministic given the same config + strategy + seed.
    No side effects. No database writes. No network calls.
    Returns the complete result including event log and metrics.
    """
```

This design enables:
- **Parallelism**: No shared state between simulations.
- **Reproducibility**: Same inputs → same output, always.
- **Testability**: Test any scenario without infrastructure.
- **Debugging**: Replay any simulation by rerunning with the same seed.

## Tick Model

Each tick represents a configurable amount of simulated real time (default: 5 minutes).

### Tick Execution Order

```
┌─────────────────────────────────────────────────┐
│ TICK N                                          │
│                                                 │
│  1. DETECT    Scan for enemy aircraft in range  │
│  2. DECIDE    Strategy evaluates state, picks   │
│               actions for each friendly asset   │
│  3. MOVE      Aircraft travel toward targets,   │
│               burn fuel                         │
│  4. ENGAGE    Resolve combats where forces meet │
│  5. DAMAGE    Undefended cities take damage     │
│  6. SERVICE   Refuel/rearm aircraft at bases,   │
│               restore base fuel supplies        │
│  7. RECORD    Snapshot state → event log        │
│  8. CHECK     Evaluate termination conditions   │
│                                                 │
└─────────────────────────────────────────────────┘
```

Each phase is implemented as a domain service function. The simulation loop calls them in order.

### Phase Details

#### 1. DETECT

```python
def detect_threats(state: SimulationState, detection_range_km: float = 200.0) -> list[Aircraft]:
    """Find enemy aircraft within detection range of friendly assets or bases."""
```

- Detection range is configurable per scenario.
- Bases have inherent radar coverage.
- Aircraft can spot enemies within a shorter range.
- Detected threats are added to `state.detected_threats` for the strategy.

#### 2. DECIDE

```python
# StrategyPort interface
def decide(state: SimulationState) -> list[Decision]:
    """Given current world state, return ordered list of decisions."""
```

The strategy receives a **read-only snapshot** of the simulation state and returns decisions. Decisions are validated before execution:
- Cannot launch aircraft that don't exist or are destroyed.
- Cannot launch from a base that's not operational.
- Cannot intercept aircraft that aren't detected.
- Invalid decisions are logged and skipped (not a sim error).

#### 3. MOVE

```python
def execute_movements(aircraft: list[Aircraft], decisions: list[Decision], tick_minutes: float) -> None:
    """Move aircraft toward their targets/destinations."""
```

- Distance covered per tick = `speed_kmh × (tick_minutes / 60)`.
- Fuel consumed = `fuel_burn_rate × distance_km`.
- If aircraft reaches destination this tick, it arrives.
- If fuel hits 0, aircraft crashes (DESTROYED).

#### 4. ENGAGE

```python
def resolve_engagements(aircraft: list[Aircraft], engagement_range_km: float = 50.0) -> list[CombatResult]:
    """Find opposing aircraft within range, resolve combat."""
```

- Uses the combat matchup probability matrix from `DOMAIN.md`.
- Each engagement uses the simulation's seeded RNG: `random.random() < P(attacker_wins)`.
- Loser is marked DESTROYED.
- Winner loses 1 ammo.
- If ammo == 0 before engagement, aircraft cannot engage (must RTB).
- Multiple engagements per tick are resolved sequentially (no double-counting).

#### 5. DAMAGE

```python
def apply_city_damage(cities: list[City], enemy_bombers: list[Aircraft], tick_minutes: float) -> None:
    """Undefended cities in range of enemy bombers take damage."""
```

- Only BOMBER type deals city damage (others focus on air-to-air).
- Damage rate depends on number of bombers and city defense value.
- Casualties calculated proportionally to damage increase.
- Capital at damage >= 1.0 triggers simulation loss.

#### 6. SERVICE

```python
def service_aircraft(bases: list[Base], aircraft: list[Aircraft], tick_minutes: float) -> None:
    """Progress refueling/rearming for aircraft at bases."""
```

- Aircraft in REFUELING state progress toward full fuel.
- Aircraft in REARMING state progress toward full ammo.
- MAINTENANCE state progresses toward ready.
- Base fuel storage decreases when refueling, regenerates each tick.

#### 7. RECORD

```python
def record_tick(simulation: Simulation) -> SimulationTick:
    """Snapshot current state for the replay log."""
```

Creates a serializable snapshot of all aircraft positions, base states, city states, active battles, and decisions made. This is what the graphics team uses for replay.

#### 8. CHECK

```python
def check_termination(state: SimulationState, max_ticks: int) -> SimulationStatus | None:
    """Return a terminal status if simulation should end, else None."""
```

Termination conditions (checked in order):
1. Friendly capital destroyed → `LOSS`
2. Enemy capital destroyed → `WIN`
3. All friendly aircraft destroyed → `LOSS`
4. All enemy aircraft destroyed → `WIN`
5. All enemy bases destroyed → `WIN`
6. `current_tick >= max_ticks` → `TIMEOUT` (evaluate by metrics)

## Strategy Port

The strategy is the **variable under test**. Each simulation run uses one strategy. Batch runs compare many strategies.

### Interface

```python
class StrategyPort(ABC):
    """
    Decision-making interface. Receives full simulation state,
    returns a list of decisions for this tick.
    """
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def description(self) -> str: ...

    @abstractmethod
    def decide(self, state: SimulationState) -> list[Decision]: ...
```

### Example Strategies

#### Defensive Strategy

Prioritizes protecting cities and capital. Only engages threats approaching defended zones.

```python
class DefensiveStrategy(StrategyPort):
    name = "defensive_v1"
    description = "Protect capital and cities. Engage only approaching threats."

    def decide(self, state: SimulationState) -> list[Decision]:
        decisions = []
        for threat in state.detected_threats:
            # Find nearest available combat plane
            nearest = find_nearest_available(state.friendly_aircraft, threat.position)
            if nearest:
                decisions.append(Decision(
                    type=DecisionType.INTERCEPT,
                    aircraft_id=nearest.id,
                    target_id=threat.id,
                ))
        # RTB aircraft low on fuel
        for ac in state.friendly_aircraft:
            if ac.state == AircraftState.AIRBORNE and ac.fuel_current < ac.fuel_capacity * 0.2:
                decisions.append(Decision(
                    type=DecisionType.RTB,
                    aircraft_id=ac.id,
                    target_id=find_nearest_base(state.friendly_bases, ac.position).id,
                ))
        return decisions
```

#### Aggressive Strategy

Pushes forward, targets enemy bases and bombers proactively.

#### Balanced Strategy

Mix of patrol zones and responsive intercepts. Good baseline.

### Writing a New Strategy

1. Create `scenario/strategies/my_strategy.py`.
2. Implement `StrategyPort`.
3. The `decide()` method receives `SimulationState` — use it to:
   - Read `friendly_aircraft`, `enemy_aircraft`, `detected_threats`
   - Check fuel levels, ammo counts, base capacities
   - Return a list of `Decision` objects
4. Register in the strategy registry (simple dict mapping name → class).
5. Test: run a single simulation via API, inspect the replay log.

### Strategy Constraints

- Strategies can only issue decisions for friendly aircraft.
- Strategies receive only **detected** enemy positions (fog of war).
- Strategies cannot modify simulation state directly — they return decisions.
- Invalid decisions are silently skipped with a log warning.

## Parallel Execution

### Architecture

```
POST /simulations/batch
  │
  ├─ BatchConfig: {scenario, strategies[], seeds[], count}
  │
  └─ ProcessPoolExecutor(max_workers=cpu_count())
       │
       ├─ Process 1: run_simulation(config, strategy_A, seed=42)
       ├─ Process 2: run_simulation(config, strategy_A, seed=43)
       ├─ Process 3: run_simulation(config, strategy_B, seed=42)
       ├─ Process 4: run_simulation(config, strategy_B, seed=43)
       └─ ... (one process per simulation)
       │
       └─ Results collected, stored in DB, metrics aggregated
```

### How It Works

```python
from concurrent.futures import ProcessPoolExecutor, as_completed

def run_batch(configs: list[SimConfig], max_workers: int | None = None) -> list[SimulationResult]:
    max_workers = max_workers or os.cpu_count()
    results = []

    with ProcessPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(run_simulation, cfg.scenario, cfg.strategy, cfg.seed): cfg
            for cfg in configs
        }
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            # Optionally publish progress via event publisher

    return results
```

### Scaling

| Cores | Simulations | Time per Sim | Total Time (approx) |
|---|---|---|---|
| 8 | 1,000 | 100ms | ~12.5 seconds |
| 16 | 1,000 | 100ms | ~6.3 seconds |
| 32 | 10,000 | 100ms | ~31 seconds |
| 64 | 10,000 | 100ms | ~16 seconds |

Each simulation is independent — scaling is linear with cores.

### Progress Reporting

During batch execution, progress is reported via WebSocket:

```json
{
  "batch_id": "batch-abc",
  "completed": 423,
  "total": 1000,
  "eta_seconds": 120,
  "latest_result": { "sim_id": "...", "outcome": "WIN", "ticks": 342 }
}
```

## Random Seed System

Every simulation takes a `seed: int` parameter used to initialize its own `random.Random(seed)` instance. This ensures:

- **Reproducibility**: Same seed → identical simulation.
- **Independence**: Different seeds explore different combat outcomes.
- **Batch design**: Run each strategy across the same set of seeds to compare fairly.

The seeded RNG is used for:
- Combat resolution (P(win) checks)
- Enemy decision-making (if enemy uses a stochastic strategy)
- Any other probabilistic events

**Never use `random.random()` (global RNG) in simulation code.** Always use the simulation's local `rng` instance.

## Replay Log Format

Each simulation produces a replay log for the graphics team. Exported as JSON:

```json
{
  "simulation_id": "sim-abc-123",
  "scenario": "boreal_passage_v1",
  "strategy": "defensive_v1",
  "seed": 42,
  "side": "north",
  "outcome": "WIN",
  "total_ticks": 480,
  "tick_minutes": 5,
  "ticks": [
    {
      "tick": 0,
      "aircraft": [
        {
          "id": "n-cp-01",
          "type": "combat_plane",
          "side": "north",
          "position": [198.3, 335.0],
          "fuel": 1.0,
          "ammo": 6,
          "state": "grounded"
        }
      ],
      "bases": [
        {
          "id": "northern_vanguard",
          "name": "Northern Vanguard Base",
          "side": "north",
          "position": [198.3, 335.0],
          "operational": true,
          "fuel_storage": 5000,
          "aircraft_count": 8
        }
      ],
      "cities": [
        {
          "id": "arktholm",
          "name": "Arktholm",
          "side": "north",
          "position": [418.3, 95.0],
          "damage": 0.0,
          "casualties": 0
        }
      ],
      "battles": [],
      "decisions": [],
      "events": ["Simulation started. Controlling NORTH side."]
    },
    {
      "tick": 1,
      "aircraft": [...],
      "events": [
        "n-cp-01 launched from Northern Vanguard Base",
        "Enemy drone swarm detected at (600, 500)"
      ]
    }
  ],
  "metrics": {
    "total_civilian_casualties": 1200,
    "time_to_first_casualty": 45,
    "aircraft_lost": 3,
    "aircraft_remaining": 9,
    "bases_lost": 0,
    "cities_defended": 3,
    "capital_survived": true,
    "engagement_win_rate": 0.72,
    "sorties_flown": 34
  }
}
```

The graphics team reads this file and animates it at any playback speed. They never need to run the simulation engine.

## Scenario Configuration

Scenarios are JSON files in `scenario/`:

```json
{
  "id": "boreal_passage_v1",
  "name": "The Boreal Passage — Standard",
  "theater_width_km": 1667,
  "theater_height_km": 1300,
  "tick_minutes": 5,
  "max_ticks": 1000,
  "detection_range_km": 200,
  "engagement_range_km": 50,
  "bases": [...],
  "cities": [...],
  "starting_aircraft": {
    "north": [
      {"type": "combat_plane", "count": 6, "base": "northern_vanguard"},
      {"type": "combat_plane", "count": 6, "base": "highridge_command"},
      {"type": "uav", "count": 4, "base": "boreal_watch_post"},
      {"type": "drone_swarm", "count": 8, "base": "highridge_command"},
      {"type": "bomber", "count": 3, "base": "northern_vanguard"}
    ],
    "south": [...]
  },
  "combat_matchups": {
    "drone_swarm": {"drone_swarm": 0.50, "uav": 0.55, "combat_plane": 0.20, "bomber": 0.65},
    "uav": {"drone_swarm": 0.45, "uav": 0.50, "combat_plane": 0.25, "bomber": 0.60},
    "combat_plane": {"drone_swarm": 0.80, "uav": 0.75, "combat_plane": 0.50, "bomber": 0.70},
    "bomber": {"drone_swarm": 0.35, "uav": 0.40, "combat_plane": 0.30, "bomber": 0.50}
  }
}
```

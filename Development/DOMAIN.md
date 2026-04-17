# Domain Model — Boreal Passage

## Scenario: The Boreal Passage

Two countries separated by a maritime strait (~400km wide). The theater of operations is approximately 1667km × 1300km.

### Country X (North) — Green

| Asset | Name | Type | Position (x_km, y_km) | Notes |
|---|---|---|---|---|
| Air Base | Northern Vanguard Base | air_base | (198.3, 335.0) | Western coastal, mainland |
| Air Base | Highridge Command | air_base | (838.3, 75.0) | Deep inland, mainland |
| Air Base | Boreal Watch Post | air_base | (1158.3, 385.0) | Forward operating base, island |
| Capital | Arktholm (Capital X) | capital | (418.3, 95.0) | Political capital, mainland |
| City | Valbrek | major_city | (1423.3, 213.3) | Eastern coast, mainland |
| City | Nordvik | major_city | (140.0, 323.3) | Western coast, mainland |

### Country Y (South) — Brown

| Asset | Name | Type | Position (x_km, y_km) | Notes |
|---|---|---|---|---|
| Air Base | Firewatch Station | air_base | (1398.3, 1071.7) | Eastern coastal, mainland |
| Air Base | Southern Redoubt | air_base | (321.7, 1238.3) | Inland, mainland |
| Air Base | Spear Point Base | air_base | (918.3, 835.0) | Forward strike base, island |
| Capital | Meridia (Capital Y) | capital | (1225.0, 1208.3) | Political capital, mainland |
| City | Callhaven | major_city | (96.7, 1150.0) | Western, mainland |
| City | Solano | major_city | (576.7, 1236.7) | Inland, mainland |

### Terrain Features

The strait contains several islands used as forward positions:
- North Strait Island West (~657, 493)
- North Strait Island East (~1157, 388) — houses Boreal Watch Post
- North Remote Island (~303, 627)
- South Forward Island (~1408, 753)
- South Small Island (~423, 920)
- South Central Peninsula (~898, 828) — houses Spear Point Base

## Entities

### Aircraft (Abstract Base Class)

All aircraft types inherit from `Aircraft`. This is the primary extension point for adding new unit types.

```python
@dataclass
class Aircraft:
    id: str                          # Unique identifier (e.g., "n-f16-01")
    type: AircraftType               # Enum: DRONE_SWARM, UAV, COMBAT_PLANE, BOMBER
    side: Side                       # Enum: NORTH, SOUTH
    position: Position               # Current (x_km, y_km)
    state: AircraftState             # Enum: GROUNDED, AIRBORNE, REFUELING, DESTROYED
    fuel_current: float              # Current fuel (0.0 to fuel_capacity)
    ammo_current: int                # Current ammo/payload count
    assigned_base: str               # Home base ID

    # --- Type-specific constants (set by subclass) ---
    speed_kmh: float                 # Cruise speed
    fuel_capacity: float             # Max fuel units
    fuel_burn_rate: float            # Fuel consumed per km traveled
    refuel_time_minutes: float       # Minutes to fully refuel at base
    ammo_capacity: int               # Max ammo/payload
    rearm_time_minutes: float        # Minutes to rearm at base
    maintenance_time_minutes: float  # Turnaround time between sorties
    combat_matchups: dict[str, float]  # opponent_type → P(win)
```

#### AircraftType Enum

```python
class AircraftType(str, Enum):
    DRONE_SWARM = "drone_swarm"
    UAV = "uav"
    COMBAT_PLANE = "combat_plane"
    BOMBER = "bomber"
```

#### Aircraft Types — Default Stats

These values should be refined through research (see `research/` folder). Values below are initial working estimates.

| Attribute | Drone Swarm | UAV | Combat Plane | Bomber |
|---|---|---|---|---|
| `speed_kmh` | 150 | 250 | 900 | 600 |
| `fuel_capacity` | 100 | 300 | 800 | 1200 |
| `fuel_burn_rate` | 0.8 | 0.5 | 1.2 | 2.0 |
| `refuel_time_minutes` | 30 | 45 | 60 | 90 |
| `ammo_capacity` | 20 | 4 | 6 | 12 |
| `rearm_time_minutes` | 20 | 30 | 40 | 60 |
| `maintenance_time_minutes` | 15 | 30 | 45 | 60 |

#### Combat Matchup Probabilities — P(row wins vs column)

|  | Drone Swarm | UAV | Combat Plane | Bomber |
|---|---|---|---|---|
| **Drone Swarm** | 0.50 | 0.55 | 0.20 | 0.65 |
| **UAV** | 0.45 | 0.50 | 0.25 | 0.60 |
| **Combat Plane** | 0.80 | 0.75 | 0.50 | 0.70 |
| **Bomber** | 0.35 | 0.40 | 0.30 | 0.50 |

> These are P(attacker wins). The defender's probability is `1 - P(attacker wins)`.
> Values are initial estimates. Update via research in `research/combat_probabilities.md`.

### AircraftState Enum

```python
class AircraftState(str, Enum):
    GROUNDED = "grounded"          # At base, ready or being serviced
    AIRBORNE = "airborne"          # In flight
    REFUELING = "refueling"        # At base, being refueled
    REARMING = "rearming"          # At base, being rearmed
    MAINTENANCE = "maintenance"    # At base, post-sortie turnaround
    ENGAGED = "engaged"            # Currently in combat
    DESTROYED = "destroyed"        # Eliminated from simulation
```

### Base

```python
@dataclass
class Base:
    id: str                        # e.g., "northern_vanguard"
    name: str                      # "Northern Vanguard Base"
    side: Side
    position: Position
    max_aircraft_capacity: int     # Max aircraft parked simultaneously
    fuel_storage: float            # Total fuel available for refueling
    fuel_resupply_rate: float      # Fuel units restored per tick
    is_operational: bool           # False if destroyed
    current_aircraft: list[str]    # IDs of aircraft currently at base
```

#### Base Capacities — Defaults

| Base | Max Aircraft | Fuel Storage | Resupply Rate/Tick |
|---|---|---|---|
| Northern Vanguard Base | 12 | 5000 | 100 |
| Highridge Command | 15 | 8000 | 150 |
| Boreal Watch Post | 6 | 2000 | 50 |
| Firewatch Station | 12 | 5000 | 100 |
| Southern Redoubt | 15 | 8000 | 150 |
| Spear Point Base | 8 | 3000 | 75 |

### City

```python
@dataclass
class City:
    id: str                        # e.g., "arktholm"
    name: str                      # "Arktholm (Capital X)"
    side: Side
    position: Position
    population: int                # Civilian population
    is_capital: bool               # True for Arktholm and Meridia
    defense_value: float           # Strategic importance (0-1), capitals = 1.0
    damage_taken: float            # Cumulative damage (0.0 = pristine, 1.0 = destroyed)
    casualties: int                # Civilian casualties so far
```

#### City Populations — Defaults

| City | Population | Is Capital | Defense Value |
|---|---|---|---|
| Arktholm (Capital X) | 500,000 | Yes | 1.0 |
| Valbrek | 120,000 | No | 0.5 |
| Nordvik | 150,000 | No | 0.5 |
| Meridia (Capital Y) | 450,000 | Yes | 1.0 |
| Callhaven | 100,000 | No | 0.5 |
| Solano | 130,000 | No | 0.5 |

### Battle

```python
@dataclass
class Battle:
    id: str
    tick: int                      # When the engagement started
    position: Position             # Where the battle occurs
    attackers: list[str]           # Aircraft IDs
    defenders: list[str]           # Aircraft IDs
    result: CombatResult | None    # None if still in progress
```

### Simulation

The aggregate root. Contains all state for one simulation run.

```python
@dataclass
class Simulation:
    id: str
    scenario_id: str               # Which scenario config
    strategy_id: str               # Which strategy is being used
    seed: int                      # Random seed for reproducibility
    side: Side                     # Which side the player controls
    current_tick: int
    max_ticks: int                 # Termination: max simulation length
    status: SimulationStatus       # PENDING, RUNNING, COMPLETED, FAILED
    state: SimulationState         # Current world state snapshot
    event_log: list[SimulationTick]  # Full history for replay
    metrics: SimulationMetrics | None  # Computed after completion
```

## Value Objects

### Position

```python
@dataclass(frozen=True)
class Position:
    x_km: float
    y_km: float

    def distance_to(self, other: "Position") -> float:
        """Euclidean distance in km."""
        return math.sqrt((self.x_km - other.x_km)**2 + (self.y_km - other.y_km)**2)

    def travel_time_minutes(self, other: "Position", speed_kmh: float) -> float:
        """Minutes to travel from self to other at given speed."""
        return (self.distance_to(other) / speed_kmh) * 60
```

### Decision

```python
@dataclass(frozen=True)
class Decision:
    type: DecisionType
    aircraft_id: str
    target_id: str | None = None   # Aircraft ID for INTERCEPT, Base ID for RTB/RELOCATE
    position: Position | None = None  # For PATROL zone center

class DecisionType(str, Enum):
    LAUNCH = "launch"              # Scramble aircraft from base
    INTERCEPT = "intercept"        # Engage specific enemy aircraft
    PATROL = "patrol"              # Defend a zone/area
    RTB = "rtb"                    # Return to base for refuel/rearm
    HOLD = "hold"                  # Maintain current position/heading
    RELOCATE = "relocate"          # Move to a different base
```

### CombatResult

```python
@dataclass(frozen=True)
class CombatResult:
    attacker_id: str
    defender_id: str
    attacker_won: bool
    attacker_destroyed: bool
    defender_destroyed: bool
    collateral_damage: float       # Damage to nearby city if applicable
```

### SimulationMetrics

```python
@dataclass(frozen=True)
class SimulationMetrics:
    total_civilian_casualties: int
    time_to_first_casualty: int | None   # Tick number, None if no casualties
    aircraft_lost: int
    aircraft_remaining: int
    bases_lost: int
    bases_remaining: int
    cities_defended: int                  # Cities with damage < 0.5
    capital_survived: bool
    total_ticks: int
    fuel_efficiency: float               # Avg fuel utilization ratio
    engagement_win_rate: float           # Fraction of combats won
    response_time_avg: float             # Avg ticks from threat detection to intercept
    total_engagements: int
    sorties_flown: int
```

### SimulationState

Snapshot of the entire world at a given tick. This is what strategies receive to make decisions.

```python
@dataclass
class SimulationState:
    tick: int
    friendly_aircraft: list[Aircraft]
    enemy_aircraft: list[Aircraft]
    friendly_bases: list[Base]
    enemy_bases: list[Base]
    friendly_cities: list[City]
    enemy_cities: list[City]
    active_battles: list[Battle]
    detected_threats: list[Aircraft]    # Enemy aircraft in detection range
```

### SimulationTick

One tick's worth of events for the replay log.

```python
@dataclass
class SimulationTick:
    tick: int
    aircraft_states: list[dict]    # Serialized aircraft positions/states
    base_states: list[dict]        # Serialized base states
    city_states: list[dict]        # Serialized city states
    battles: list[dict]            # Active/resolved battles this tick
    decisions_made: list[dict]     # What the strategy decided
    events: list[str]              # Human-readable event descriptions
```

## Domain Rules

### Movement

- Aircraft travel in straight lines between positions.
- Fuel consumed = `fuel_burn_rate × distance_km`.
- If fuel reaches 0 while airborne, aircraft is DESTROYED (crashed).
- Aircraft cannot exceed their `speed_kmh`.

### Refueling

- Aircraft must be at a base to refuel.
- Refueling takes `refuel_time_minutes` (converted to ticks).
- Base must have fuel in `fuel_storage`. If storage is empty, aircraft waits.
- Base fuel regenerates at `fuel_resupply_rate` per tick.
- Base `max_aircraft_capacity` limits how many can be parked simultaneously.

### Combat

- Combat triggers when opposing aircraft are within engagement range (configurable, default 50km).
- Each engagement resolves in one tick using the probability matrix.
- Loser is DESTROYED. Winner continues with reduced ammo (`ammo_current -= 1`).
- If ammo is 0, aircraft cannot engage and must RTB.
- Combat near a city causes `collateral_damage` proportional to the engagement.

### City Damage

- Undefended cities under attack take damage per tick.
- Bombers deal more city damage than other types.
- Casualties = `population × damage_increase × casualty_rate`.
- Capital destruction ends the simulation (loss condition).

### Termination Conditions

A simulation ends when ANY of these is true:
1. Capital is destroyed (`damage >= 1.0`) → side loses.
2. All aircraft on one side are destroyed → that side loses.
3. `max_ticks` reached → evaluate by metrics (fewer casualties wins).
4. All enemy bases destroyed → attacker wins.

## Adding a New Aircraft Type

1. Add entry to `AircraftType` enum.
2. Create subclass or factory entry with all stats filled in.
3. Add row/column to combat matchup probability table.
4. Document stats and source in `Development/DOMAIN.md` (this file).
5. If stats require research, create a file in `research/` first (see `Development/RESEARCH.md`).

**Example — adding a Stealth Fighter:**

```python
# In aircraft.py
class StealthFighter(Aircraft):
    speed_kmh = 1200
    fuel_capacity = 600
    fuel_burn_rate = 1.8
    refuel_time_minutes = 75
    ammo_capacity = 4
    rearm_time_minutes = 35
    maintenance_time_minutes = 90
    combat_matchups = {
        "drone_swarm": 0.90,
        "uav": 0.85,
        "combat_plane": 0.65,
        "bomber": 0.80,
        "stealth_fighter": 0.50,
    }
```

Then update the matchup table in this document and reference your research source.

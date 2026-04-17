# Implementation Guide: Genetic Algorithm Strategy Optimization

## Overview

Add an evolutionary optimization system that automatically discovers optimal air defense strategies by evolving parameterized strategies through thousands of simulated battles.

**Research basis**: `research/strategy_optimization.md`

## Architecture

Follows hexagonal architecture. New code spans all three layers.

### New Files

```
backend/src/domain/
  value_objects/
    genome.py                          # StrategyGenome (frozen dataclass)
    optimization_config.py             # OptimizationConfig, OptimizationResult
  ports/
    optimizer.py                       # OptimizerPort ABC
  services/
    fitness.py                         # score() pure function

backend/src/application/
  optimize_strategy.py                 # OptimizeStrategyUseCase

backend/src/infrastructure/
  optimization/
    __init__.py
    ga_optimizer.py                    # GeneticAlgorithmOptimizer (implements OptimizerPort)
    parameterized_strategy.py          # ParameterizedStrategy (implements StrategyPort)
    ga_operators.py                    # Tournament selection, SBX crossover, polynomial mutation
```

## Implementation Steps

### Step 1: Domain Value Objects

#### `genome.py`

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar

@dataclass(frozen=True)
class StrategyGenome:
    """28-gene chromosome encoding a parameterized strategy."""
    genes: tuple[float, ...]

    GENE_COUNT: ClassVar[int] = 28
    
    # Indices of discrete genes (decoded by quantization)
    DISCRETE_GENES: ClassVar[frozenset[int]] = frozenset({4, 11, 16, 17, 18, 20})

    def __post_init__(self):
        if len(self.genes) != self.GENE_COUNT:
            raise ValueError(f"Expected {self.GENE_COUNT} genes, got {len(self.genes)}")
        if not all(0.0 <= g <= 1.0 for g in self.genes):
            raise ValueError("All genes must be in [0.0, 1.0]")
```

#### `optimization_config.py`

```python
from __future__ import annotations
from dataclasses import dataclass, field

@dataclass(frozen=True)
class OptimizationConfig:
    population_size: int = 100
    generations: int = 50
    crossover_rate: float = 0.9
    mutation_rate: float = 0.036       # 1/28
    elite_fraction: float = 0.05
    tournament_size: int = 3
    seeds_per_evaluation: int = 20
    coevolution_enabled: bool = False  # Start simple, add later
    scenario_id: str = "boreal_passage_v1"
    enemy_strategy_id: str = "balanced_v1"
    fitness_weights: dict[str, float] = field(default_factory=lambda: {
        "outcome": 1.0,
        "casualties": 2.0,
        "aircraft": 1.0,
        "engagement": 1.0,
        "cities": 1.5,
        "fuel": 0.5,
        "response": 0.8,
    })

@dataclass
class GenerationStats:
    generation: int
    best_fitness: float
    mean_fitness: float
    std_fitness: float
    worst_fitness: float
    best_genome: StrategyGenome

@dataclass
class OptimizationResult:
    best_genome: StrategyGenome
    best_fitness: float
    generation_history: list[GenerationStats]
    total_simulations: int
    wall_time_seconds: float
```

### Step 2: Fitness Function (Domain Service)

#### `fitness.py`

```python
from __future__ import annotations

def score(result) -> float:
    """
    Score a simulation result. Pure function, no side effects.
    Higher is better. Returns float.
    """
    m = result.metrics

    if not m.capital_survived:
        return -1000.0

    outcome_map = {"WIN": 100.0, "TIMEOUT": 20.0, "LOSS": -100.0}
    outcome_score = outcome_map.get(result.outcome, 0.0)

    casualty_score = -min(m.total_civilian_casualties / 1000.0, 100.0)
    aircraft_score = (m.aircraft_remaining / max(m.aircraft_remaining + m.aircraft_lost, 1)) * 50.0
    engagement_score = m.engagement_win_rate * 50.0
    cities_score = m.cities_defended * 15.0
    fuel_score = m.fuel_efficiency * 20.0
    response_score = max(0, 30.0 - m.response_time_avg)

    return (
        outcome_score * 1.0
        + casualty_score * 2.0
        + aircraft_score * 1.0
        + engagement_score * 1.0
        + cities_score * 1.5
        + fuel_score * 0.5
        + response_score * 0.8
    )
```

### Step 3: Optimizer Port (Domain)

#### `optimizer.py`

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable
from ..value_objects.genome import StrategyGenome
from ..value_objects.optimization_config import OptimizationConfig, OptimizationResult

class OptimizerPort(ABC):
    @abstractmethod
    def optimize(
        self,
        config: OptimizationConfig,
        evaluate_fn: Callable[[StrategyGenome], float],
        progress_callback: Callable[[int, int, float], None] | None = None,
    ) -> OptimizationResult:
        """
        Run optimization loop.
        evaluate_fn: takes a genome, returns fitness score
        progress_callback: (generation, total_generations, best_fitness)
        """
        ...
```

### Step 4: Parameterized Strategy (Infrastructure)

#### `parameterized_strategy.py`

This is the most critical file. It translates the 28-gene vector into actual `decide()` behavior.

```python
from __future__ import annotations
from dataclasses import dataclass
import math

# Domain imports
from src.domain.ports.strategy import StrategyPort
from src.domain.entities.simulation import SimulationState
from src.domain.entities.aircraft import AircraftState, AircraftType
from src.domain.value_objects.decision import Decision, DecisionType
from src.domain.value_objects.genome import StrategyGenome


@dataclass
class DecodedParams:
    """Decoded strategy parameters from genome."""
    # Group A: Resource Management
    fuel_rtb_threshold: float        # [0.10, 0.40]
    reserve_fraction: float          # [0.10, 0.70]
    min_fuel_to_launch: float        # [0.30, 0.90]
    patrol_fuel_floor: float         # [0.20, 0.50]
    ammo_rtb_threshold: int          # {0, 1, 2}
    sortie_launch_delay: int         # [0, 10] ticks

    # Group B: Threat Response
    threat_distance_weight: float    # [0.0, 1.0]
    bomber_priority_boost: float     # [1.0, 5.0]
    combat_plane_priority: float     # [1.0, 3.0]
    uav_priority: float              # [0.5, 2.0]
    drone_swarm_priority: float      # [0.3, 1.5]
    max_interceptors_per_threat: int  # {1, 2, 3}
    threat_range_engage: float       # [100, 500] km

    # Group C: Aircraft Type Preferences
    prefer_cp_vs_bomber: float       # [0.0, 1.0]
    prefer_cp_vs_cp: float           # [0.0, 1.0]
    use_drones_vs_drones: float      # [0.0, 1.0]
    bomber_usage_mode: int           # {0=HOLD, 1=ESCORT, 2=OFFENSIVE}
    uav_usage_mode: int              # {0=PATROL, 1=INTERCEPT, 2=SCOUT}

    # Group D: Patrol & Positioning
    num_patrol_zones: int            # {1, 2, 3, 4, 5}
    patrol_zone_depth: float         # [0.0, 1.0]
    aircraft_per_zone: int           # {1, 2, 3, 4}
    patrol_zone_spread: float        # [100, 400] km
    capital_patrol_weight: float     # [0.0, 1.0]
    forward_patrol_bias: float       # [0.0, 1.0]

    # Group E: Engagement Rules
    launch_aggressiveness: float     # [0.0, 1.0]
    commit_ratio_vs_threats: float   # [0.5, 3.0]
    retreat_on_disadvantage: float   # [0.0, 1.0]
    retaliation_escalation: float    # [0.0, 1.0]


def decode_genome(genome: StrategyGenome) -> DecodedParams:
    """Decode [0,1] gene values to domain-meaningful parameters."""
    g = genome.genes
    return DecodedParams(
        fuel_rtb_threshold=0.10 + g[0] * 0.30,
        reserve_fraction=0.10 + g[1] * 0.60,
        min_fuel_to_launch=0.30 + g[2] * 0.60,
        patrol_fuel_floor=0.20 + g[3] * 0.30,
        ammo_rtb_threshold=int(g[4] * 2.99),           # {0, 1, 2}
        sortie_launch_delay=int(g[5] * 10),
        threat_distance_weight=g[6],
        bomber_priority_boost=1.0 + g[7] * 4.0,
        combat_plane_priority=1.0 + g[8] * 2.0,
        uav_priority=0.5 + g[9] * 1.5,
        drone_swarm_priority=0.3 + g[10] * 1.2,
        max_interceptors_per_threat=1 + int(g[11] * 2.99),  # {1, 2, 3}
        threat_range_engage=100.0 + g[12] * 400.0,
        prefer_cp_vs_bomber=g[13],
        prefer_cp_vs_cp=g[14],
        use_drones_vs_drones=g[15],
        bomber_usage_mode=int(g[16] * 2.99),            # {0, 1, 2}
        uav_usage_mode=int(g[17] * 2.99),               # {0, 1, 2}
        num_patrol_zones=1 + int(g[18] * 4.99),          # {1..5}
        patrol_zone_depth=g[19],
        aircraft_per_zone=1 + int(g[20] * 3.99),         # {1..4}
        patrol_zone_spread=100.0 + g[21] * 300.0,
        capital_patrol_weight=g[22],
        forward_patrol_bias=g[23],
        launch_aggressiveness=g[24],
        commit_ratio_vs_threats=0.5 + g[25] * 2.5,
        retreat_on_disadvantage=g[26],
        retaliation_escalation=g[27],
    )


class ParameterizedStrategy(StrategyPort):
    """Strategy driven entirely by a genome parameter vector."""

    def __init__(self, genome: StrategyGenome):
        self._genome = genome
        self._params = decode_genome(genome)

    @property
    def name(self) -> str:
        return f"evolved_{hash(self._genome.genes) & 0xFFFF:04x}"

    @property
    def description(self) -> str:
        return f"Evolved strategy (reserve={self._params.reserve_fraction:.0%}, rtb_fuel={self._params.fuel_rtb_threshold:.0%})"

    def decide(self, state: SimulationState) -> list[Decision]:
        p = self._params
        decisions: list[Decision] = []
        already_tasked: set[str] = set()

        # --- Phase 1: RTB (fuel/ammo thresholds from genome) ---
        for ac in state.friendly_aircraft:
            if ac.state == AircraftState.AIRBORNE:
                if ac.fuel_current < ac.fuel_capacity * p.fuel_rtb_threshold:
                    base = _find_nearest_base(state.friendly_bases, ac.position)
                    if base:
                        decisions.append(Decision(type=DecisionType.RTB, aircraft_id=ac.id, target_id=base.id))
                        already_tasked.add(ac.id)
                elif ac.ammo_current <= p.ammo_rtb_threshold:
                    base = _find_nearest_base(state.friendly_bases, ac.position)
                    if base:
                        decisions.append(Decision(type=DecisionType.RTB, aircraft_id=ac.id, target_id=base.id))
                        already_tasked.add(ac.id)

        # --- Phase 2: Threat scoring and interception ---
        threats = list(state.detected_threats)
        capital = _find_capital(state.friendly_cities)

        # Score threats using genome weights
        def threat_score(t):
            type_multiplier = {
                AircraftType.BOMBER: p.bomber_priority_boost,
                AircraftType.COMBAT_PLANE: p.combat_plane_priority,
                AircraftType.UAV: p.uav_priority,
                AircraftType.DRONE_SWARM: p.drone_swarm_priority,
            }.get(t.type, 1.0)

            if capital:
                dist_to_capital = _distance(t.position, capital.position)
            else:
                dist_to_capital = 999.0
            dist_to_nearest_city = min(
                (_distance(t.position, c.position) for c in state.friendly_cities),
                default=999.0,
            )
            dist_score = (
                p.threat_distance_weight * (1000 - dist_to_capital)
                + (1 - p.threat_distance_weight) * (1000 - dist_to_nearest_city)
            )
            return type_multiplier * dist_score

        threats.sort(key=threat_score, reverse=True)

        # Filter by engagement range
        threats = [t for t in threats if _any_asset_in_range(t, state, p.threat_range_engage)]

        # Calculate commitment limit
        available = [ac for ac in state.friendly_aircraft
                     if ac.state not in (AircraftState.DESTROYED,)]
        max_commit = int(len(available) * (1.0 - p.reserve_fraction))
        committed = sum(1 for ac in state.friendly_aircraft if ac.state == AircraftState.AIRBORNE and ac.id not in already_tasked)
        can_commit = max(0, max_commit - committed)

        for threat in threats:
            if can_commit <= 0:
                break
            interceptors_for_threat = min(p.max_interceptors_per_threat, can_commit)

            for _ in range(interceptors_for_threat):
                interceptor = _select_interceptor(state, threat, p, already_tasked)
                if not interceptor:
                    break

                if interceptor.state == AircraftState.GROUNDED:
                    decisions.append(Decision(type=DecisionType.LAUNCH, aircraft_id=interceptor.id))

                decisions.append(Decision(type=DecisionType.INTERCEPT, aircraft_id=interceptor.id, target_id=threat.id))
                already_tasked.add(interceptor.id)
                can_commit -= 1

        # --- Phase 3: Launch decisions (aggressiveness from genome) ---
        if p.launch_aggressiveness > 0.7:
            # Aggressive: launch all available
            for ac in state.friendly_aircraft:
                if ac.id not in already_tasked and ac.state == AircraftState.GROUNDED:
                    if ac.fuel_current > ac.fuel_capacity * p.min_fuel_to_launch and can_commit > 0:
                        decisions.append(Decision(type=DecisionType.LAUNCH, aircraft_id=ac.id))
                        can_commit -= 1

        # --- Phase 4: Patrol management ---
        # [Implementation uses num_patrol_zones, patrol_zone_depth, aircraft_per_zone,
        #  capital_patrol_weight to compute and maintain patrol zones]
        # Similar to BalancedStrategy but with genome-driven parameters

        return decisions
```

**Note**: The `decide()` method above is a skeleton. The full implementation should include all patrol zone computation, aircraft type matching, and bomber/UAV usage mode logic. Use the existing `BalancedStrategy` as a template but replace all hard-coded values with `self._params.*` lookups.

### Step 5: GA Operators (Infrastructure)

#### `ga_operators.py`

```python
from __future__ import annotations
import math
import random as stdlib_random
from ..value_objects.genome import StrategyGenome

def random_genome(rng: stdlib_random.Random) -> StrategyGenome:
    return StrategyGenome(tuple(rng.random() for _ in range(StrategyGenome.GENE_COUNT)))

def tournament_select(population: list, k: int, rng: stdlib_random.Random):
    candidates = rng.sample(population, k)
    return max(candidates, key=lambda ind: ind.fitness)

def sbx_crossover(p1: StrategyGenome, p2: StrategyGenome, eta: float, prob: float, rng: stdlib_random.Random):
    if rng.random() > prob:
        return p1, p2
    
    genes1, genes2 = list(p1.genes), list(p2.genes)
    child1, child2 = [], []
    
    for i in range(StrategyGenome.GENE_COUNT):
        if i in StrategyGenome.DISCRETE_GENES:
            if rng.random() < 0.5:
                child1.append(genes1[i]); child2.append(genes2[i])
            else:
                child1.append(genes2[i]); child2.append(genes1[i])
        else:
            u = rng.random()
            if u <= 0.5:
                beta = (2 * u) ** (1 / (eta + 1))
            else:
                beta = (1 / (2 * (1 - u))) ** (1 / (eta + 1))
            c1 = max(0.0, min(1.0, 0.5 * ((1 + beta) * genes1[i] + (1 - beta) * genes2[i])))
            c2 = max(0.0, min(1.0, 0.5 * ((1 - beta) * genes1[i] + (1 + beta) * genes2[i])))
            child1.append(c1); child2.append(c2)
    
    return StrategyGenome(tuple(child1)), StrategyGenome(tuple(child2))

def polynomial_mutate(genome: StrategyGenome, eta_m: float, prob: float, rng: stdlib_random.Random):
    genes = list(genome.genes)
    for i in range(StrategyGenome.GENE_COUNT):
        if rng.random() > prob:
            continue
        if i in StrategyGenome.DISCRETE_GENES:
            genes[i] = rng.random()
        else:
            u = rng.random()
            if u < 0.5:
                delta = (2 * u) ** (1 / (eta_m + 1)) - 1
            else:
                delta = 1 - (2 * (1 - u)) ** (1 / (eta_m + 1))
            genes[i] = max(0.0, min(1.0, genes[i] + delta * 0.2))
    return StrategyGenome(tuple(genes))
```

### Step 6: GA Optimizer (Infrastructure)

#### `ga_optimizer.py`

```python
from __future__ import annotations
import time
from src.domain.ports.optimizer import OptimizerPort
from src.domain.value_objects.optimization_config import OptimizationConfig, OptimizationResult, GenerationStats
from .ga_operators import random_genome, tournament_select, sbx_crossover, polynomial_mutate

class GeneticAlgorithmOptimizer(OptimizerPort):
    def optimize(self, config, evaluate_fn, progress_callback=None):
        import random
        rng = random.Random(42)
        start = time.time()
        
        # Initialize population
        population = [
            _Individual(random_genome(rng)) for _ in range(config.population_size)
        ]
        history = []
        total_sims = 0
        
        for gen in range(config.generations):
            # Adaptive seeding
            seeds = 10 if gen < config.generations * 0.3 else config.seeds_per_evaluation
            
            # Evaluate fitness
            for ind in population:
                if ind.fitness is None:
                    ind.fitness = evaluate_fn(ind.genome)
                    total_sims += seeds
            
            # Record stats
            fitnesses = [ind.fitness for ind in population]
            stats = GenerationStats(
                generation=gen,
                best_fitness=max(fitnesses),
                mean_fitness=sum(fitnesses) / len(fitnesses),
                std_fitness=_stdev(fitnesses),
                worst_fitness=min(fitnesses),
                best_genome=max(population, key=lambda i: i.fitness).genome,
            )
            history.append(stats)
            
            if progress_callback:
                progress_callback(gen, config.generations, stats.best_fitness)
            
            # Convergence check
            if len(history) >= 5 and all(h.std_fitness < 0.5 for h in history[-5:]):
                break
            
            # Create next generation
            sorted_pop = sorted(population, key=lambda i: i.fitness, reverse=True)
            elite_count = max(1, int(config.population_size * config.elite_fraction))
            next_gen = [_Individual(ind.genome, ind.fitness) for ind in sorted_pop[:elite_count]]
            
            while len(next_gen) < config.population_size:
                p1 = tournament_select(population, config.tournament_size, rng)
                p2 = tournament_select(population, config.tournament_size, rng)
                c1, c2 = sbx_crossover(p1.genome, p2.genome, eta=20, prob=config.crossover_rate, rng=rng)
                c1 = polynomial_mutate(c1, eta_m=20, prob=config.mutation_rate, rng=rng)
                c2 = polynomial_mutate(c2, eta_m=20, prob=config.mutation_rate, rng=rng)
                next_gen.append(_Individual(c1))
                if len(next_gen) < config.population_size:
                    next_gen.append(_Individual(c2))
            
            population = next_gen[:config.population_size]
        
        best = max(population, key=lambda i: i.fitness)
        return OptimizationResult(
            best_genome=best.genome,
            best_fitness=best.fitness,
            generation_history=history,
            total_simulations=total_sims,
            wall_time_seconds=time.time() - start,
        )
```

### Step 7: Use Case (Application Layer)

#### `optimize_strategy.py`

```python
from __future__ import annotations
from statistics import mean
from src.domain.ports.optimizer import OptimizerPort
from src.domain.services.fitness import score

class OptimizeStrategyUseCase:
    def __init__(self, optimizer, batch_runner, scenario_config):
        self._optimizer = optimizer
        self._batch_runner = batch_runner
        self._scenario = scenario_config

    def execute(self, config):
        from src.infrastructure.optimization.parameterized_strategy import ParameterizedStrategy

        def evaluate(genome):
            strategy = ParameterizedStrategy(genome)
            results = self._batch_runner.run_batch(
                self._scenario, strategy, config.enemy_strategy_id,
                seed_start=1, seed_count=config.seeds_per_evaluation,
            )
            return mean(score(r) for r in results)

        return self._optimizer.optimize(config, evaluate)
```

### Step 8: API Endpoint

Add to `infrastructure/api/routes/`:

```
POST /api/v1/optimization/run        -> starts optimization, returns optimization_id
GET  /api/v1/optimization/{id}       -> returns status + results
```

## Testing

1. `test_genome_creation_validation` -- Invalid gene count or range raises error
2. `test_genome_decode_ranges` -- All decoded params within expected ranges
3. `test_parameterized_strategy_produces_decisions` -- Given a genome and state, returns valid decisions
4. `test_fitness_score_capital_destroyed_penalty` -- Capital loss = -1000
5. `test_ga_operators_preserve_bounds` -- Crossover and mutation keep genes in [0,1]
6. `test_tournament_selection_picks_fittest` -- Tournament reliably selects high-fitness individuals
7. `test_optimizer_improves_over_generations` -- Best fitness increases over generations (smoke test)

## Compute Budget

| Configuration | Simulations | Time (8 cores) |
|---|---|---|
| Quick test (pop=20, gen=10, seeds=5) | 1,000 | ~12 seconds |
| Standard (pop=100, gen=50, seeds=20) | 100,000 | ~21 minutes |
| Full (pop=100, gen=100, seeds=30) | 300,000 | ~63 minutes |

Start with the quick test to validate the pipeline works, then scale up.

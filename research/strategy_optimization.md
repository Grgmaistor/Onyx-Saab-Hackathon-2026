# Strategy Optimization via Evolutionary Algorithms

## Question
How can we use evolutionary optimization (genetic algorithms, co-evolution) to automatically discover optimal air defense strategies within the Boreal Passage simulation engine? What is the best approach given our architecture?

## Summary
A complete design for a Genetic Algorithm (GA) based strategy optimizer that evolves parameterized strategies through the existing simulation batch infrastructure. The approach encodes strategy behavior as a 28-gene chromosome, uses weighted multi-objective fitness scoring, tournament selection with SBX crossover and polynomial mutation, and competitive co-evolution with a Hall of Fame archive for robustness. The design fits cleanly into the existing hexagonal architecture. Complementary approaches (Bayesian optimization, MCTS, RL) are analyzed. Confidence: MEDIUM -- based on published defense simulation optimization literature, GA game AI research, and architectural analysis of the codebase.

---

## Findings

### 1. Strategy DNA Encoding (Chromosome Design)

#### Encoding Philosophy

The chromosome represents the **tunable parameters** of a `ParameterizedStrategy` -- a strategy class that implements `StrategyPort` but whose behavior is driven entirely by a parameter vector rather than hard-coded logic. Each gene is normalized to [0.0, 1.0] internally and decoded to domain-meaningful ranges at evaluation time.

This approach is well-supported by research: parameterized rule-based strategies evolved by GAs perform comparably to expert-tuned parameters in combat simulations (see Sources).

#### Gene Catalog (28 genes in 5 functional groups)

**Group A: Resource Management (6 genes)**

| # | Gene Name | Decoded Range | Description |
|---|-----------|---------------|-------------|
| 0 | `fuel_rtb_threshold` | [0.10, 0.40] | Fraction of fuel capacity below which aircraft must RTB |
| 1 | `reserve_fraction` | [0.10, 0.70] | Fraction of total aircraft to hold in reserve |
| 2 | `min_fuel_to_launch` | [0.30, 0.90] | Minimum fuel fraction required to launch from base |
| 3 | `patrol_fuel_floor` | [0.20, 0.50] | Fuel level at which a patrolling aircraft should RTB |
| 4 | `ammo_rtb_threshold` | {0, 1, 2} | RTB when ammo drops to this count |
| 5 | `sortie_launch_delay` | [0, 10] ticks | Minimum ticks between re-launching same aircraft |

**Group B: Threat Response (7 genes)**

| # | Gene Name | Decoded Range | Description |
|---|-----------|---------------|-------------|
| 6 | `threat_distance_weight` | [0.0, 1.0] | Weight of distance-to-capital vs distance-to-nearest-city |
| 7 | `bomber_priority_boost` | [1.0, 5.0] | Multiplier on threat score for BOMBER targets |
| 8 | `combat_plane_priority` | [1.0, 3.0] | Multiplier on threat score for COMBAT_PLANE targets |
| 9 | `uav_priority` | [0.5, 2.0] | Multiplier on threat score for UAV targets |
| 10 | `drone_swarm_priority` | [0.3, 1.5] | Multiplier on threat score for DRONE_SWARM targets |
| 11 | `max_interceptors_per_threat` | {1, 2, 3} | Max aircraft to assign against a single threat |
| 12 | `threat_range_engage` | [100, 500] km | Only engage threats within this distance of assets |

**Group C: Aircraft Type Preferences (5 genes)**

| # | Gene Name | Decoded Range | Description |
|---|-----------|---------------|-------------|
| 13 | `prefer_cp_vs_bomber` | [0.0, 1.0] | Preference for sending combat planes against bombers |
| 14 | `prefer_cp_vs_cp` | [0.0, 1.0] | Preference for combat planes against enemy combat planes |
| 15 | `use_drones_vs_drones` | [0.0, 1.0] | Willingness to send drone swarms against enemy drones |
| 16 | `bomber_usage_mode` | {HOLD, ESCORT, OFFENSIVE} | How to deploy own bombers |
| 17 | `uav_usage_mode` | {PATROL, INTERCEPT, SCOUT} | Primary role for UAVs |

**Group D: Patrol & Positioning (6 genes)**

| # | Gene Name | Decoded Range | Description |
|---|-----------|---------------|-------------|
| 18 | `num_patrol_zones` | {1, 2, 3, 4, 5} | Number of simultaneous patrol zones |
| 19 | `patrol_zone_depth` | [0.0, 1.0] | How far forward to push patrol zones (0=capital, 1=strait midpoint) |
| 20 | `aircraft_per_zone` | {1, 2, 3, 4} | Desired aircraft per patrol zone |
| 21 | `patrol_zone_spread` | [100, 400] km | Width of patrol zone coverage |
| 22 | `capital_patrol_weight` | [0.0, 1.0] | Fraction of patrol allocation for capital zone |
| 23 | `forward_patrol_bias` | [0.0, 1.0] | Bias toward patrolling strait vs own territory |

**Group E: Engagement Rules (4 genes)**

| # | Gene Name | Decoded Range | Description |
|---|-----------|---------------|-------------|
| 24 | `launch_aggressiveness` | [0.0, 1.0] | 0=launch only on detection near capital, 1=launch all immediately |
| 25 | `commit_ratio_vs_threats` | [0.5, 3.0] | Ratio of interceptors per detected threat |
| 26 | `retreat_on_disadvantage` | [0.0, 1.0] | Willingness to disengage when outnumbered |
| 27 | `retaliation_escalation` | [0.0, 1.0] | How much to escalate when losing engagements |

#### Why This Encoding

- **Flat vector**: Standard GA operators (crossover, mutation) work uniformly across all genes
- **[0,1] normalization**: Operators don't need gene-specific logic; decoding to domain ranges happens in `ParameterizedStrategy.decode()`
- **Discrete genes**: Stored as continuous floats, decoded by quantization: `categories[floor(value * len(categories))]`
- **28 genes**: Within the sweet spot for GA optimization (10-50 dimensions); avoids curse of dimensionality

---

### 2. Fitness Function Design

#### Approach: Weighted Scalarization with Hard Constraints

```
fitness(genome) = mean_over_N_seeds(score(run_simulation(config, ParameterizedStrategy(genome), enemy, seed_i)))
```

#### Scoring Function

```python
def score(result: SimulationResult) -> float:
    m = result.metrics

    # Hard constraint: capital must survive
    if not m.capital_survived:
        return -1000.0

    # Outcome bonus
    outcome_score = {WIN: 100.0, TIMEOUT: 20.0, LOSS: -100.0}[result.outcome]

    # Component scores (normalized to roughly [0, 100])
    casualty_score = -min(m.total_civilian_casualties / 1000.0, 100.0)
    aircraft_score = (m.aircraft_remaining / (m.aircraft_remaining + m.aircraft_lost + 0.001)) * 50.0
    engagement_score = m.engagement_win_rate * 50.0
    cities_score = m.cities_defended * 15.0          # up to 3 cities * 15 = 45
    fuel_score = m.fuel_efficiency * 20.0
    response_score = max(0, 30.0 - m.response_time_avg)
    duration_bonus = max(0, (1000 - m.total_ticks) / 1000.0) * 10.0 if result.outcome == WIN else 0

    # Weighted combination
    return (
        outcome_score * 1.0
      + casualty_score * 2.0       # heavily penalize civilian casualties
      + aircraft_score * 1.0
      + engagement_score * 1.0
      + cities_score * 1.5
      + fuel_score * 0.5
      + response_score * 0.8
      + duration_bonus * 0.3
    )
```

#### Configurable Weight Profiles

| Profile | Casualties | Win | Aircraft | Engagement | Cities | Fuel | Response |
|---------|-----------|-----|----------|-----------|--------|------|----------|
| Balanced | 2.0 | 1.0 | 1.0 | 1.0 | 1.5 | 0.5 | 0.8 |
| Humanitarian | 5.0 | 0.5 | 0.5 | 0.5 | 3.0 | 0.3 | 1.5 |
| Aggressive | 0.5 | 3.0 | 0.3 | 2.0 | 0.5 | 0.2 | 0.5 |
| Attrition | 1.0 | 1.5 | 2.5 | 1.5 | 1.0 | 1.5 | 0.5 |

#### Seeds per Evaluation

| Seeds | Statistical Quality | Compute (at 100ms/sim) | Recommendation |
|-------|--------------------|-----------------------|----------------|
| 5 | High variance, noisy | 0.5s | Too few |
| 10 | Moderate variance | 1.0s | Minimum viable (early generations) |
| 20 | Low variance | 2.0s | **Recommended default** |
| 50 | Very stable | 5.0s | Final validation only |

**Adaptive seeding**: Start with 10 seeds in early generations, increase to 20-30 in later generations. Saves ~40% total compute.

---

### 3. GA Operators

#### Selection: Tournament (k=3)

Tournament selection with k=3 provides moderate selection pressure, handles noisy fitness well, and is the standard choice for strategy game optimization.

```
TOURNAMENT_SELECT(population, k=3):
    candidates = random.sample(population, k)
    return max(candidates, key=lambda ind: ind.fitness)
```

#### Crossover: Simulated Binary Crossover (SBX) + Uniform for Discrete

- **Continuous genes**: SBX with distribution index eta=20 (creates offspring near parents with controllable spread)
- **Discrete genes** (indices 4, 11, 16, 17, 18, 20): Uniform crossover (each gene inherited from one parent with P=0.5)
- **Crossover rate**: 0.9

#### Mutation: Polynomial + Random Reset

- **Continuous genes**: Polynomial mutation with eta_m=20
- **Discrete genes**: Random reset
- **Per-gene probability**: 1/28 = 0.036 (standard 1/N recommendation)

#### Elitism

Top 5% (5 of 100 individuals) preserved unchanged into next generation.

#### Recommended Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Population size | 100 | Good balance for 28-gene problem |
| Generations | 50-100 | 50 gens = ~21 min on 8 cores |
| Crossover rate | 0.9 | Standard for SBX |
| Mutation rate per gene | 1/28 = 0.036 | Standard 1/N |
| Tournament size | 3 | Moderate selection pressure |
| Elitism | 5% (5 individuals) | Preserve best solutions |
| Seeds per evaluation | 20 (adaptive: 10 early, 30 late) | Statistical stability |

#### Compute Budget

```
Per generation:  100 individuals x 20 seeds = 2,000 simulations
                 At ~100ms/sim on 8 cores: ~25 seconds

Full run (50 generations): 100,000 simulations, ~21 minutes on 8 cores
Full run (100 generations): 200,000 simulations, ~42 minutes on 8 cores
```

---

### 4. Co-evolution Approach

#### Problem: Overfitting to Fixed Enemy

Evolving against a single fixed enemy (e.g., `BalancedStrategy`) produces strategies that exploit that enemy's specific weaknesses but fail against others.

#### Solution: Competitive Co-evolution with Hall of Fame

```
COEVOLUTION_LOOP:
    pop_A = initialize_population(100)     # "Our" strategies (North)
    pop_B = initialize_population(50)      # Enemy strategies (South)
    hall_of_fame_A = []
    hall_of_fame_B = []

    for generation in range(100):
        # Evaluate pop_A against MIX of opponents:
        #   50% current pop_B (co-evolution pressure)
        #   30% hall_of_fame_B (robustness against past champions)
        #   20% fixed hand-coded strategies (baseline anchoring)

        for individual in pop_A:
            opponents = (
                sample(pop_B, 3) +
                sample(hall_of_fame_B, min(2, len(hall_of_fame_B))) +
                [DefensiveStrategy(), AggressiveStrategy()]
            )
            individual.fitness = mean([
                mean_score_over_seeds(individual, opp, seeds=10)
                for opp in opponents
            ])

        # Similarly evaluate pop_B, then evolve both populations
        # Update hall of fame with generation champion if new best
```

#### Why This Design

1. **Current enemy population**: Arms race pressure -- must beat current opponents
2. **Hall of Fame**: Prevents "forgetting" -- must still beat past champions (avoids cycling pathology)
3. **Fixed baselines**: Anchors fitness landscape -- ensures competitiveness with human-designed strategies

#### Robustness Validation

After evolution, run a **round-robin tournament** of top 10 evolved strategies against all hand-coded strategies + top 5 evolved enemy strategies + each other. The robust winner has highest **mean** performance across all opponents.

---

### 5. Integration with Hexagonal Architecture

```
Domain Layer (no external deps):
  domain/value_objects/genome.py          # StrategyGenome dataclass (frozen)
  domain/ports/optimizer.py               # OptimizerPort ABC
  domain/services/fitness.py              # score() pure function

Application Layer:
  application/optimize_strategy.py        # OptimizeStrategyUseCase
                                          # Orchestrates GA loop via ports

Infrastructure Layer:
  infrastructure/optimization/
    ga_optimizer.py                        # Implements OptimizerPort
    parameterized_strategy.py             # ParameterizedStrategy(StrategyPort)
                                          # Decodes genome -> decide() behavior
```

**Dependency flow**: Infrastructure -> Application -> Domain (inward only, hexagonal rules respected)

The `ParameterizedStrategy` lives in infrastructure because it's a concrete adapter implementing the `StrategyPort` interface. The genome value object and fitness function live in the domain as pure logic.

#### Key Classes

```python
# Domain
@dataclass(frozen=True)
class StrategyGenome:
    genes: tuple[float, ...]  # Length 28, each in [0.0, 1.0]

class OptimizerPort(ABC):
    @abstractmethod
    def optimize(self, config: OptimizationConfig, evaluate_fn) -> OptimizationResult: ...

# Application
class OptimizeStrategyUseCase:
    def execute(self, config) -> OptimizationResult:
        def evaluate(genome):
            strategy = ParameterizedStrategy(genome)
            results = self._batch_runner.run(strategy, config.seeds_per_evaluation)
            return mean(score(r) for r in results)
        return self._optimizer.optimize(config, evaluate)
```

#### API Endpoints (New)

```
POST /api/v1/optimization/run           # Start optimization
GET  /api/v1/optimization/{id}/status   # Check progress
GET  /api/v1/optimization/{id}/results  # Get results + Pareto front
WS   /ws/optimization/{id}              # Live progress updates
```

---

### 6. GA Loop Pseudocode

```
EVOLVE_STRATEGY(config):
    population = [random_genome() for _ in range(POP_SIZE)]
    hall_of_fame = []
    history = []

    for gen in range(GENERATIONS):
        # Adaptive seeding
        seeds = 10 if gen < 0.3 * GENERATIONS else 20 if gen < 0.7 * GENERATIONS else 30

        # Evaluate fitness (parallel via ProcessPoolExecutor)
        for individual in population:
            if coevolution_enabled:
                opponents = select_opponent_mix(hall_of_fame, fixed_strategies, enemy_pop)
                individual.fitness = mean([evaluate_vs(individual, opp, seeds) for opp in opponents])
            else:
                individual.fitness = evaluate_vs_fixed_enemy(individual, BalancedStrategy(), seeds)

        # Record statistics
        history.append(GenerationStats(gen, best, mean, stdev))

        # Update hall of fame
        best = max(population, key=fitness)
        if new_best: hall_of_fame.append(best); trim_to_20()

        # Convergence check
        if stdev < 0.5 for 5 consecutive generations: break

        # Create next generation
        next_gen = top_5_percent(population)  # elitism
        while len(next_gen) < POP_SIZE:
            p1, p2 = tournament_select(population, k=3), tournament_select(population, k=3)
            c1, c2 = sbx_crossover(p1, p2, prob=0.9)
            c1 = polynomial_mutate(c1, prob=1/28)
            c2 = polynomial_mutate(c2, prob=1/28)
            next_gen.extend([c1, c2])
        population = next_gen[:POP_SIZE]

    # Post-hoc Pareto analysis on top 50 genomes evaluated with 50 seeds
    pareto_front = compute_pareto_front(top_50, objectives=[
        ("win_rate", "maximize"),
        ("mean_casualties", "minimize"),
        ("mean_aircraft_survival", "maximize"),
    ])

    return OptimizationResult(best_genome, best_fitness, history, pareto_front)
```

---

### 7. Alternative / Complementary Approaches

| Criteria | GA (parameterized) | Bayesian Opt. | MCTS | RL (deep) |
|----------|-------------------|---------------|------|-----------|
| Sample efficiency | Medium (100K) | High (500) | N/A (per-tick) | Low (1M+) |
| Implementation effort | Low | Low | Medium | High |
| Interpretability | High (parameters) | High | Medium | Low |
| Multi-objective support | Good (NSGA-II) | Limited | N/A | Limited |
| Co-evolution support | Natural | Difficult | N/A | Possible (self-play) |
| Parallelizability | Excellent | Limited | Limited | Good |
| Best for | Strategy-level optimization | Fine-tuning | Tactical decisions | End-to-end policy |

#### Bayesian Optimization
- **Pro**: Far more sample-efficient (100-500 evaluations vs 100K)
- **Con**: Struggles with 28 dimensions (GP fitting is O(n^3))
- **Recommendation**: Use as a **refinement step** after GA converges. Run GA 30 generations, then BO 200 evaluations to fine-tune top genome's continuous parameters.

#### Monte Carlo Tree Search (MCTS)
- **Pro**: Excellent for per-tick tactical decisions
- **Con**: Branching factor is enormous (~27 aircraft x multiple actions per tick)
- **Recommendation**: **Complementary, not competing**. Use GA for macro-strategy parameters, MCTS at runtime for micro-tactical decisions within strategic constraints. Defer to later phase.

#### Reinforcement Learning
- **Pro**: Can learn complex state-dependent policies; modern MARL handles multi-agent coordination
- **Con**: Requires millions of episodes, black-box policies, harder to implement, reward shaping errors
- **Recommendation**: Most powerful long-term but highest complexity. For hackathon, GA on parameterized strategies is more practical. Consider RL as future enhancement.

#### Simulated Annealing
- **Pro**: Simple to implement
- **Con**: Single-threaded (doesn't exploit our parallelism), no population diversity
- **Recommendation**: Not recommended -- dominated by GA when parallel evaluation is available.

---

### 8. Implementation Roadmap

**Phase 1: Foundation**
1. `StrategyGenome` value object in domain
2. `ParameterizedStrategy` in infrastructure (most critical -- translates 28 genes into coherent decisions)
3. `score()` fitness function in domain services
4. Unit tests for genome encoding/decoding

**Phase 2: GA Engine**
5. GA operators (tournament, SBX, polynomial mutation)
6. `OptimizeStrategyUseCase` orchestration
7. `GeneticAlgorithmOptimizer` (implements `OptimizerPort`)
8. Integration with `RunBatchUseCase` for parallel fitness evaluation
9. Progress reporting via `EventPublisher`

**Phase 3: Co-evolution & Robustness**
10. Hall of Fame archive
11. Opponent mixing (current pop + HoF + fixed baselines)
12. Round-robin validation tournament
13. Convergence detection (early stopping)

**Phase 4: Analysis & Refinement**
14. Pareto front computation
15. Bayesian optimization refinement for top genomes
16. Visualization endpoints (fitness history, parameter distributions, Pareto front)
17. API endpoints for optimization management

### Recommended Libraries

| Library | Purpose | Notes |
|---------|---------|-------|
| **pymoo** | Multi-objective (NSGA-II), Pareto front | Use for post-hoc Pareto analysis |
| **DEAP** | GA framework | Alternative: supports custom operators and co-evolution |
| **Optuna** | Bayesian optimization refinement | Phase 4 fine-tuning |
| Custom (~200 lines) | Core GA loop | Simpler than framework for hackathon; directly uses existing `run_simulation` |

---

## Sources

1. [Hindawi - Using GA in Simulation Models of Conflict](https://www.hindawi.com/journals/aai/2010/701904/) -- GA for higher-level planning in military simulation
2. [RAND - Allocation of Forces Using Genetic Algorithms (TR-423)](https://www.rand.org/content/dam/rand/pubs/technical_reports/2008/RAND_TR423.pdf) -- GA force allocation optimization
3. [ResearchGate - Generating War Game Strategies using GA](https://www.researchgate.net/publication/3949330) -- GA strategy optimization in wargames
4. [ScienceDirect - Hybrid Multi-Objective EA for UAV Defense](https://www.sciencedirect.com/science/article/abs/pii/S221065022400110X) -- Multi-objective optimization for UAV operations
5. [ScienceDirect - Evolutionary Multi-Agent RL for Multi-UAV Air Combat](https://www.sciencedirect.com/science/article/abs/pii/S0950705124006348) -- RL comparison point
6. [IEEE - Robustness of Coevolved Strategies in RTS Games](https://ieeexplore.ieee.org/document/6557725/) -- Co-evolution pathology and Hall of Fame solution
7. [Springer - Co-Evolutionary Optimization of Autonomous Agents](https://link.springer.com/content/pdf/10.1007/978-3-662-45523-4_31.pdf) -- Co-evolution design patterns
8. [Deb et al. - NSGA-II](https://sci2s.ugr.es/sites/default/files/files/Teaching/OtherPostGraduateCourses/Metaheuristicas/Deb_NSGAII.pdf) -- Multi-objective GA with Pareto front
9. [pymoo - Multi-objective Optimization in Python](https://pymoo.org/) -- Library for Pareto analysis
10. [GitHub - DEAP](https://github.com/DEAP/deap) -- Distributed Evolutionary Algorithms in Python
11. [MDPI - Choosing Mutation and Crossover Ratios for GAs](https://www.mdpi.com/2078-2489/10/12/390) -- 1/N mutation rate recommendation
12. [Research.Google - Bayesian-Optimized Genetic Algorithm](https://research.google.com/pubs/archive/46487.pdf) -- Hybrid GA+BO approach
13. [ArXiv - Time Efficiency in Optimization with Bayesian-EA Hybrid](https://arxiv.org/pdf/2005.04166) -- BO refinement after GA
14. [INFORMS - Simulation-based Optimization of Air Force Mission Planning](https://informs-sim.org/wsc23papers/203.pdf) -- Simulation optimization in defense
15. [Gamedeveloper - Genetic Algorithms in Games](https://www.gamedeveloper.com/design/genetic-algorithms-in-games-part-1-) -- GA for game AI
16. [Nature - Autonomous Air Combat Decision Making via GNN and RL](https://www.nature.com/articles/s41598-025-00463-y) -- Modern RL for air combat
17. [CSIAC - Optimization for Defense Simulation Models](https://csiac.dtic.mil/articles/optimization-and-analysis-for-defense-simulation-models/) -- Defense simulation optimization overview

## Methodology

Research was conducted on 2026-04-17 using web searches across defense simulation optimization, genetic algorithms for game AI, evolutionary strategy optimization, and military wargaming literature. The design integrates findings from RAND/CNAS defense research, academic GA/evolutionary computing literature, and game AI publications. The architecture was designed by analyzing the existing codebase structure (hexagonal architecture, pure simulation functions, batch execution, strategy port interface) and mapping optimization components to appropriate layers.

## Confidence Assessment

- **Overall confidence**: MEDIUM
- **High confidence**: GA architecture fit (well-established technique for parameterized strategy optimization), co-evolution with Hall of Fame (proven approach in game AI), compute budget estimates (based on existing batch infrastructure)
- **Medium confidence**: Gene catalog and ranges (reasonable but will require tuning), fitness function weights (subjective; profiles help), SBX/polynomial mutation parameters (standard values, may need adjustment)
- **Low confidence**: Specific convergence timeline (depends on fitness landscape smoothness), co-evolution stability (can cycle in practice), Bayesian optimization integration details (depends on implementation)
- **Recommendations**: Start with Phase 1-2, validate on small runs (10 generations, population 20), tune parameters empirically before committing to full 100-generation runs

## Applied In
- `backend/src/domain/value_objects/genome.py` -- StrategyGenome dataclass
- `backend/src/domain/ports/optimizer.py` -- OptimizerPort interface
- `backend/src/domain/services/fitness.py` -- Fitness scoring function
- `backend/src/application/optimize_strategy.py` -- OptimizeStrategyUseCase
- `backend/src/infrastructure/optimization/` -- GA implementation + ParameterizedStrategy
- `Development/API.md` -- New optimization endpoints

## Last Updated
2026-04-17

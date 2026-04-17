# Architecture — Hexagonal (Ports & Adapters)

## Overview

This project uses **Hexagonal Architecture** (also called Ports & Adapters) to keep the simulation domain pure, testable, and extensible. The core simulation logic has zero knowledge of databases, HTTP, or file systems.

## Why Hexagonal

1. **Extensibility**: Adding a new aircraft type = one new class in the domain. No infrastructure changes.
2. **Testability**: Domain logic is tested in isolation — no mocks for databases or APIs needed.
3. **Swappability**: Replace SQLite with Postgres by writing one new adapter. Replace FastAPI with gRPC. The domain never changes.
4. **Parallel development**: Frontend team works on adapters, simulation team works on domain. No conflicts.

## Layer Diagram

```
┌──────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js)                     │
│   Dashboard │ Sim Control │ Map Viz │ Results Table       │
└────────────────────────┬─────────────────────────────────┘
                         │ HTTP + WebSocket
┌────────────────────────┴─────────────────────────────────┐
│              INFRASTRUCTURE LAYER (Adapters)               │
│                                                           │
│  FastAPI Routes ──→ translate HTTP to use-case calls      │
│  SQLiteRepo ──────→ implements SimulationRepository port  │
│  WebSocketPub ────→ implements EventPublisher port        │
│  JSONExporter ────→ implements ExportPort                 │
│  ProcessPoolRunner → orchestrates parallel sim execution  │
└────────────────────────┬─────────────────────────────────┘
                         │ calls (depends on)
┌────────────────────────┴─────────────────────────────────┐
│              APPLICATION LAYER (Use Cases)                 │
│                                                           │
│  RunSimulationUseCase    │ RunBatchUseCase                │
│  GetResultsUseCase       │ CompareResultsUseCase          │
│  CreateScenarioUseCase   │ ExportReplayUseCase            │
│                                                           │
│  Orchestrates domain objects through ports.               │
│  Contains NO business logic — only coordination.          │
└────────────────────────┬─────────────────────────────────┘
                         │ calls (depends on)
┌────────────────────────┴─────────────────────────────────┐
│                    DOMAIN LAYER (Core)                     │
│                                                           │
│  Entities:          │ Services:            │ Ports:        │
│   Aircraft (ABC)    │  CombatResolver      │  SimRepo      │
│    ├ DroneSwarm     │  FuelManager         │  EventPub     │
│    ├ UAV            │  MovementCalculator  │  StrategyPort │
│    ├ CombatPlane    │  MetricsCollector    │  MetricsPort  │
│    └ Bomber         │  SimulationClock     │  ExportPort   │
│   Base              │                      │               │
│   City              │ Value Objects:       │               │
│   Battle            │  Position            │               │
│   Simulation        │  FuelState           │               │
│   SimulationState   │  AmmoState           │               │
│                     │  CombatOdds          │               │
│                     │  CombatResult        │               │
│                     │  SimulationTick      │               │
│                     │  Decision            │               │
└──────────────────────────────────────────────────────────┘
```

## Dependency Rule

**Dependencies ALWAYS point inward.** This is the single most important rule.

```
Infrastructure → Application → Domain
     ✓               ✓           ✗ (domain depends on nothing external)
```

- `domain/` imports ONLY from `domain/` and Python stdlib.
- `application/` imports from `domain/` and Python stdlib.
- `infrastructure/` imports from `application/`, `domain/`, and external libraries (FastAPI, SQLAlchemy, etc.).

**Violations of this rule must be rejected in code review.**

## Directory → Layer Mapping

```
backend/src/
├── domain/                    # DOMAIN LAYER
│   ├── entities/              # Core business objects with identity
│   │   ├── __init__.py
│   │   ├── aircraft.py        # Aircraft ABC + DroneSwarm, UAV, CombatPlane, Bomber
│   │   ├── base.py            # Military base with capacity, position, fuel storage
│   │   ├── city.py            # City/Capital with population, position
│   │   ├── battle.py          # Engagement between forces
│   │   └── simulation.py      # Simulation aggregate root
│   ├── value_objects/         # Immutable values without identity
│   │   ├── __init__.py
│   │   ├── position.py        # (x_km, y_km) coordinate on the map
│   │   ├── fuel_state.py      # Current fuel level, burn tracking
│   │   ├── combat_result.py   # Outcome of an engagement
│   │   └── decision.py        # A strategic action (LAUNCH, INTERCEPT, etc.)
│   ├── ports/                 # Interfaces the domain expects
│   │   ├── __init__.py
│   │   ├── simulation_repository.py  # Save/load simulation results
│   │   ├── event_publisher.py        # Publish simulation events
│   │   ├── strategy.py               # Decision-making interface
│   │   └── export.py                 # Export replay data
│   └── services/              # Domain logic that spans entities
│       ├── __init__.py
│       ├── combat_resolver.py # Resolve engagements using probability tables
│       ├── movement.py        # Calculate travel time, fuel consumption
│       ├── fuel_manager.py    # Track refueling, base capacity
│       └── metrics.py         # Compute simulation metrics
│
├── application/               # APPLICATION LAYER
│   ├── __init__.py
│   ├── run_simulation.py      # Single simulation use case
│   ├── run_batch.py           # Batch simulation use case
│   ├── get_results.py         # Query results use case
│   ├── compare_results.py     # Compare simulation outcomes
│   └── export_replay.py       # Export replay for graphics team
│
└── infrastructure/            # INFRASTRUCTURE LAYER
    ├── persistence/
    │   ├── __init__.py
    │   ├── sqlite_repo.py     # Implements SimulationRepository
    │   ├── models.py          # SQLAlchemy table models
    │   └── database.py        # DB connection/session management
    ├── api/
    │   ├── __init__.py
    │   ├── main.py            # FastAPI app factory
    │   ├── dependencies.py    # Dependency injection wiring
    │   ├── routes/
    │   │   ├── __init__.py
    │   │   ├── simulations.py # /simulations endpoints
    │   │   ├── scenarios.py   # /scenarios endpoints
    │   │   └── results.py     # /results endpoints
    │   └── websocket.py       # WebSocket handler for live updates
    ├── export/
    │   ├── __init__.py
    │   └── json_export.py     # Implements ExportPort → JSON files
    └── simulation/
        ├── __init__.py
        └── process_pool_runner.py  # Parallel sim execution
```

## Ports (Interfaces)

Ports are abstract base classes defined in the domain. Infrastructure provides concrete implementations.

### SimulationRepository

```python
class SimulationRepository(ABC):
    @abstractmethod
    def save(self, result: SimulationResult) -> str: ...

    @abstractmethod
    def get(self, simulation_id: str) -> SimulationResult | None: ...

    @abstractmethod
    def list_by_batch(self, batch_id: str) -> list[SimulationResult]: ...

    @abstractmethod
    def get_metrics(self, simulation_id: str) -> SimulationMetrics: ...
```

### StrategyPort

```python
class StrategyPort(ABC):
    @abstractmethod
    def decide(self, state: SimulationState) -> list[Decision]: ...
```

### EventPublisher

```python
class EventPublisher(ABC):
    @abstractmethod
    def publish_tick(self, simulation_id: str, tick: SimulationTick) -> None: ...

    @abstractmethod
    def publish_complete(self, simulation_id: str, result: SimulationResult) -> None: ...
```

### ExportPort

```python
class ExportPort(ABC):
    @abstractmethod
    def export_replay(self, simulation_id: str, ticks: list[SimulationTick]) -> str: ...
```

## Dependency Injection

Wiring happens in `infrastructure/api/dependencies.py`. The FastAPI app constructs adapters and injects them into use cases:

```python
def get_simulation_repo() -> SimulationRepository:
    return SQLiteSimulationRepo(get_db_session())

def get_run_simulation_use_case() -> RunSimulationUseCase:
    return RunSimulationUseCase(
        repo=get_simulation_repo(),
        publisher=get_event_publisher(),
    )
```

Use cases receive ports (interfaces), never concrete adapters.

## How to Add a New Adapter

Example: switching from SQLite to Postgres.

1. Create `backend/src/infrastructure/persistence/postgres_repo.py`.
2. Implement `SimulationRepository` interface.
3. Update `dependencies.py` to return the new adapter.
4. Zero changes to domain or application layers.

## How to Add a New Use Case

1. Create a new file in `backend/src/application/`.
2. Accept ports via constructor injection.
3. Orchestrate domain entities and services.
4. Create a route in `infrastructure/api/routes/` that calls the use case.

## Cross-Cutting Concerns

| Concern | Approach |
|---|---|
| Logging | Python `logging` module. Infrastructure layer only. Domain uses return values, not logging. |
| Error handling | Domain raises domain-specific exceptions. Infrastructure catches and translates to HTTP responses. |
| Configuration | Environment variables loaded in infrastructure, passed as plain values to domain. |
| Serialization | Pydantic models in the API layer. Domain uses plain dataclasses/attrs. |

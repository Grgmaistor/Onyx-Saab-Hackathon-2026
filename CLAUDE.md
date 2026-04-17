# Boreal Passage — Air Combat Simulation Engine

## Project Overview

Strategic air combat simulation engine for the "Boreal Passage" scenario. Two countries (X = North, Y = South) separated by a maritime strait. The engine runs thousands of parallel simulations with different strategies and compares outcomes to identify optimal decision patterns for air defense controllers.

## Quick Start

```bash
docker compose up --build
```

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000

## Tech Stack

| Layer | Technology |
|---|---|
| Simulation Engine | Python 3.12, concurrent.futures.ProcessPoolExecutor |
| Backend API | FastAPI, Pydantic, SQLAlchemy |
| Frontend | Next.js 14, React, TypeScript, Pixi.js (map viz) |
| Database | SQLite (file: `data/simulations.db`) |
| Containers | Docker Compose (2 services: backend, frontend) |

## Architecture

**Hexagonal Architecture (Ports & Adapters).** Read `Development/ARCHITECTURE.md` for full details.

Rules every contributor and coding agent MUST follow:

1. **Domain core has ZERO external dependencies.** Nothing in `backend/src/domain/` imports FastAPI, SQLAlchemy, or any infrastructure library. Only Python stdlib and domain-internal imports.
2. **Dependencies point inward.** Infrastructure → Application → Domain. Never the reverse.
3. **New features start at the domain.** Define the entity/port/service first, then wire adapters.
4. **All aircraft types inherit from `Aircraft` ABC** in `backend/src/domain/entities/aircraft.py`.
5. **All strategies implement `StrategyPort`** in `backend/src/domain/ports/strategy.py`.
6. **Simulations are pure functions.** `run_simulation(config, strategy, seed) → SimulationResult`. No side effects during execution.

## Project Structure

```
├── CLAUDE.md                          # THIS FILE — read first
├── docker-compose.yml
├── .env.example
├── data/                              # Persistent data (gitignored)
│   └── simulations.db
├── Development/                       # All development guides
│   ├── ARCHITECTURE.md                # Hexagonal architecture details
│   ├── DOMAIN.md                      # Entities, value objects, combat rules
│   ├── SIMULATION.md                  # Tick model, strategies, parallelism
│   ├── API.md                         # REST + WebSocket specification
│   ├── RESEARCH.md                    # How to conduct and store research
│   └── CONTRIBUTING.md                # Code style, git, testing, how-to guides
├── research/                          # AI research findings (markdown + sources)
├── scenario/                          # Scenario configs and strategy definitions
│   ├── boreal_passage.json
│   └── strategies/
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── src/
│       ├── domain/                    # PURE domain — no external deps
│       │   ├── entities/
│       │   ├── value_objects/
│       │   ├── ports/
│       │   └── services/
│       ├── application/               # Use cases — orchestrates domain
│       └── infrastructure/            # Adapters — implements ports
│           ├── persistence/
│           ├── api/
│           ├── export/
│           └── simulation/
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
└── tests/
```

## Development Rules

### Before Writing Code

1. Read `Development/ARCHITECTURE.md` to understand the hexagonal layers.
2. Read `Development/DOMAIN.md` to understand entities and combat rules.
3. Read `Development/CONTRIBUTING.md` for code style and workflow.
4. If your task involves simulation logic, read `Development/SIMULATION.md`.
5. If your task involves API endpoints, read `Development/API.md`.

### When Adding a New Aircraft Type

1. Create a new class in `backend/src/domain/entities/aircraft.py` inheriting from `Aircraft`.
2. Define all required attributes: speed, fuel capacity, burn rate, refuel time, combat matchups.
3. Add the type to `AircraftType` enum.
4. No infrastructure changes needed — the simulation engine picks it up automatically.
5. Update `Development/DOMAIN.md` with the new type's stats.
6. If stats require research, follow `Development/RESEARCH.md` workflow first.

### When Adding a New Strategy

1. Create a new file in `scenario/strategies/`.
2. Implement the `StrategyPort` interface from `backend/src/domain/ports/strategy.py`.
3. The strategy receives full simulation state and returns a list of `Decision` objects.
4. Register the strategy in the strategy registry.
5. Test with a single simulation before running batches.

### When Adding a New API Endpoint

1. Define the use case in `backend/src/application/`.
2. Create the route in `backend/src/infrastructure/api/routes/`.
3. Use Pydantic models for request/response schemas.
4. Document in `Development/API.md`.

### When Doing Research

1. Follow the workflow in `Development/RESEARCH.md`.
2. All findings go to `research/` as markdown files.
3. Include sources, methodology, and confidence levels.
4. Reference research files from domain code comments when stats are based on research.

## Environment Variables

```bash
# Backend
DATABASE_URL=sqlite:///data/simulations.db
SIMULATION_MAX_WORKERS=auto          # defaults to os.cpu_count()
SIMULATION_DEFAULT_TICK_MINUTES=5    # real-time minutes per tick
LOG_LEVEL=INFO

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## Key Concepts

- **Tick**: One discrete time step in a simulation (default = 5 minutes of simulated time).
- **Strategy**: A pluggable decision-making function that controls one side's forces.
- **Scenario**: The map, bases, cities, and starting conditions (Boreal Passage is the default).
- **Batch**: A group of simulations run with varying strategies/seeds for comparison.
- **Replay Log**: JSON event log of a simulation, consumed by the graphics team for visualization.

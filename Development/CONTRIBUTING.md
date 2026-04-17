# Contributing Guide — Code Style, Workflow, and How-Tos

## Golden Rules

1. **Read the docs before coding.** `CLAUDE.md` is your entry point. Then read the relevant `Development/*.md` file for your task.
2. **Domain core has zero external dependencies.** If you're importing `fastapi`, `sqlalchemy`, or anything non-stdlib in `domain/`, you're doing it wrong.
3. **Dependencies point inward.** Infrastructure → Application → Domain. Never the reverse.
4. **Research before guessing.** If you need a number (aircraft speed, win probability), check `research/` or create a research file. Don't invent stats.
5. **Simulations are pure functions.** No side effects, no global state, no database calls inside `run_simulation()`.

## Python Code Style

### General

- **Python 3.12+** — use modern syntax (type unions with `|`, `match` statements where appropriate).
- **Type hints everywhere.** All function signatures, all class attributes. Use `from __future__ import annotations` at top of every file.
- **Dataclasses for domain entities.** Use `@dataclass` for entities and `@dataclass(frozen=True)` for value objects.
- **ABC for ports.** All ports are abstract base classes with `@abstractmethod` decorators.
- **No classes where functions suffice.** Domain services can be plain functions. Don't wrap a single function in a class.
- **Enum for finite sets.** Aircraft types, decision types, simulation status — use `str, Enum` for JSON serialization.

### Naming

| What | Convention | Example |
|---|---|---|
| Files | `snake_case.py` | `combat_resolver.py` |
| Classes | `PascalCase` | `CombatResolver`, `DroneSwarm` |
| Functions | `snake_case` | `resolve_engagement()` |
| Constants | `UPPER_SNAKE` | `MAX_DETECTION_RANGE_KM` |
| Type aliases | `PascalCase` | `AircraftId = str` |
| Private | Leading `_` | `_calculate_fuel_burn()` |

### Imports

```python
# 1. stdlib
from __future__ import annotations
import math
from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum

# 2. domain (relative within domain)
from .entities.aircraft import Aircraft
from .value_objects.position import Position

# 3. application (if in infrastructure)
from src.application.run_simulation import RunSimulationUseCase

# 4. external libraries (infrastructure only)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
```

Domain files NEVER have section 3 or 4.

### Error Handling

- **Domain exceptions** in `backend/src/domain/exceptions.py`: `SimulationError`, `InvalidDecisionError`, `FuelExhaustedError`.
- **Domain raises, infrastructure catches.** Domain code raises domain exceptions. API routes catch them and return HTTP error responses.
- **No bare `except`.** Always catch specific exceptions.
- **Let it crash for bugs.** Don't catch-and-swallow programmer errors. Only handle expected failure modes.

### Testing

```
backend/tests/
├── domain/                # Unit tests — no external deps, no mocks
│   ├── test_combat_resolver.py
│   ├── test_movement.py
│   ├── test_fuel_manager.py
│   └── test_aircraft.py
├── application/           # Integration tests — mock ports
│   ├── test_run_simulation.py
│   └── test_run_batch.py
└── infrastructure/        # End-to-end tests — real DB, real API
    ├── test_api_simulations.py
    └── test_sqlite_repo.py
```

- **Domain tests are pure.** No mocks, no fixtures, no database. Just instantiate domain objects and assert behavior.
- **Application tests mock the ports.** Use `unittest.mock` or simple stub implementations.
- **Infrastructure tests use real dependencies.** In-memory SQLite, TestClient for FastAPI.
- **Use pytest.** Run with `pytest backend/tests/`.
- **Test file naming:** `test_[module_name].py`.
- **Test function naming:** `test_[what]_[condition]_[expected]`, e.g., `test_combat_resolver_drone_vs_uav_returns_result`.

## TypeScript/Frontend Code Style

### General

- **TypeScript strict mode.** No `any` unless unavoidable (document why).
- **Functional components.** React function components with hooks.
- **Named exports.** No default exports.
- **Interface over type** for object shapes. `type` for unions and intersections.

### Naming

| What | Convention | Example |
|---|---|---|
| Files (components) | `PascalCase.tsx` | `MapVisualization.tsx` |
| Files (utilities) | `camelCase.ts` | `apiClient.ts` |
| Components | `PascalCase` | `SimulationControl` |
| Functions | `camelCase` | `fetchSimulationResults()` |
| Constants | `UPPER_SNAKE` | `API_BASE_URL` |
| Interfaces | `PascalCase` | `SimulationMetrics` |

### State Management

- **React state + context** for UI state.
- **SWR or React Query** for server state (API data fetching).
- **No Redux** — overkill for this project.

### API Communication

- **REST calls** via a typed API client in `frontend/src/lib/api.ts`.
- **WebSocket** via a hook in `frontend/src/lib/useWebSocket.ts`.
- **All API types** mirror the Pydantic schemas from the backend.

## Git Workflow

### Branch Naming

```
feature/[short-description]     # New features
fix/[short-description]         # Bug fixes
research/[topic]                # Research additions
refactor/[short-description]    # Refactoring
```

Examples: `feature/batch-simulation-api`, `fix/fuel-burn-calculation`, `research/combat-probabilities`

### Commit Messages

```
[type]: [short description]

[Optional longer description]
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `research`

Examples:
```
feat: add batch simulation endpoint with parallel execution
fix: correct fuel burn rate calculation for bombers
docs: add combat matchup probability research
test: add domain tests for combat resolver
research: document UAV performance characteristics
```

### Pull Request Checklist

Before merging, verify:

- [ ] Code follows the hexagonal architecture (no inward dependency violations)
- [ ] Domain code has zero external imports
- [ ] New aircraft types documented in `Development/DOMAIN.md`
- [ ] New API endpoints documented in `Development/API.md`
- [ ] New stats sourced in `research/` with confidence levels
- [ ] Tests pass: `pytest backend/tests/`
- [ ] Type check passes: `mypy backend/src/`
- [ ] Frontend builds: `npm run build` in `frontend/`

## How-To Guides

### How to Add a New Aircraft Type

1. Open `backend/src/domain/entities/aircraft.py`.
2. Add new value to `AircraftType` enum.
3. Create a new dataclass or factory function with all stats.
4. Add combat matchup entries (this type vs all others, and all others vs this type).
5. Update `Development/DOMAIN.md`:
   - Add row to "Aircraft Types — Default Stats" table.
   - Add row AND column to "Combat Matchup Probabilities" table.
6. If stats needed research, create/update file in `research/`.
7. Update `scenario/boreal_passage.json` if the new type should appear in the default scenario.
8. Write domain tests in `backend/tests/domain/test_aircraft.py`.

### How to Add a New Strategy

1. Create `scenario/strategies/my_strategy.py`.
2. Import and implement `StrategyPort` from `backend/src/domain/ports/strategy.py`.
3. Implement the `decide(state: SimulationState) -> list[Decision]` method.
4. Register in the strategy registry (dict in `backend/src/infrastructure/simulation/strategy_registry.py`).
5. Test with a single simulation: `POST /api/v1/simulations` with your strategy ID.
6. Compare against existing strategies using batch run.

### How to Add a New API Endpoint

1. Determine if a new use case is needed in `backend/src/application/`.
2. Create Pydantic request/response schemas in `backend/src/infrastructure/api/schemas/`.
3. Add the route function in the appropriate `backend/src/infrastructure/api/routes/` file.
4. Wire dependency injection in `backend/src/infrastructure/api/dependencies.py`.
5. Document in `Development/API.md`.
6. Add an infrastructure-level test.

### How to Add a New Metric

1. Add the field to `SimulationMetrics` in `backend/src/domain/value_objects/metrics.py`.
2. Update the `MetricsCollector` service in `backend/src/domain/services/metrics.py` to compute it.
3. Update the replay log serialization if it should appear in replay JSON.
4. Update `Development/DOMAIN.md` metrics table.
5. Update the API response schemas.
6. Add frontend display if needed.

### How to Add a New Base or City to the Scenario

1. Add the location data to `scenario/boreal_passage.json`.
2. Include coordinates from `Boreal_passage_coordinates.csv` or define new ones.
3. Update `Development/DOMAIN.md` location tables.
4. No code changes needed — the simulation engine reads from the scenario config.

### How to Run the Project

```bash
# Start everything
docker compose up --build

# Backend only (development)
cd backend
pip install -e ".[dev]"
uvicorn src.infrastructure.api.main:app --reload --port 8000

# Frontend only (development)
cd frontend
npm install
npm run dev

# Run tests
cd backend
pytest tests/

# Type check
cd backend
mypy src/
```

### How to Export a Replay for the Graphics Team

```bash
# Via API
curl http://localhost:8000/api/v1/simulations/{sim_id}/replay > replay.json

# The replay.json file can be given directly to the graphics team.
# See SIMULATION.md for the replay format specification.
```

## Docker Development

### docker-compose.yml Services

| Service | Port | Description |
|---|---|---|
| `backend` | 8000 | FastAPI + simulation engine |
| `frontend` | 3000 | Next.js dev server |

### Volumes

- `./data:/app/data` — SQLite database persistence
- `./backend/src:/app/src` — Backend hot reload
- `./frontend/src:/app/src` — Frontend hot reload
- `./scenario:/app/scenario` — Scenario configs
- `./research:/app/research` — Research files (read-only in container)

### Environment

Copy `.env.example` to `.env` and adjust as needed. The Docker Compose file reads from `.env`.

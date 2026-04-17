# API Specification

## Overview

The backend exposes a REST API via FastAPI with WebSocket support for real-time simulation updates. All endpoints are prefixed with `/api/v1`.

Base URL: `http://localhost:8000/api/v1`
WebSocket: `ws://localhost:8000/ws`
OpenAPI Docs: `http://localhost:8000/docs`

## REST Endpoints

### Scenarios

#### `GET /scenarios`

List all available scenarios.

**Response 200:**
```json
{
  "scenarios": [
    {
      "id": "boreal_passage_v1",
      "name": "The Boreal Passage — Standard",
      "theater_width_km": 1667,
      "theater_height_km": 1300,
      "tick_minutes": 5,
      "max_ticks": 1000,
      "north_bases": 3,
      "south_bases": 3,
      "total_aircraft": 54
    }
  ]
}
```

#### `GET /scenarios/{scenario_id}`

Get full scenario configuration including bases, cities, starting aircraft.

**Response 200:** Full `ScenarioConfig` JSON (see `SIMULATION.md` for schema).

#### `POST /scenarios`

Create a custom scenario.

**Request:**
```json
{
  "name": "Custom Scenario",
  "tick_minutes": 5,
  "max_ticks": 500,
  "bases": [...],
  "cities": [...],
  "starting_aircraft": {...}
}
```

**Response 201:**
```json
{
  "id": "custom_abc123",
  "name": "Custom Scenario"
}
```

---

### Strategies

#### `GET /strategies`

List all registered strategies.

**Response 200:**
```json
{
  "strategies": [
    {
      "id": "defensive_v1",
      "name": "defensive_v1",
      "description": "Protect capital and cities. Engage only approaching threats."
    },
    {
      "id": "aggressive_v1",
      "name": "aggressive_v1",
      "description": "Push forward, target enemy bases and bombers proactively."
    },
    {
      "id": "balanced_v1",
      "name": "balanced_v1",
      "description": "Mix of patrol zones and responsive intercepts."
    }
  ]
}
```

---

### Simulations

#### `POST /simulations`

Run a single simulation.

**Request:**
```json
{
  "scenario_id": "boreal_passage_v1",
  "strategy_id": "defensive_v1",
  "side": "north",
  "seed": 42,
  "enemy_strategy_id": "aggressive_v1"
}
```

**Response 202:**
```json
{
  "simulation_id": "sim-abc-123",
  "status": "running"
}
```

#### `POST /simulations/batch`

Run a batch of simulations. This is the primary endpoint for mass simulation.

**Request:**
```json
{
  "scenario_id": "boreal_passage_v1",
  "side": "north",
  "runs": [
    {
      "strategy_id": "defensive_v1",
      "enemy_strategy_id": "aggressive_v1",
      "seed_start": 1,
      "seed_count": 500
    },
    {
      "strategy_id": "balanced_v1",
      "enemy_strategy_id": "aggressive_v1",
      "seed_start": 1,
      "seed_count": 500
    }
  ]
}
```

This creates 1000 simulations: 500 defensive vs aggressive, 500 balanced vs aggressive, using seeds 1–500 for fair comparison.

**Response 202:**
```json
{
  "batch_id": "batch-xyz-789",
  "total_simulations": 1000,
  "status": "running"
}
```

#### `GET /simulations/{simulation_id}`

Get simulation status and result.

**Response 200:**
```json
{
  "simulation_id": "sim-abc-123",
  "batch_id": "batch-xyz-789",
  "scenario_id": "boreal_passage_v1",
  "strategy_id": "defensive_v1",
  "side": "north",
  "seed": 42,
  "status": "completed",
  "outcome": "WIN",
  "total_ticks": 480,
  "metrics": {
    "total_civilian_casualties": 1200,
    "time_to_first_casualty": 45,
    "aircraft_lost": 3,
    "aircraft_remaining": 9,
    "bases_lost": 0,
    "cities_defended": 3,
    "capital_survived": true,
    "engagement_win_rate": 0.72,
    "response_time_avg": 4.2,
    "sorties_flown": 34,
    "fuel_efficiency": 0.68,
    "total_engagements": 18
  }
}
```

#### `GET /simulations/{simulation_id}/replay`

Get the full replay log for graphics team consumption.

**Response 200:** Full replay JSON (see `SIMULATION.md` — Replay Log Format).

---

### Batches

#### `GET /batches/{batch_id}`

Get batch status and progress.

**Response 200:**
```json
{
  "batch_id": "batch-xyz-789",
  "status": "running",
  "total": 1000,
  "completed": 423,
  "failed": 0,
  "eta_seconds": 120
}
```

#### `GET /batches/{batch_id}/results`

Get aggregated results for a completed batch.

**Response 200:**
```json
{
  "batch_id": "batch-xyz-789",
  "status": "completed",
  "total": 1000,
  "summary": {
    "by_strategy": {
      "defensive_v1": {
        "simulations": 500,
        "wins": 312,
        "losses": 145,
        "timeouts": 43,
        "win_rate": 0.624,
        "avg_civilian_casualties": 2340,
        "avg_time_to_first_casualty": 38.2,
        "avg_aircraft_lost": 4.1,
        "avg_engagement_win_rate": 0.68,
        "capital_survival_rate": 0.89
      },
      "balanced_v1": {
        "simulations": 500,
        "wins": 389,
        "losses": 87,
        "timeouts": 24,
        "win_rate": 0.778,
        "avg_civilian_casualties": 1580,
        "avg_time_to_first_casualty": 52.7,
        "avg_aircraft_lost": 3.2,
        "avg_engagement_win_rate": 0.74,
        "capital_survival_rate": 0.95
      }
    },
    "best_strategy": "balanced_v1",
    "best_by_metric": {
      "lowest_casualties": "balanced_v1",
      "highest_win_rate": "balanced_v1",
      "highest_capital_survival": "balanced_v1",
      "fastest_response": "defensive_v1"
    }
  }
}
```

#### `GET /batches/{batch_id}/simulations`

List individual simulations in a batch with pagination.

**Query params:** `?offset=0&limit=50&strategy_id=defensive_v1&outcome=WIN&sort_by=total_civilian_casualties&sort_order=asc`

**Response 200:**
```json
{
  "batch_id": "batch-xyz-789",
  "total": 312,
  "offset": 0,
  "limit": 50,
  "simulations": [
    {
      "simulation_id": "sim-abc-001",
      "strategy_id": "defensive_v1",
      "seed": 1,
      "outcome": "WIN",
      "total_ticks": 342,
      "metrics": {...}
    }
  ]
}
```

---

### Results & Analysis

#### `GET /results/compare`

Compare two strategies side by side.

**Query params:** `?batch_id=batch-xyz-789&strategy_a=defensive_v1&strategy_b=balanced_v1`

**Response 200:**
```json
{
  "strategy_a": {
    "id": "defensive_v1",
    "win_rate": 0.624,
    "metrics_avg": {...}
  },
  "strategy_b": {
    "id": "balanced_v1",
    "win_rate": 0.778,
    "metrics_avg": {...}
  },
  "comparison": {
    "win_rate_delta": 0.154,
    "casualties_delta": -760,
    "statistically_significant": true,
    "recommended": "balanced_v1"
  }
}
```

#### `GET /results/patterns`

Identify winning patterns across simulations.

**Query params:** `?batch_id=batch-xyz-789&min_simulations=100`

**Response 200:**
```json
{
  "patterns": [
    {
      "description": "Early intercept of bombers within 3 ticks of detection",
      "frequency_in_wins": 0.89,
      "frequency_in_losses": 0.31,
      "impact": "high"
    },
    {
      "description": "Maintain at least 2 combat planes at forward base",
      "frequency_in_wins": 0.76,
      "frequency_in_losses": 0.42,
      "impact": "medium"
    }
  ]
}
```

---

## WebSocket API

### Connection

```
ws://localhost:8000/ws/batches/{batch_id}
```

### Messages (Server → Client)

#### Batch Progress

```json
{
  "type": "batch_progress",
  "batch_id": "batch-xyz-789",
  "completed": 423,
  "total": 1000,
  "eta_seconds": 120
}
```

#### Simulation Complete

```json
{
  "type": "simulation_complete",
  "simulation_id": "sim-abc-123",
  "outcome": "WIN",
  "ticks": 342,
  "strategy_id": "defensive_v1"
}
```

#### Batch Complete

```json
{
  "type": "batch_complete",
  "batch_id": "batch-xyz-789",
  "summary": {...}
}
```

### Live Simulation Streaming

For watching a single simulation in real-time:

```
ws://localhost:8000/ws/simulations/{simulation_id}/live
```

#### Tick Update

```json
{
  "type": "tick",
  "tick": 42,
  "aircraft": [...],
  "battles": [...],
  "events": ["n-cp-01 intercepted enemy UAV at (450, 380)"]
}
```

This is useful for the frontend map visualization during a single watched simulation.

---

## Error Responses

All errors follow a consistent format:

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Simulation sim-abc-123 not found"
  }
}
```

| HTTP Status | Code | When |
|---|---|---|
| 400 | `INVALID_REQUEST` | Malformed request body |
| 404 | `NOT_FOUND` | Resource doesn't exist |
| 409 | `ALREADY_RUNNING` | Batch already in progress |
| 422 | `VALIDATION_ERROR` | Invalid scenario config |
| 500 | `INTERNAL_ERROR` | Unexpected server error |

---

## Pydantic Models

All request/response schemas are defined as Pydantic models in `backend/src/infrastructure/api/schemas/`. These are **infrastructure-layer objects** — they serialize/deserialize between JSON and domain entities. Domain entities themselves are plain dataclasses.

```
backend/src/infrastructure/api/schemas/
├── __init__.py
├── simulation.py      # SimulationRequest, SimulationResponse, BatchRequest, etc.
├── scenario.py        # ScenarioResponse, CreateScenarioRequest
├── results.py         # MetricsResponse, CompareResponse, PatternResponse
└── common.py          # ErrorResponse, PaginationParams
```

## Adding a New Endpoint

1. Define the use case in `backend/src/application/` if it doesn't exist.
2. Create Pydantic request/response models in `infrastructure/api/schemas/`.
3. Add the route in `infrastructure/api/routes/`.
4. Wire up dependency injection in `infrastructure/api/dependencies.py`.
5. Document the endpoint in this file.
6. Test via FastAPI auto-docs at `/docs`.

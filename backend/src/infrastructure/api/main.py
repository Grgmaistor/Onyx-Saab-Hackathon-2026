from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.persistence.database import init_db
from src.infrastructure.api.routes import simulations, scenarios, batches, results, strategies, attack_plans, training


def create_app() -> FastAPI:
    app = FastAPI(title="Boreal Passage Simulation Engine", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(simulations.router, prefix="/api/v1")
    app.include_router(scenarios.router, prefix="/api/v1")
    app.include_router(batches.router, prefix="/api/v1")
    app.include_router(results.router, prefix="/api/v1")
    app.include_router(strategies.router, prefix="/api/v1")
    app.include_router(attack_plans.router, prefix="/api/v1")
    app.include_router(training.router, prefix="/api/v1")

    @app.on_event("startup")
    def startup():
        init_db()

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()

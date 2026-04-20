from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.api.dependencies import get_active_settings_or_bootstrap
from src.infrastructure.api.routes import (
    attack_plans,
    defense_playbooks,
    evaluation,
    knowledge,
    settings as settings_routes,
    training,
)
from src.infrastructure.persistence.database import init_db


def create_app() -> FastAPI:
    app = FastAPI(
        title="Boreal Passage Simulation Engine",
        version="2.0.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(settings_routes.router, prefix="/api/v1")
    app.include_router(attack_plans.router, prefix="/api/v1")
    app.include_router(defense_playbooks.router, prefix="/api/v1")
    app.include_router(evaluation.router, prefix="/api/v1")
    app.include_router(training.router, prefix="/api/v1")
    app.include_router(knowledge.router, prefix="/api/v1")

    @app.on_event("startup")
    def startup():
        init_db()
        # Bootstrap: ensure there's at least one Settings row, active.
        try:
            get_active_settings_or_bootstrap()
        except Exception as e:
            print(f"Bootstrap warning: {e}")

    @app.get("/health")
    def health():
        return {"status": "ok", "version": "2.0.0"}

    return app


app = create_app()

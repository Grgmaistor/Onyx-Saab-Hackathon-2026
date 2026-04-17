from __future__ import annotations

from fastapi import APIRouter
from src.infrastructure.api.dependencies import get_registry

router = APIRouter(prefix="/strategies", tags=["strategies"])


@router.get("")
def list_strategies():
    reg = get_registry()
    return {"strategies": [
        {"id": s.name, "name": s.name, "description": s.description}
        for s in reg.list_all()]}

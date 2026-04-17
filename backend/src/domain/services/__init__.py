from __future__ import annotations

from .combat_resolver import resolve_engagements
from .movement import execute_movements
from .fuel_manager import service_aircraft
from .detection import detect_threats
from .damage import apply_city_damage
from .metrics import compute_metrics
from .simulation_engine import run_simulation

__all__ = [
    "resolve_engagements",
    "execute_movements",
    "service_aircraft",
    "detect_threats",
    "apply_city_damage",
    "compute_metrics",
    "run_simulation",
]

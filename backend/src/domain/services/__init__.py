from __future__ import annotations

from .attack_plan_executor import execute_attack_plan
from .detection import detect_threats
from .engagement_engine import resolve_engagements
from .fitness import compute_fitness
from .movement import advance_aircraft
from .pattern_extractor import extract_pattern
from .pilot_reflexes import ReflexAction, ReflexKind, evaluate_reflexes, evaluate_reflexes_bulk
from .playbook_executor import Command, ExecutorState, execute_playbook
from .service_manager import kill_parked_aircraft, service_aircraft
from .simulation_engine import run_simulation
from .strike_resolver import resolve_strikes

__all__ = [
    "execute_attack_plan",
    "detect_threats",
    "resolve_engagements",
    "compute_fitness",
    "advance_aircraft",
    "extract_pattern",
    "ReflexAction",
    "ReflexKind",
    "evaluate_reflexes",
    "evaluate_reflexes_bulk",
    "Command",
    "ExecutorState",
    "execute_playbook",
    "kill_parked_aircraft",
    "service_aircraft",
    "run_simulation",
    "resolve_strikes",
]

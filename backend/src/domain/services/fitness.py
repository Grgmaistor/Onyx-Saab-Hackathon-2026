"""
Fitness scoring for a match result. Used both for ranking defenses in the
knowledge base and for training evaluation.

Weighted multi-objective with hard constraint:
- Capital destroyed = -1000 (fitness floor)
- Primary: minimize civilian casualties
- Secondary: preserve aircraft, defend cities, deter enemy sorties
- Tertiary: air denial score, fuel efficiency
"""

from __future__ import annotations

from ..value_objects.match_result import SimulationOutcome
from ..value_objects.metrics import SimulationMetrics


# Profile weights (see research/strategy_optimization.md)
PROFILES: dict[str, dict[str, float]] = {
    "balanced": {
        "outcome": 1.0,
        "casualties": 2.0,
        "aircraft": 1.0,
        "engagement": 1.0,
        "cities": 1.5,
        "deterrence": 1.5,
        "fuel": 0.5,
        "response": 0.8,
    },
    "humanitarian": {
        "outcome": 0.5,
        "casualties": 5.0,
        "aircraft": 0.5,
        "engagement": 0.5,
        "cities": 3.0,
        "deterrence": 2.5,
        "fuel": 0.3,
        "response": 1.5,
    },
    "attrition": {
        "outcome": 1.0,
        "casualties": 1.0,
        "aircraft": 2.5,
        "engagement": 1.5,
        "cities": 1.0,
        "deterrence": 1.0,
        "fuel": 1.5,
        "response": 0.5,
    },
}


def compute_fitness(
    metrics: SimulationMetrics,
    outcome: SimulationOutcome,
    profile_name: str = "balanced",
) -> float:
    """Higher is better. Returns -1000 if capital destroyed."""
    if not metrics.capital_survived:
        return -1000.0

    weights = PROFILES.get(profile_name, PROFILES["balanced"])

    outcome_map = {
        SimulationOutcome.WIN: 100.0,
        SimulationOutcome.TIMEOUT: 20.0,
        SimulationOutcome.LOSS: -100.0,
        SimulationOutcome.UNDECIDED: 0.0,
    }
    outcome_score = outcome_map.get(outcome, 0.0)

    casualty_score = -min(metrics.total_civilian_casualties / 1000.0, 100.0)

    ac_total = max(1, metrics.aircraft_remaining + metrics.aircraft_lost)
    aircraft_score = (metrics.aircraft_remaining / ac_total) * 50.0

    engagement_score = metrics.engagement_win_rate * 50.0
    cities_score = metrics.cities_defended * 15.0
    deterrence_score = (
        metrics.enemy_sorties_deterred * 2.0
        + metrics.enemy_weapons_jettisoned * 3.0
        + metrics.enemy_mission_kills * 1.5
        + metrics.air_denial_score * 50.0
    )
    fuel_score = metrics.fuel_efficiency * 20.0
    response_score = max(0.0, 30.0 - metrics.response_time_avg)

    return (
        outcome_score * weights["outcome"]
        + casualty_score * weights["casualties"]
        + aircraft_score * weights["aircraft"]
        + engagement_score * weights["engagement"]
        + cities_score * weights["cities"]
        + deterrence_score * weights["deterrence"]
        + fuel_score * weights["fuel"]
        + response_score * weights["response"]
    )

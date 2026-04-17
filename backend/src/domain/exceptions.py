from __future__ import annotations


class SimulationError(Exception):
    """Base exception for simulation domain errors."""


class InvalidDecisionError(SimulationError):
    """Raised when a strategy issues an invalid decision."""


class FuelExhaustedError(SimulationError):
    """Raised when an aircraft runs out of fuel mid-flight."""


class BaseCapacityError(SimulationError):
    """Raised when a base cannot accept more aircraft."""


class SimulationTerminated(SimulationError):
    """Raised when a termination condition is met."""

    def __init__(self, reason: str, outcome: str) -> None:
        self.reason = reason
        self.outcome = outcome
        super().__init__(reason)

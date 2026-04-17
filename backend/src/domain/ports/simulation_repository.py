from __future__ import annotations

from abc import ABC, abstractmethod

from ..entities.simulation import SimulationResult


class SimulationRepository(ABC):

    @abstractmethod
    def save(self, result: SimulationResult) -> str: ...

    @abstractmethod
    def get(self, simulation_id: str) -> SimulationResult | None: ...

    @abstractmethod
    def list_by_batch(self, batch_id: str) -> list[SimulationResult]: ...

    @abstractmethod
    def delete(self, simulation_id: str) -> bool: ...

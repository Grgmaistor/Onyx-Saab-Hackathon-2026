from __future__ import annotations

from abc import ABC, abstractmethod

from ..entities.simulation import SimulationResult, SimulationTick


class EventPublisher(ABC):

    @abstractmethod
    def publish_tick(self, simulation_id: str, tick: SimulationTick) -> None: ...

    @abstractmethod
    def publish_complete(self, simulation_id: str, result: SimulationResult) -> None: ...

    @abstractmethod
    def publish_batch_progress(self, batch_id: str, completed: int, total: int) -> None: ...

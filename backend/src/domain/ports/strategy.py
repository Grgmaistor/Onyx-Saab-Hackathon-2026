from __future__ import annotations

from abc import ABC, abstractmethod

from ..entities.simulation import SimulationState
from ..value_objects.decision import Decision


class StrategyPort(ABC):

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def description(self) -> str: ...

    @abstractmethod
    def decide(self, state: SimulationState) -> list[Decision]: ...

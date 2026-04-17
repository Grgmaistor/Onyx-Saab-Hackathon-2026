from __future__ import annotations

from abc import ABC, abstractmethod

from ..entities.simulation import SimulationConfig, SimulationTick
from ..value_objects.metrics import SimulationMetrics


class ExportPort(ABC):

    @abstractmethod
    def export_replay(
        self,
        simulation_id: str,
        config: SimulationConfig,
        outcome: str,
        ticks: list[SimulationTick],
        metrics: SimulationMetrics | None,
    ) -> dict: ...

from __future__ import annotations

from src.domain.entities.simulation import SimulationResult
from src.domain.ports.simulation_repository import SimulationRepository


class GetResultsUseCase:
    def __init__(self, repo: SimulationRepository) -> None:
        self._repo = repo

    def get(self, simulation_id: str) -> SimulationResult | None:
        return self._repo.get(simulation_id)

    def list_by_batch(self, batch_id: str) -> list[SimulationResult]:
        return self._repo.list_by_batch(batch_id)

from __future__ import annotations

from src.domain.ports.simulation_repository import SimulationRepository
from src.domain.ports.export import ExportPort


class ExportReplayUseCase:
    def __init__(self, repo: SimulationRepository, exporter: ExportPort) -> None:
        self._repo = repo
        self._exporter = exporter

    def execute(self, simulation_id: str) -> dict | None:
        result = self._repo.get(simulation_id)
        if not result:
            return None
        return self._exporter.export_replay(
            result.simulation_id, result.config, result.outcome.value,
            result.event_log, result.metrics)

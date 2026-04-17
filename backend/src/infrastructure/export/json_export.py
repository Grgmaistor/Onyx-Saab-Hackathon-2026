from __future__ import annotations

from src.domain.entities.simulation import SimulationConfig, SimulationTick
from src.domain.ports.export import ExportPort
from src.domain.value_objects.metrics import SimulationMetrics


class JSONExportAdapter(ExportPort):
    def export_replay(self, simulation_id: str, config: SimulationConfig,
                      outcome: str, ticks: list[SimulationTick],
                      metrics: SimulationMetrics | None) -> dict:
        return {
            "simulation_id": simulation_id,
            "scenario": config.scenario_id,
            "strategy": config.strategy_id,
            "enemy_strategy": config.enemy_strategy_id,
            "seed": config.seed,
            "side": config.side.value,
            "outcome": outcome,
            "total_ticks": len(ticks) - 1,
            "tick_minutes": config.tick_minutes,
            "ticks": [{"tick": t.tick, "aircraft": t.aircraft_states,
                       "bases": t.base_states, "cities": t.city_states,
                       "battles": t.battles, "decisions": t.decisions_made,
                       "events": t.events} for t in ticks],
            "metrics": metrics.to_dict() if metrics else None,
        }

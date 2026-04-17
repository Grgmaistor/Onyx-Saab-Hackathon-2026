from __future__ import annotations

import json
from src.domain.entities.aircraft import Side
from src.domain.entities.simulation import (
    SimulationConfig, SimulationOutcome, SimulationResult, SimulationTick,
)
from src.domain.ports.simulation_repository import SimulationRepository
from src.domain.value_objects.metrics import SimulationMetrics
from .database import get_session
from .models import SimulationResultModel


class SQLiteSimulationRepo(SimulationRepository):

    def save(self, result: SimulationResult) -> str:
        session = get_session()
        try:
            log_data = [{"tick": t.tick, "aircraft_states": t.aircraft_states,
                         "base_states": t.base_states, "city_states": t.city_states,
                         "battles": t.battles, "decisions_made": t.decisions_made,
                         "events": t.events} for t in result.event_log]
            m_data = result.metrics.to_dict() if result.metrics else None
            existing = session.query(SimulationResultModel).get(result.simulation_id)
            if existing:
                session.delete(existing)
                session.flush()
            session.add(SimulationResultModel(
                simulation_id=result.simulation_id, batch_id=result.batch_id,
                scenario_id=result.config.scenario_id, strategy_id=result.config.strategy_id,
                enemy_strategy_id=result.config.enemy_strategy_id, side=result.config.side.value,
                seed=result.config.seed, outcome=result.outcome.value,
                total_ticks=result.total_ticks, event_log_json=json.dumps(log_data),
                metrics_json=json.dumps(m_data) if m_data else None))
            session.commit()
            return result.simulation_id
        finally:
            session.close()

    def get(self, simulation_id: str) -> SimulationResult | None:
        session = get_session()
        try:
            m = session.query(SimulationResultModel).get(simulation_id)
            return self._to_domain(m) if m else None
        finally:
            session.close()

    def list_by_batch(self, batch_id: str) -> list[SimulationResult]:
        session = get_session()
        try:
            return [self._to_domain(m) for m in
                    session.query(SimulationResultModel).filter_by(batch_id=batch_id).all()]
        finally:
            session.close()

    def delete(self, simulation_id: str) -> bool:
        session = get_session()
        try:
            m = session.query(SimulationResultModel).get(simulation_id)
            if not m:
                return False
            session.delete(m)
            session.commit()
            return True
        finally:
            session.close()

    @staticmethod
    def _to_domain(m: SimulationResultModel) -> SimulationResult:
        log = [SimulationTick(tick=t["tick"], aircraft_states=t["aircraft_states"],
                              base_states=t["base_states"], city_states=t["city_states"],
                              battles=t["battles"], decisions_made=t["decisions_made"],
                              events=t["events"]) for t in json.loads(m.event_log_json)]
        metrics = SimulationMetrics(**json.loads(m.metrics_json)) if m.metrics_json else None
        cfg = SimulationConfig(scenario_id=m.scenario_id, strategy_id=m.strategy_id,
                               enemy_strategy_id=m.enemy_strategy_id, side=Side(m.side), seed=m.seed)
        return SimulationResult(simulation_id=m.simulation_id, batch_id=m.batch_id,
                                config=cfg, outcome=SimulationOutcome(m.outcome),
                                total_ticks=m.total_ticks, event_log=log, metrics=metrics)

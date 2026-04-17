from __future__ import annotations

from sqlalchemy import Column, String, Integer, Text
from .database import DBBase


class SimulationResultModel(DBBase):
    __tablename__ = "simulation_results"

    simulation_id = Column(String, primary_key=True)
    batch_id = Column(String, nullable=True, index=True)
    scenario_id = Column(String, nullable=False)
    strategy_id = Column(String, nullable=False)
    enemy_strategy_id = Column(String, nullable=False)
    side = Column(String, nullable=False)
    seed = Column(Integer, nullable=False)
    outcome = Column(String, nullable=False)
    total_ticks = Column(Integer, nullable=False)
    event_log_json = Column(Text, nullable=False)
    metrics_json = Column(Text, nullable=True)

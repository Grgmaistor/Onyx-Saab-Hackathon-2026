from __future__ import annotations

from dataclasses import dataclass

from .aircraft import Side
from ..value_objects.position import Position


@dataclass
class City:
    id: str
    name: str
    side: Side
    position: Position
    population: int
    is_capital: bool
    defense_value: float
    damage_taken: float = 0.0
    casualties: int = 0

    @property
    def is_destroyed(self) -> bool:
        return self.damage_taken >= 1.0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "side": self.side.value,
            "position": [self.position.x_km, self.position.y_km],
            "population": self.population,
            "is_capital": self.is_capital,
            "damage": round(self.damage_taken, 4),
            "casualties": self.casualties,
        }

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    x_km: float
    y_km: float

    def distance_to(self, other: Position) -> float:
        return math.sqrt((self.x_km - other.x_km) ** 2 + (self.y_km - other.y_km) ** 2)

    def travel_time_minutes(self, other: Position, speed_kmh: float) -> float:
        if speed_kmh <= 0:
            return float("inf")
        return (self.distance_to(other) / speed_kmh) * 60

    def move_toward(self, target: Position, distance_km: float) -> Position:
        total = self.distance_to(target)
        if total <= distance_km:
            return target
        ratio = distance_km / total
        return Position(
            x_km=self.x_km + (target.x_km - self.x_km) * ratio,
            y_km=self.y_km + (target.y_km - self.y_km) * ratio,
        )

    def to_dict(self) -> dict:
        return {"x_km": self.x_km, "y_km": self.y_km}

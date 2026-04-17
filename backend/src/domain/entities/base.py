from __future__ import annotations

from dataclasses import dataclass, field

from .aircraft import Side
from ..value_objects.position import Position


@dataclass
class Base:
    id: str
    name: str
    side: Side
    position: Position
    max_aircraft_capacity: int
    fuel_storage: float
    fuel_storage_max: float
    fuel_resupply_rate: float
    is_operational: bool = True
    current_aircraft: list[str] = field(default_factory=list)

    @property
    def available_capacity(self) -> int:
        return self.max_aircraft_capacity - len(self.current_aircraft)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "side": self.side.value,
            "position": [self.position.x_km, self.position.y_km],
            "operational": self.is_operational,
            "fuel_storage": round(self.fuel_storage, 1),
            "aircraft_count": len(self.current_aircraft),
            "capacity": self.max_aircraft_capacity,
        }

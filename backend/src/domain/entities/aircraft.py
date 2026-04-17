from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ..value_objects.position import Position


class Side(str, Enum):
    NORTH = "north"
    SOUTH = "south"


class AircraftType(str, Enum):
    DRONE_SWARM = "drone_swarm"
    UAV = "uav"
    COMBAT_PLANE = "combat_plane"
    BOMBER = "bomber"


class AircraftState(str, Enum):
    GROUNDED = "grounded"
    AIRBORNE = "airborne"
    REFUELING = "refueling"
    REARMING = "rearming"
    MAINTENANCE = "maintenance"
    ENGAGED = "engaged"
    DESTROYED = "destroyed"


AIRCRAFT_SPECS: dict[AircraftType, dict] = {
    AircraftType.DRONE_SWARM: {
        "speed_kmh": 150,
        "fuel_capacity": 100,
        "fuel_burn_rate": 0.8,
        "refuel_time_minutes": 30,
        "ammo_capacity": 20,
        "rearm_time_minutes": 20,
        "maintenance_time_minutes": 15,
        "combat_matchups": {
            "drone_swarm": 0.50, "uav": 0.55,
            "combat_plane": 0.20, "bomber": 0.65,
        },
    },
    AircraftType.UAV: {
        "speed_kmh": 250,
        "fuel_capacity": 300,
        "fuel_burn_rate": 0.5,
        "refuel_time_minutes": 45,
        "ammo_capacity": 4,
        "rearm_time_minutes": 30,
        "maintenance_time_minutes": 30,
        "combat_matchups": {
            "drone_swarm": 0.45, "uav": 0.50,
            "combat_plane": 0.25, "bomber": 0.60,
        },
    },
    AircraftType.COMBAT_PLANE: {
        "speed_kmh": 900,
        "fuel_capacity": 800,
        "fuel_burn_rate": 1.2,
        "refuel_time_minutes": 60,
        "ammo_capacity": 6,
        "rearm_time_minutes": 40,
        "maintenance_time_minutes": 45,
        "combat_matchups": {
            "drone_swarm": 0.80, "uav": 0.75,
            "combat_plane": 0.50, "bomber": 0.70,
        },
    },
    AircraftType.BOMBER: {
        "speed_kmh": 600,
        "fuel_capacity": 1200,
        "fuel_burn_rate": 2.0,
        "refuel_time_minutes": 90,
        "ammo_capacity": 12,
        "rearm_time_minutes": 60,
        "maintenance_time_minutes": 60,
        "combat_matchups": {
            "drone_swarm": 0.35, "uav": 0.40,
            "combat_plane": 0.30, "bomber": 0.50,
        },
    },
}


@dataclass
class Aircraft:
    id: str
    type: AircraftType
    side: Side
    position: Position
    state: AircraftState
    fuel_current: float
    fuel_capacity: float
    fuel_burn_rate: float
    speed_kmh: float
    ammo_current: int
    ammo_capacity: int
    refuel_time_minutes: float
    rearm_time_minutes: float
    maintenance_time_minutes: float
    combat_matchups: dict[str, float]
    assigned_base: str
    service_ticks_remaining: int = 0
    target_position: Position | None = None
    target_id: str | None = None

    @property
    def is_available(self) -> bool:
        return self.state in (AircraftState.GROUNDED, AircraftState.AIRBORNE)

    @property
    def is_alive(self) -> bool:
        return self.state != AircraftState.DESTROYED

    @property
    def fuel_fraction(self) -> float:
        if self.fuel_capacity <= 0:
            return 0.0
        return self.fuel_current / self.fuel_capacity

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "side": self.side.value,
            "position": [self.position.x_km, self.position.y_km],
            "state": self.state.value,
            "fuel": round(self.fuel_fraction, 2),
            "ammo": self.ammo_current,
        }


def create_aircraft(
    aircraft_id: str,
    aircraft_type: AircraftType,
    side: Side,
    position: Position,
    assigned_base: str,
) -> Aircraft:
    specs = AIRCRAFT_SPECS[aircraft_type]
    return Aircraft(
        id=aircraft_id,
        type=aircraft_type,
        side=side,
        position=position,
        state=AircraftState.GROUNDED,
        fuel_current=specs["fuel_capacity"],
        fuel_capacity=specs["fuel_capacity"],
        fuel_burn_rate=specs["fuel_burn_rate"],
        speed_kmh=specs["speed_kmh"],
        ammo_current=specs["ammo_capacity"],
        ammo_capacity=specs["ammo_capacity"],
        refuel_time_minutes=specs["refuel_time_minutes"],
        rearm_time_minutes=specs["rearm_time_minutes"],
        maintenance_time_minutes=specs["maintenance_time_minutes"],
        combat_matchups=dict(specs["combat_matchups"]),
        assigned_base=assigned_base,
    )

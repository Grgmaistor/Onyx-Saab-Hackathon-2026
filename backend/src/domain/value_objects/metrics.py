from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SimulationMetrics:
    """
    Full KPI set per simulation. Expanded from v1 to include deterrence,
    mission-kill, and damage-without-destruction outcomes per the realistic
    engagement model.
    """
    # Humanitarian
    total_civilian_casualties: int
    time_to_first_casualty: int | None
    cities_defended: int              # cities with no or light damage
    capital_survived: bool

    # Air force attrition (friendly)
    aircraft_lost: int                # hard kills
    aircraft_remaining: int
    aircraft_damaged_in_repair: int   # flyable but grounded for repair
    bases_lost: int                   # destroyed
    bases_remaining: int
    parked_aircraft_destroyed: int    # on-ground destruction at bases

    # Engagement performance
    total_engagements: int
    engagements_won: int
    engagement_win_rate: float
    missiles_fired: int
    missiles_hit: int

    # Deterrence / air denial
    enemy_sorties_deterred: int       # bomber/uav/drone aborted before strike
    enemy_weapons_jettisoned: int     # bombers that dropped payload to evade
    enemy_mission_kills: int          # damaged but not destroyed, forced abort
    air_denial_score: float           # fraction of enemy strike sorties that failed to deliver

    # Logistics
    sorties_flown: int
    fuel_efficiency: float
    response_time_avg: float          # avg ticks from threat detection to intercept

    # Meta
    total_ticks: int

    def to_dict(self) -> dict:
        return {
            "total_civilian_casualties": self.total_civilian_casualties,
            "time_to_first_casualty": self.time_to_first_casualty,
            "cities_defended": self.cities_defended,
            "capital_survived": self.capital_survived,
            "aircraft_lost": self.aircraft_lost,
            "aircraft_remaining": self.aircraft_remaining,
            "aircraft_damaged_in_repair": self.aircraft_damaged_in_repair,
            "bases_lost": self.bases_lost,
            "bases_remaining": self.bases_remaining,
            "parked_aircraft_destroyed": self.parked_aircraft_destroyed,
            "total_engagements": self.total_engagements,
            "engagements_won": self.engagements_won,
            "engagement_win_rate": round(self.engagement_win_rate, 4),
            "missiles_fired": self.missiles_fired,
            "missiles_hit": self.missiles_hit,
            "enemy_sorties_deterred": self.enemy_sorties_deterred,
            "enemy_weapons_jettisoned": self.enemy_weapons_jettisoned,
            "enemy_mission_kills": self.enemy_mission_kills,
            "air_denial_score": round(self.air_denial_score, 4),
            "sorties_flown": self.sorties_flown,
            "fuel_efficiency": round(self.fuel_efficiency, 4),
            "response_time_avg": round(self.response_time_avg, 2),
            "total_ticks": self.total_ticks,
        }

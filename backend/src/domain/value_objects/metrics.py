from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SimulationMetrics:
    total_civilian_casualties: int
    time_to_first_casualty: int | None
    aircraft_lost: int
    aircraft_remaining: int
    bases_lost: int
    bases_remaining: int
    cities_defended: int
    capital_survived: bool
    total_ticks: int
    fuel_efficiency: float
    engagement_win_rate: float
    response_time_avg: float
    total_engagements: int
    sorties_flown: int

    def to_dict(self) -> dict:
        return {
            "total_civilian_casualties": self.total_civilian_casualties,
            "time_to_first_casualty": self.time_to_first_casualty,
            "aircraft_lost": self.aircraft_lost,
            "aircraft_remaining": self.aircraft_remaining,
            "bases_lost": self.bases_lost,
            "bases_remaining": self.bases_remaining,
            "cities_defended": self.cities_defended,
            "capital_survived": self.capital_survived,
            "total_ticks": self.total_ticks,
            "fuel_efficiency": round(self.fuel_efficiency, 4),
            "engagement_win_rate": round(self.engagement_win_rate, 4),
            "response_time_avg": round(self.response_time_avg, 2),
            "total_engagements": self.total_engagements,
            "sorties_flown": self.sorties_flown,
        }

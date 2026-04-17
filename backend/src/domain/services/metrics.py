from __future__ import annotations

from ..entities.aircraft import AircraftState, Side
from ..entities.simulation import SimulationConfig, SimulationTick
from ..value_objects.metrics import SimulationMetrics


def compute_metrics(
    event_log: list[SimulationTick],
    all_aircraft_final: list[dict],
    all_cities_final: list[dict],
    all_bases_final: list[dict],
    friendly_side: str,
) -> SimulationMetrics:
    total_casualties = 0
    time_to_first = None
    aircraft_lost = 0
    aircraft_remaining = 0
    bases_lost = 0
    bases_remaining = 0
    cities_defended = 0
    capital_survived = True
    total_engagements = 0
    engagements_won = 0
    sorties_flown = 0
    total_fuel_used = 0.0
    total_fuel_capacity = 0.0
    response_times: list[int] = []

    # Count from final state dicts
    for ac in all_aircraft_final:
        if ac.get("side") != friendly_side:
            continue
        total_fuel_capacity += 1.0
        total_fuel_used += (1.0 - ac.get("fuel", 0.0))
        if ac.get("state") == AircraftState.DESTROYED.value:
            aircraft_lost += 1
        else:
            aircraft_remaining += 1

    for city in all_cities_final:
        if city.get("side") != friendly_side:
            continue
        total_casualties += city.get("casualties", 0)
        if city.get("damage", 0) < 0.5:
            cities_defended += 1
        if city.get("is_capital") and city.get("damage", 0) >= 1.0:
            capital_survived = False

    for base in all_bases_final:
        if base.get("side") != friendly_side:
            continue
        if not base.get("operational", True):
            bases_lost += 1
        else:
            bases_remaining += 1

    # Scan event log
    for tick_data in event_log:
        for event in tick_data.events:
            if "defeated" in event:
                total_engagements += 1
                # Check if friendly won (friendly id appears first before "defeated")
                parts = event.split(" defeated ")
                if len(parts) == 2:
                    winner_part = parts[0]
                    if f"-{friendly_side[0]}-" in winner_part or winner_part.startswith(f"{friendly_side[0]}-"):
                        engagements_won += 1

            if "launched" in event or "scrambled" in event:
                sorties_flown += 1

            if "casualties" in event and time_to_first is None:
                # Check if it's our side's city
                for city in all_cities_final:
                    if city.get("side") == friendly_side and city.get("name", "") in event:
                        time_to_first = tick_data.tick
                        break

    fuel_efficiency = 0.0
    if total_fuel_capacity > 0:
        fuel_efficiency = total_fuel_used / total_fuel_capacity

    win_rate = 0.0
    if total_engagements > 0:
        win_rate = engagements_won / total_engagements

    avg_response = 0.0
    if response_times:
        avg_response = sum(response_times) / len(response_times)

    return SimulationMetrics(
        total_civilian_casualties=total_casualties,
        time_to_first_casualty=time_to_first,
        aircraft_lost=aircraft_lost,
        aircraft_remaining=aircraft_remaining,
        bases_lost=bases_lost,
        bases_remaining=bases_remaining,
        cities_defended=cities_defended,
        capital_survived=capital_survived,
        total_ticks=len(event_log),
        fuel_efficiency=fuel_efficiency,
        engagement_win_rate=win_rate,
        response_time_avg=avg_response,
        total_engagements=total_engagements,
        sorties_flown=sorties_flown,
    )

from __future__ import annotations

import random
import uuid

from ..entities.aircraft import Aircraft, AircraftState
from ..entities.battle import Battle
from ..value_objects.combat_result import CombatResult


def resolve_engagements(
    friendly_aircraft: list[Aircraft],
    enemy_aircraft: list[Aircraft],
    engagement_range_km: float,
    rng: random.Random,
    current_tick: int,
) -> tuple[list[Battle], list[str]]:
    battles: list[Battle] = []
    events: list[str] = []
    engaged_ids: set[str] = set()

    airborne_friendly = [
        a for a in friendly_aircraft
        if a.state == AircraftState.AIRBORNE and a.is_alive and a.ammo_current > 0
    ]
    airborne_enemy = [
        a for a in enemy_aircraft
        if a.state == AircraftState.AIRBORNE and a.is_alive
    ]

    for attacker in airborne_friendly:
        if attacker.id in engaged_ids:
            continue

        for defender in airborne_enemy:
            if defender.id in engaged_ids:
                continue

            dist = attacker.position.distance_to(defender.position)
            if dist > engagement_range_km:
                continue

            # Resolve combat
            battle_id = str(uuid.uuid4())[:8]
            win_prob = attacker.combat_matchups.get(
                defender.type.value, 0.5
            )
            attacker_won = rng.random() < win_prob

            if attacker_won:
                defender.state = AircraftState.DESTROYED
                attacker.ammo_current -= 1
                events.append(
                    f"{attacker.id} ({attacker.type.value}) defeated "
                    f"{defender.id} ({defender.type.value}) at "
                    f"({attacker.position.x_km:.0f}, {attacker.position.y_km:.0f})"
                )
            else:
                attacker.state = AircraftState.DESTROYED
                if defender.ammo_current > 0:
                    defender.ammo_current -= 1
                events.append(
                    f"{defender.id} ({defender.type.value}) defeated "
                    f"{attacker.id} ({attacker.type.value}) at "
                    f"({defender.position.x_km:.0f}, {defender.position.y_km:.0f})"
                )

            result = CombatResult(
                battle_id=battle_id,
                attacker_id=attacker.id,
                defender_id=defender.id,
                attacker_won=attacker_won,
                attacker_destroyed=not attacker_won,
                defender_destroyed=attacker_won,
            )

            battle = Battle(
                id=battle_id,
                tick=current_tick,
                position=attacker.position,
                attacker_ids=[attacker.id],
                defender_ids=[defender.id],
                results=[result],
            )
            battles.append(battle)
            engaged_ids.add(attacker.id)
            engaged_ids.add(defender.id)
            break  # attacker used, move to next

    return battles, events

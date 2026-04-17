from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CombatResult:
    battle_id: str
    attacker_id: str
    defender_id: str
    attacker_won: bool
    attacker_destroyed: bool
    defender_destroyed: bool
    collateral_damage: float = 0.0

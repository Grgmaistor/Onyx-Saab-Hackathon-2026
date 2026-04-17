from __future__ import annotations

from dataclasses import dataclass, field

from ..value_objects.combat_result import CombatResult
from ..value_objects.position import Position


@dataclass
class Battle:
    id: str
    tick: int
    position: Position
    attacker_ids: list[str] = field(default_factory=list)
    defender_ids: list[str] = field(default_factory=list)
    results: list[CombatResult] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tick": self.tick,
            "position": [self.position.x_km, self.position.y_km],
            "attackers": self.attacker_ids,
            "defenders": self.defender_ids,
            "results": [
                {
                    "attacker_id": r.attacker_id,
                    "defender_id": r.defender_id,
                    "attacker_won": r.attacker_won,
                }
                for r in self.results
            ],
        }

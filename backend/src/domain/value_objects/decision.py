from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .position import Position


class DecisionType(str, Enum):
    LAUNCH = "launch"
    INTERCEPT = "intercept"
    PATROL = "patrol"
    RTB = "rtb"
    HOLD = "hold"
    RELOCATE = "relocate"


@dataclass(frozen=True)
class Decision:
    type: DecisionType
    aircraft_id: str
    target_id: str | None = None
    position: Position | None = None

from __future__ import annotations

from src.domain.ports.strategy import StrategyPort


class StrategyRegistry:
    def __init__(self) -> None:
        self._strategies: dict[str, StrategyPort] = {}

    def register(self, strategy: StrategyPort) -> None:
        self._strategies[strategy.name] = strategy

    def get(self, name: str) -> StrategyPort | None:
        return self._strategies.get(name)

    def list_all(self) -> list[StrategyPort]:
        return list(self._strategies.values())

    def as_dict(self) -> dict[str, StrategyPort]:
        return dict(self._strategies)

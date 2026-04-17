from __future__ import annotations

import json
from pathlib import Path


def load_scenarios(scenario_dir: str = "scenario") -> dict[str, dict]:
    scenarios: dict[str, dict] = {}
    base = Path(scenario_dir)
    if not base.exists():
        return scenarios
    for f in base.glob("*.json"):
        data = json.loads(f.read_text(encoding="utf-8"))
        scenarios[data.get("id", f.stem)] = data
    return scenarios

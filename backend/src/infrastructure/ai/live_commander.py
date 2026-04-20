"""
Live Commander — LLM-in-the-loop decision maker during Evaluation mode.

Uses rolling conversation with prompt caching and periodic compaction.
See Development/Architecture/LIVE_COMMANDER.md.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from src.domain.entities.simulation import SimulationState
from src.domain.ports.llm_agent import LLMAgentPort, LLMMessage
from src.domain.services.playbook_executor import Command
from src.domain.value_objects.defense_playbook import DefensePlaybook
from src.domain.value_objects.position import Position
from src.domain.value_objects.settings import Settings

from .prompts import LIVE_COMMANDER_SYSTEM


COMPACTION_EVERY_TICKS = 25


@dataclass
class LiveCommanderState:
    """Mutable state carried across a live evaluation session."""
    settings: Settings
    playbook: DefensePlaybook
    conversation: list[LLMMessage] = field(default_factory=list)
    tick_count: int = 0
    last_tick_state: dict | None = None   # for delta computation
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cached_tokens: int = 0
    total_cost_usd: float = 0.0
    commands_issued: list[dict] = field(default_factory=list)


class LiveCommander:
    def __init__(self, agent: LLMAgentPort) -> None:
        self._agent = agent

    def initialize(
        self, settings: Settings, playbook: DefensePlaybook,
    ) -> LiveCommanderState:
        """Begin a new evaluation session. Returns live state."""
        state = LiveCommanderState(settings=settings, playbook=playbook)

        # Initial context (cached) lives in system prompt only
        return state

    async def decide(
        self,
        state: LiveCommanderState,
        sim_state: SimulationState,
    ) -> tuple[list[Command], dict]:
        """
        Call the LLM with the current state delta. Parse the response.
        Return (commands_to_apply, raw_response_dict).
        """
        state.tick_count += 1

        # Compute delta vs last tick
        current_snapshot = _snapshot(sim_state)
        delta = _compute_delta(state.last_tick_state, current_snapshot)
        state.last_tick_state = current_snapshot

        # Periodic compaction
        if state.tick_count > 0 and state.tick_count % COMPACTION_EVERY_TICKS == 0:
            await self._compact(state)

        # Add current tick message
        user_content = json.dumps({
            "tick": sim_state.tick,
            "delta": delta,
            "detected_threats_count": len(sim_state.detected_threats),
            "friendly_airborne_count": sum(
                1 for a in sim_state.friendly_aircraft if a.is_airborne
            ),
        })
        state.conversation.append(LLMMessage(role="user", content=user_content))

        # Build system with settings/playbook/doctrine context (cacheable)
        system = _build_system_prompt(state.settings, state.playbook)

        try:
            parsed, resp = await self._agent.call_json(
                system_prompt=system,
                messages=state.conversation,
                max_tokens=400,
                temperature=0.5,
                use_cache=True,
            )
        except Exception:
            # Fallback to "continue" on LLM failures
            parsed = {"action": "continue"}
            resp_content = json.dumps(parsed)
            state.conversation.append(
                LLMMessage(role="assistant", content=resp_content)
            )
            return [], parsed

        # Track token usage
        state.total_input_tokens += resp.input_tokens
        state.total_output_tokens += resp.output_tokens
        state.total_cached_tokens += resp.cached_tokens
        state.total_cost_usd += resp.cost_usd

        state.conversation.append(LLMMessage(role="assistant", content=resp.content))

        # Translate action
        commands = self._translate_action(parsed, sim_state)
        if parsed.get("action") != "continue":
            state.commands_issued.append({"tick": sim_state.tick, "response": parsed})
        return commands, parsed

    async def _compact(self, state: LiveCommanderState) -> None:
        """Summarize conversation history into a single memo message."""
        if len(state.conversation) < 4:
            return

        compaction_request = LLMMessage(
            role="user",
            content=(
                "Summarize the evaluation so far in ~200 tokens: key decisions you made, "
                "enemy intent as you understand it, current tactical state, and any running "
                "concerns. Respond with plain text, not JSON."
            ),
        )
        messages = list(state.conversation) + [compaction_request]
        system = _build_system_prompt(state.settings, state.playbook)

        try:
            resp = await self._agent.call(
                system_prompt=system,
                messages=messages,
                max_tokens=400,
                temperature=0.4,
                use_cache=False,
            )
            state.total_input_tokens += resp.input_tokens
            state.total_output_tokens += resp.output_tokens
            state.total_cost_usd += resp.cost_usd

            # Replace conversation with memo
            memo = LLMMessage(
                role="user",
                content=f"[Session memory so far]\n{resp.content}",
                cacheable=True,
            )
            state.conversation = [memo]
        except Exception:
            # If compaction fails, keep the last 10 messages and drop the rest
            state.conversation = state.conversation[-10:]

    def _translate_action(
        self, parsed: dict, sim_state: SimulationState,
    ) -> list[Command]:
        """Convert LLM JSON response into Command objects the sim can apply."""
        action = parsed.get("action", "continue")
        if action == "continue":
            return []
        if action == "command":
            return self._parse_commands(parsed.get("commands", []), sim_state)
        if action == "update_playbook":
            # TODO: apply playbook patch live (future)
            return []
        if action == "escalate":
            return []
        return []

    def _parse_commands(
        self, commands_data: list[dict], sim_state: SimulationState,
    ) -> list[Command]:
        commands: list[Command] = []
        for cmd in commands_data:
            ctype = cmd.get("type", "")
            if ctype in ("scramble", "launch", "intercept"):
                count = cmd.get("count", 1)
                aircraft_type = cmd.get("aircraft_type", "combat_plane")
                from_base = cmd.get("from_base")
                intercept_target = cmd.get("intercept_target")

                ready = [
                    a for a in sim_state.friendly_aircraft
                    if a.state.value == "grounded"
                    and a.type.value == aircraft_type
                    and (from_base is None or a.assigned_base == from_base)
                ]
                target_pos = None
                target_id = None
                if intercept_target:
                    for t in sim_state.detected_threats:
                        if t.id == intercept_target:
                            target_pos = t.position
                            target_id = t.id
                            break

                for ac in ready[:count]:
                    commands.append(Command(
                        type="launch",
                        aircraft_id=ac.id,
                        target_id=target_id,
                        position=target_pos,
                        from_base=ac.assigned_base,
                    ))
        return commands


def _build_system_prompt(settings: Settings, playbook: DefensePlaybook) -> str:
    return f"""{LIVE_COMMANDER_SYSTEM}

== SETTINGS ==
{settings.name}
Defender resources: {json.dumps(settings.defender_resources)}
Attacker resources: {json.dumps(settings.attacker_resources)}

== CURRENT PLAYBOOK ==
{playbook.name}: {playbook.description}
{playbook.doctrine_notes}

Standing orders count: {len(playbook.standing_orders)}
Triggers count: {len(playbook.triggers)}
"""


# =======================================================================
# Delta computation
# =======================================================================

def _snapshot(sim_state: SimulationState) -> dict:
    return {
        "friendly_aircraft_states": {
            a.id: {"state": a.state.value, "fuel": round(a.fuel_fraction, 2),
                   "ammo": a.ammo_current, "pos": [round(a.position.x_km), round(a.position.y_km)]}
            for a in sim_state.friendly_aircraft
        },
        "enemy_aircraft_states": {
            a.id: {"state": a.state.value, "pos": [round(a.position.x_km), round(a.position.y_km)]}
            for a in sim_state.enemy_aircraft if a.is_airborne
        },
        "locations_health": {
            loc.id: {
                "destroyed": loc.is_destroyed,
                "launch_disabled": loc.is_launch_disabled,
                "casualties": loc.casualties,
            }
            for loc in sim_state.friendly_locations
        },
    }


def _compute_delta(prev: dict | None, curr: dict) -> dict:
    if prev is None:
        return {"initial_state": curr}

    delta: dict = {
        "friendly_changes": [],
        "enemy_new": [],
        "enemy_gone": [],
        "asset_changes": [],
    }

    prev_fa = prev.get("friendly_aircraft_states", {})
    curr_fa = curr.get("friendly_aircraft_states", {})
    for aid, cur in curr_fa.items():
        prev_state = prev_fa.get(aid, {})
        if prev_state.get("state") != cur["state"]:
            delta["friendly_changes"].append({"id": aid, "new_state": cur["state"]})

    prev_ea = set(prev.get("enemy_aircraft_states", {}).keys())
    curr_ea = set(curr.get("enemy_aircraft_states", {}).keys())
    for aid in curr_ea - prev_ea:
        delta["enemy_new"].append({
            "id": aid,
            "pos": curr["enemy_aircraft_states"][aid]["pos"],
        })
    for aid in prev_ea - curr_ea:
        delta["enemy_gone"].append(aid)

    prev_loc = prev.get("locations_health", {})
    curr_loc = curr.get("locations_health", {})
    for lid, cur in curr_loc.items():
        p = prev_loc.get(lid, {})
        if (
            p.get("destroyed") != cur["destroyed"]
            or p.get("launch_disabled") != cur["launch_disabled"]
            or cur["casualties"] > p.get("casualties", 0)
        ):
            delta["asset_changes"].append({"id": lid, **cur})

    return delta

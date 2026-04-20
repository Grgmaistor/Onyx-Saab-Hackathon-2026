"""
Claude agent implementing LLMAgentPort. Handles:
- Prompt caching via anthropic-beta header
- JSON parse + repair retry
- Cost tracking
"""

from __future__ import annotations

import json
import os
import re

import httpx

from src.domain.ports.llm_agent import LLMAgentPort, LLMMessage, LLMResponse


ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-sonnet-4-6"


class ClaudeAgent(LLMAgentPort):
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: float = 120.0,
    ) -> None:
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self._model = model or os.environ.get("ANTHROPIC_MODEL", DEFAULT_MODEL)
        self._timeout = timeout_seconds

    async def call(
        self,
        system_prompt: str,
        messages: list[LLMMessage],
        max_tokens: int = 4096,
        temperature: float = 1.0,
        use_cache: bool = True,
        stream: bool = False,
    ) -> LLMResponse:
        if not self._api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")

        payload = self._build_payload(
            system_prompt, messages, max_tokens, temperature, use_cache,
        )

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                ANTHROPIC_API_URL,
                headers=self._headers(use_cache),
                json=payload,
            )
            if response.status_code >= 400:
                raise ValueError(f"Anthropic API {response.status_code}: {response.text}")
            data = response.json()

        return self._parse_response(data)

    async def call_json(
        self,
        system_prompt: str,
        messages: list[LLMMessage],
        max_tokens: int = 4096,
        temperature: float = 1.0,
        use_cache: bool = True,
    ) -> tuple[dict, LLMResponse]:
        """Call, parse as JSON, retry once on failure with a repair prompt."""
        resp = await self.call(system_prompt, messages, max_tokens, temperature, use_cache)
        parsed = _try_extract_json(resp.content)
        if parsed is not None:
            return parsed, resp

        # Retry with repair instruction
        repair_messages = list(messages) + [
            LLMMessage(role="assistant", content=resp.content),
            LLMMessage(
                role="user",
                content=(
                    "Your last response was not valid JSON. "
                    "Respond again with ONLY the valid JSON object, no prose, no markdown fences."
                ),
            ),
        ]
        resp2 = await self.call(system_prompt, repair_messages, max_tokens, temperature, use_cache)
        parsed2 = _try_extract_json(resp2.content)
        if parsed2 is None:
            raise ValueError(f"LLM did not return valid JSON after retry: {resp2.content[:500]}")
        return parsed2, resp2

    # ==== Helpers ====

    def _headers(self, use_cache: bool) -> dict:
        h = {
            "x-api-key": self._api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        if use_cache:
            h["anthropic-beta"] = "prompt-caching-2024-07-31"
        return h

    def _build_payload(
        self,
        system_prompt: str,
        messages: list[LLMMessage],
        max_tokens: int,
        temperature: float,
        use_cache: bool,
    ) -> dict:
        # System prompt as cacheable block if caching enabled
        if use_cache and system_prompt:
            system_blocks = [
                {"type": "text", "text": system_prompt,
                 "cache_control": {"type": "ephemeral"}},
            ]
        else:
            system_blocks = system_prompt

        # Messages — support cache breakpoints on user/assistant messages
        built_messages = []
        for m in messages:
            if use_cache and m.cacheable:
                built_messages.append({
                    "role": m.role,
                    "content": [
                        {"type": "text", "text": m.content,
                         "cache_control": {"type": "ephemeral"}},
                    ],
                })
            else:
                built_messages.append({"role": m.role, "content": m.content})

        return {
            "model": self._model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system_blocks,
            "messages": built_messages,
        }

    def _parse_response(self, data: dict) -> LLMResponse:
        content = ""
        for block in data.get("content", []):
            if block.get("type") == "text":
                content += block.get("text", "")
        usage = data.get("usage", {})
        return LLMResponse(
            content=content.strip(),
            input_tokens=usage.get("input_tokens", 0),
            output_tokens=usage.get("output_tokens", 0),
            cached_tokens=usage.get("cache_read_input_tokens", 0),
            stop_reason=data.get("stop_reason", ""),
            raw=data,
        )


def _try_extract_json(text: str) -> dict | None:
    """Parse JSON from a response; tolerate markdown fences and prose wrappers."""
    if not text:
        return None
    text = text.strip()

    # Strip markdown fences
    if text.startswith("```"):
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            text = match.group(1).strip()

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find the first {...} block
    brace_match = re.search(r"\{.*\}", text, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            pass
    return None

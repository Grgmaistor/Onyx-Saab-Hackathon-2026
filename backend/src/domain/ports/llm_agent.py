from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class LLMResponse:
    """Generic envelope for LLM responses."""
    content: str                      # raw text
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    stop_reason: str = ""
    raw: dict = field(default_factory=dict)

    @property
    def cost_usd(self) -> float:
        """Rough Sonnet 4.6 pricing: $3/M input, $15/M output, cached 10% of input."""
        fresh_in = max(0, self.input_tokens - self.cached_tokens)
        return (
            fresh_in * 3.0 / 1_000_000
            + self.cached_tokens * 0.30 / 1_000_000
            + self.output_tokens * 15.0 / 1_000_000
        )


@dataclass
class LLMMessage:
    """A message in a conversation."""
    role: str                         # "user" | "assistant"
    content: str
    cacheable: bool = False           # mark for prompt cache breakpoint


class LLMAgentPort(ABC):
    """
    Abstract interface for LLM calls. Single port, implemented by ClaudeAgent
    or stub agent for testing.
    """

    @abstractmethod
    async def call(
        self,
        system_prompt: str,
        messages: list[LLMMessage],
        max_tokens: int = 4096,
        temperature: float = 1.0,
        use_cache: bool = True,
        stream: bool = False,
    ) -> LLMResponse:
        """Synchronous call with conversation history."""
        ...

    @abstractmethod
    async def call_json(
        self,
        system_prompt: str,
        messages: list[LLMMessage],
        max_tokens: int = 4096,
        temperature: float = 1.0,
        use_cache: bool = True,
    ) -> tuple[dict, LLMResponse]:
        """Call and parse JSON response. Retries once on parse failure."""
        ...

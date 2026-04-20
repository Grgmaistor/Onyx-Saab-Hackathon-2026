"""Dependency injection wiring for FastAPI."""

from __future__ import annotations

from functools import lru_cache

from src.application.training_orchestrator import TrainingOrchestrator
from src.application.use_cases import (
    AttackPlanUseCase,
    DefensePlaybookUseCase,
    RunMatchUseCase,
    SettingsUseCase,
)
from src.infrastructure.ai.claude_agent import ClaudeAgent
from src.infrastructure.ai.generators import (
    AttackPlanGenerator,
    DefensePlaybookGenerator,
    DoctrineSynthesizer,
    MatchAnalyzer,
)
from src.infrastructure.ai.live_commander import LiveCommander
from src.infrastructure.persistence.database import init_db
from src.infrastructure.persistence.repos import SqlKnowledgeBase


@lru_cache
def get_kb() -> SqlKnowledgeBase:
    init_db()
    return SqlKnowledgeBase()


@lru_cache
def get_llm_agent() -> ClaudeAgent:
    return ClaudeAgent()


@lru_cache
def get_attack_generator() -> AttackPlanGenerator:
    return AttackPlanGenerator(get_llm_agent())


@lru_cache
def get_playbook_generator() -> DefensePlaybookGenerator:
    return DefensePlaybookGenerator(get_llm_agent())


@lru_cache
def get_match_analyzer() -> MatchAnalyzer:
    return MatchAnalyzer(get_llm_agent())


@lru_cache
def get_doctrine_synthesizer() -> DoctrineSynthesizer:
    return DoctrineSynthesizer(get_llm_agent())


@lru_cache
def get_live_commander() -> LiveCommander:
    return LiveCommander(get_llm_agent())


@lru_cache
def get_settings_uc() -> SettingsUseCase:
    return SettingsUseCase(get_kb())


@lru_cache
def get_attack_uc() -> AttackPlanUseCase:
    return AttackPlanUseCase(get_kb(), get_attack_generator())


@lru_cache
def get_playbook_uc() -> DefensePlaybookUseCase:
    return DefensePlaybookUseCase(get_kb(), get_playbook_generator())


@lru_cache
def get_match_uc() -> RunMatchUseCase:
    return RunMatchUseCase(get_kb(), get_match_analyzer())


@lru_cache
def get_training_orchestrator() -> TrainingOrchestrator:
    return TrainingOrchestrator(
        kb=get_kb(),
        playbook_generator=get_playbook_generator(),
        match_analyzer=get_match_analyzer(),
        doctrine_synthesizer=get_doctrine_synthesizer(),
    )


def get_active_settings_or_bootstrap():
    """Return active Settings, creating one from default scenario if none exists."""
    kb = get_kb()
    active = kb.settings.get_active()
    if active:
        return active
    # Bootstrap with default scenario
    uc = get_settings_uc()
    settings = uc.create_from_scenario_json(
        name="Boreal Passage — Standard",
        scenario_path="scenario/boreal_passage.json",
    )
    uc.set_active(settings.settings_id)
    return settings

"""Offline tests for switchable LLM provider (Gemini default / Anthropic fallback)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from config.settings import Settings, get_settings
from scorer.engine import (
    AnthropicClient,
    GeminiClient,
    _system_blocks_to_text,
    build_llm_client,
)


@dataclass
class _FakeCandidate:
    finish_reason: str = "STOP"


@dataclass
class _FakeGenerateResponse:
    text: str
    candidates: list[_FakeCandidate] = field(default_factory=list)


@dataclass
class _FakeAsyncModels:
    calls: list[dict[str, Any]] = field(default_factory=list)
    response_text: str = '{"s":90,"t":1,"r":["fit"]}'
    # Models that should raise a transient 503, to exercise the fallback chain.
    fail_models: set[str] = field(default_factory=set)
    # Return an empty MAX_TOKENS response once, to exercise budget escalation.
    truncate_first: bool = False

    async def generate_content(
        self,
        *,
        model: str,
        contents: str,
        config: Any,
    ) -> _FakeGenerateResponse:
        self.calls.append(
            {
                "model": model,
                "contents": contents,
                "system_instruction": getattr(config, "system_instruction", None),
                "max_output_tokens": getattr(config, "max_output_tokens", None),
                "temperature": getattr(config, "temperature", None),
                "response_mime_type": getattr(config, "response_mime_type", None),
                "response_schema": getattr(config, "response_schema", None),
                "thinking_config": getattr(config, "thinking_config", None),
            }
        )
        if model in self.fail_models:
            raise RuntimeError("503 UNAVAILABLE: model is overloaded")
        if self.truncate_first:
            self.truncate_first = False
            return _FakeGenerateResponse(
                text="", candidates=[_FakeCandidate(finish_reason="MAX_TOKENS")]
            )
        return _FakeGenerateResponse(
            text=self.response_text, candidates=[_FakeCandidate()]
        )


@dataclass
class _FakeAio:
    models: _FakeAsyncModels = field(default_factory=_FakeAsyncModels)


@dataclass
class _FakeGenaiClient:
    aio: _FakeAio = field(default_factory=_FakeAio)


def test_active_models_gemini_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_SCORER_MODEL", "gemini-3.6-flash")
    monkeypatch.setenv("GEMINI_WRITER_MODEL", "gemini-3.6-flash")
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.llm_provider == "gemini"
    assert settings.active_scorer_model == "gemini-3.6-flash"
    assert settings.active_writer_model == "gemini-3.6-flash"
    get_settings.cache_clear()


def test_active_models_anthropic(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("SCORER_MODEL", "claude-haiku-test")
    monkeypatch.setenv("WRITER_MODEL", "claude-sonnet-test")
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.active_scorer_model == "claude-haiku-test"
    assert settings.active_writer_model == "claude-sonnet-test"
    get_settings.cache_clear()


def test_build_llm_client_gemini(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    get_settings.cache_clear()
    client = build_llm_client()
    assert isinstance(client, GeminiClient)
    get_settings.cache_clear()


def test_build_llm_client_anthropic(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    get_settings.cache_clear()
    client = build_llm_client()
    assert isinstance(client, AnthropicClient)
    get_settings.cache_clear()


def test_build_llm_client_unknown_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    get_settings.cache_clear()
    with pytest.raises(ValueError, match="Unknown LLM_PROVIDER"):
        build_llm_client()
    get_settings.cache_clear()


def test_gemini_client_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "")
    get_settings.cache_clear()
    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        GeminiClient()
    get_settings.cache_clear()


def test_system_blocks_to_text_joins_and_skips_empty() -> None:
    text = _system_blocks_to_text(
        [
            {"type": "text", "text": "Block A", "cache_control": {"type": "ephemeral"}},
            {"type": "text", "text": "  "},
            {"type": "text", "text": "Block B"},
        ]
    )
    assert text == "Block A\n\nBlock B"


@pytest.mark.asyncio
async def test_gemini_client_complete_maps_system_blocks() -> None:
    get_settings.cache_clear()
    fake = _FakeGenaiClient()
    client = GeminiClient(client=fake)
    blocks = [
        {"type": "text", "text": "CANDIDATE FACTS", "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": "RUBRIC"},
    ]
    result = await client.complete(
        model="gemini-3.6-flash",
        system_blocks=blocks,
        user="Evaluate this job",
        max_tokens=512,
        temperature=0.0,
        json_mode=True,
        json_schema={"type": "OBJECT"},
        thinking_level="low",
    )
    assert result == '{"s":90,"t":1,"r":["fit"]}'
    assert len(fake.aio.models.calls) == 1
    call = fake.aio.models.calls[0]
    assert call["model"] == "gemini-3.6-flash"
    assert call["contents"] == "Evaluate this job"
    assert call["system_instruction"] == "CANDIDATE FACTS\n\nRUBRIC"
    assert call["max_output_tokens"] == 512
    assert call["temperature"] == 0.0
    assert call["response_mime_type"] == "application/json"
    assert call["response_schema"] == {"type": "OBJECT"}
    assert call["thinking_config"] is not None
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_gemini_client_falls_back_when_model_unavailable() -> None:
    """A 503 on the primary model must roll over to the configured fallback."""
    get_settings.cache_clear()
    fake = _FakeGenaiClient()
    fake.aio.models.fail_models = {"gemini-primary"}
    client = GeminiClient(client=fake)
    result = await client.complete(
        model="gemini-primary",
        system_blocks=[{"type": "text", "text": "SYS"}],
        user="hi",
        max_tokens=64,
        temperature=0.0,
    )
    assert result == '{"s":90,"t":1,"r":["fit"]}'
    used = [c["model"] for c in fake.aio.models.calls]
    assert used[-1] != "gemini-primary"
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_gemini_client_escalates_on_truncated_output() -> None:
    """Thinking can eat the whole budget; retry must raise max_output_tokens."""
    get_settings.cache_clear()
    fake = _FakeGenaiClient()
    fake.aio.models.truncate_first = True
    client = GeminiClient(client=fake)
    result = await client.complete(
        model="gemini-3.6-flash",
        system_blocks=[{"type": "text", "text": "SYS"}],
        user="hi",
        max_tokens=256,
        temperature=0.0,
        json_mode=True,
        thinking_level="high",
    )
    assert result == '{"s":90,"t":1,"r":["fit"]}'
    budgets = [c["max_output_tokens"] for c in fake.aio.models.calls]
    assert len(budgets) == 2
    assert budgets[1] > budgets[0]
    get_settings.cache_clear()


def test_settings_defaults_provider_gemini() -> None:
    # Direct construction avoids .env side effects from a live project .env
    settings = Settings(
        _env_file=None,  # type: ignore[call-arg]
        llm_provider="gemini",
    )
    assert settings.llm_provider == "gemini"
    assert settings.gemini_scorer_model == "gemini-3.6-flash"
    assert settings.gemini_writer_model == "gemini-3.1-pro-preview"
    assert settings.active_scorer_model == "gemini-3.6-flash"
    assert settings.scorer_concurrency == 8
    assert settings.gemini_scorer_thinking_level == "low"
    assert settings.gemini_writer_thinking_level == "high"


def test_fallback_models_exclude_primary() -> None:
    settings = Settings(
        _env_file=None,  # type: ignore[call-arg]
        llm_provider="gemini",
        gemini_fallback_models=["gemini-a", "gemini-b", "gemini-a"],
    )
    assert settings.fallback_models_for("gemini-a") == ["gemini-b"]


def test_fallback_models_empty_for_anthropic() -> None:
    settings = Settings(
        _env_file=None,  # type: ignore[call-arg]
        llm_provider="anthropic",
    )
    assert settings.fallback_models_for("claude") == []

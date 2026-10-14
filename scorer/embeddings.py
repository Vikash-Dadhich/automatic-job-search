"""Profile and job-description embeddings for the scoring gate.

Cosine similarity is local. Gemini is called only for uncached text, and a
missing key or a failed call leaves the job for the LLM.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path
from typing import Any, Protocol

import structlog

from config.settings import PROJECT_ROOT, get_settings
from core.db import Job
from scorer.clients import (
    LLMBillingError,
    OpenAIRequestBlocked,
    _embedding_usage,
    get_openai_request_ledger,
    is_permanent_account_error,
    is_transient,
    remember_openai_attempt,
)

log = structlog.get_logger(__name__)

_MIN_EMBED_CHARS = 40
_EMBED_ATTEMPTS = 3


class EmbedInputLimitReached(Exception):
    """The embedding input cap allowed no further inputs for this chunk."""


class Embedder(Protocol):
    """Batch embedder. A short result means the input cap stopped the batch."""

    async def embed(self, texts: list[str]) -> list[list[float]]: ...


def cosine(a: list[float], b: list[float]) -> float:
    """Cosine similarity. Mismatched or empty vectors raise ``ValueError``."""
    if len(a) != len(b) or not a:
        raise ValueError("vectors must be the same non-zero length")
    dot = 0.0
    norm_a = 0.0
    norm_b = 0.0
    for left, right in zip(a, b, strict=True):
        dot += left * right
        norm_a += left * left
        norm_b += right * right
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    value = dot / (norm_a**0.5 * norm_b**0.5)
    return max(-1.0, min(1.0, value))


def clears_threshold(score: float) -> bool:
    """True when cosine is high enough to spend an LLM scoring call."""
    return score >= get_settings().vector_threshold


def job_embed_text(job: Job) -> str:
    """Title and company first, then a tail-truncated description."""
    limit = get_settings().vector_max_chars
    head = "\n".join(part.strip() for part in (job.title or "", job.company or "") if part.strip())
    body = (job.description_clean or "").strip()
    if not body:
        return head[:limit]
    if len(head) >= limit:
        return head[:limit]
    room = limit - len(head) - 1
    return f"{head}\n{body[:room]}"


def profile_embed_text(profile: Any) -> str:
    """Head of the cacheable candidate block. Same cap as a job description."""
    limit = get_settings().vector_max_chars
    return profile.static_context_block().strip()[:limit]


def profile_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def text_is_too_short(text: str) -> bool:
    return len(text.strip()) < _MIN_EMBED_CHARS


def _cache_path(digest: str) -> Path:
    return PROJECT_ROOT / "storage" / "embeddings" / f"profile-{digest}.json"


def load_profile_embedding(digest: str, *, model: str, dimensions: int) -> list[float] | None:
    """Return a cached profile vector when the model and width still match."""
    path = _cache_path(digest)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    if data.get("model") != model or data.get("dim") != dimensions:
        return None
    vector = data.get("vector")
    if not isinstance(vector, list) or len(vector) != dimensions:
        return None
    try:
        return [float(item) for item in vector]
    except (TypeError, ValueError):
        return None


def save_profile_embedding(
    digest: str,
    vector: list[float],
    *,
    model: str,
    dimensions: int,
) -> None:
    path = _cache_path(digest)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"model": model, "dim": dimensions, "vector": vector}
    path.write_text(json.dumps(payload), encoding="utf-8")


def jd_vector(job: Job, dimensions: int, *, model: str | None = None) -> list[float] | None:
    """Stored JD vector when width and embedding model both match."""
    if model is not None and job.embedding_model != model:
        return None
    raw = job.embedding
    if not isinstance(raw, list) or len(raw) != dimensions:
        return None
    try:
        return [float(item) for item in raw]
    except (TypeError, ValueError):
        return None


def stored_score(
    job: Job,
    digest: str,
    dimensions: int,
    *,
    model: str | None = None,
) -> float | None:
    """Cosine already computed for this profile text, width, and embedding model."""
    if jd_vector(job, dimensions, model=model) is None:
        return None
    if job.vector_profile_hash != digest or job.vector_score is None:
        return None
    return float(job.vector_score)


class OpenAIEmbedder:
    """OpenAI embeddings. Width is ``vector_dimensions``."""

    def __init__(self, api_key: str | None = None, *, client: Any | None = None) -> None:
        if client is not None:
            self._client = client
            return
        settings = get_settings()
        key = (api_key if api_key is not None else settings.openai_api_key) or ""
        if not key.strip():
            raise ValueError("OPENAI_API_KEY is empty. The vector gate fails open without it.")
        from openai import AsyncOpenAI

        self._client = AsyncOpenAI(api_key=key.strip())

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        settings = get_settings()
        width = settings.vector_batch_size
        vectors: list[list[float]] = []
        for start in range(0, len(texts), width):
            try:
                vectors.extend(await self._embed_chunk(texts[start : start + width]))
            except EmbedInputLimitReached:
                break
        return vectors

    async def _embed_chunk(self, texts: list[str]) -> list[list[float]]:
        settings = get_settings()
        ledger = get_openai_request_ledger()
        payload = texts
        last_exc: BaseException | None = None
        for attempt in range(_EMBED_ATTEMPTS):
            if attempt == 0:
                allowed = await ledger.reserve_embed_inputs(len(texts))
                if allowed <= 0:
                    raise EmbedInputLimitReached()
                payload = texts[:allowed]
            else:
                retry_allowed = await ledger.reserve_embed_inputs(len(payload))
                if retry_allowed < len(payload):
                    raise EmbedInputLimitReached() from last_exc
            try:
                await ledger.reserve()
                response = await self._client.embeddings.create(
                    model=settings.openai_embedding_model,
                    input=payload,
                    dimensions=settings.vector_dimensions,
                )
                present, reported_model, prompt = _embedding_usage(response)
                await remember_openai_attempt(
                    operation="embedding",
                    model=reported_model or settings.openai_embedding_model,
                    success=True,
                    transient_retry=attempt > 0,
                    usage_present=present,
                    prompt_tokens=prompt,
                )
                return _vectors_from_response(response, expected=len(payload))
            except (OpenAIRequestBlocked, EmbedInputLimitReached):
                raise
            except Exception as exc:
                last_exc = exc
                await remember_openai_attempt(
                    operation="embedding",
                    model=settings.openai_embedding_model,
                    success=False,
                    transient_retry=attempt > 0,
                    api_exception=True,
                )
                if is_permanent_account_error(exc):
                    await ledger.halt()
                    raise LLMBillingError(f"vector gate: account cannot embed ({exc})") from exc
                if attempt == _EMBED_ATTEMPTS - 1 or not is_transient(exc):
                    raise
                await asyncio.sleep(min(2.0 * (2**attempt), 8.0))
        raise RuntimeError("embedding failed") from last_exc


def _vectors_from_response(response: Any, *, expected: int) -> list[list[float]]:
    data = list(getattr(response, "data", None) or [])
    if len(data) != expected:
        raise ValueError(f"expected {expected} embeddings, got {len(data)}")
    ordered = sorted(data, key=lambda item: getattr(item, "index", 0))
    vectors: list[list[float]] = []
    for item in ordered:
        values = getattr(item, "embedding", None)
        if not isinstance(values, list):
            raise ValueError("embedding response missing values")
        vectors.append([float(value) for value in values])
    return vectors


def build_embedder() -> Embedder | None:
    """OpenAI embedder when the gate is on and a key is set. Otherwise ``None``."""
    settings = get_settings()
    if not settings.vector_gate_enabled:
        return None
    if not (settings.openai_api_key or "").strip():
        log.warning("vector_gate_no_api_key")
        return None
    return OpenAIEmbedder()

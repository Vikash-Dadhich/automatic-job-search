"""Typed application settings loaded from environment / .env."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root: .../job-agent (parent of config/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Central configuration for the job agent.

    Secrets and overrides come from environment variables or a `.env` file.
    Optional fields (Telegram, etc.) stay empty until later steps need them.
    """

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Scoring always uses OpenAI.
    llm_provider: str = Field(
        default="openai",
        description="Kept for old env files. Scoring always uses OpenAI.",
    )

    # Gemini (default provider)
    gemini_api_key: str = Field(default="", description="Google Gemini API key")
    gemini_scorer_model: str = Field(
        default="gemini-3.6-flash",
        description="Fast Gemini model for high-volume 0-100 scoring",
    )
    gemini_writer_model: str = Field(
        default="gemini-3.1-pro-preview",
        description="Deep-reasoning Gemini model for outreach / open-ended answers",
    )
    gemini_scorer_thinking_level: str = Field(
        default="low",
        description="Thinking level for scoring: minimal|low|medium|high ('' omits config)",
    )
    gemini_writer_thinking_level: str = Field(
        default="high",
        description="Thinking level for writing: minimal|low|medium|high ('' omits config)",
    )
    gemini_fallback_models: list[str] = Field(
        default_factory=lambda: ["gemini-3.8-flash", "gemini-3.6-flash"],
        description="Models tried in order when the primary is overloaded/unavailable",
    )
    score_budget: int | None = Field(
        default=None,
        description=(
            "Max jobs to send into the scorer per run. None = score all discovered. "
            "Applied AFTER deterministic prerank, so the highest-potential jobs "
            "are always scored and only the weakest tail is deferred to next run. "
            "When the vector gate is on, semantic rejects do not consume a slot."
        ),
    )
    vector_gate_enabled: bool = True
    vector_threshold: float = Field(default=0.50, ge=0, le=1)
    vector_dimensions: int = Field(default=768, ge=1)
    openai_embedding_model: str = "text-embedding-3-small"
    vector_batch_size: int = Field(default=16, ge=1, le=100)
    vector_max_chars: int = Field(default=6000, ge=40)
    scorer_concurrency: int = Field(
        default=8,
        ge=1,
        description="Max concurrent LLM scoring calls (paid-tier friendly)",
    )
    llm_max_attempts: int = Field(
        default=4,
        ge=1,
        description="Attempts per model for transient LLM errors (429/503/500)",
    )
    openai_max_requests: int | None = Field(
        default=None,
        ge=0,
        description=(
            "Max OpenAI HTTP attempts in this process, including retries and "
            "empty-response follow-ups. None does not cap attempts. A billing "
            "error still stops later attempts from starting."
        ),
    )
    search_capacity: int | None = Field(
        default=None,
        ge=0,
        description=(
            "Discovery queries one pipeline run plans. None plans every enabled "
            "query. 1 is one planned query, not one HTTP request or one posting. "
            "That query still runs on each configured JobSpy site and Workday tenant."
        ),
    )
    ingest_mode: Literal["daily", "catchup"] = Field(
        default="daily",
        description=(
            "daily reads roles posted in the last 36 hours. catchup reads everything "
            "open now (30 days on search sites, no age limit on company boards)."
        ),
    )
    simplify_discovery: bool = Field(
        default=False,
        description="Find extra company boards from the Simplify Summer 2027 product list",
    )
    enable_ats_boards: bool = Field(
        default=False,
        description="Read company boards on Greenhouse, Lever and Ashby during ingestion",
    )
    ats_max_age_hours: int | None = Field(
        default=None,
        ge=1,
        description="Skip board postings older than this. None keeps every open posting.",
    )
    ingest_posting_cap: int | None = Field(
        default=None,
        ge=0,
        description=(
            "Postings one ingestion run may commit. None does not cap. "
            "The count is successful upserts in this run, including filtered rows. "
            "A duplicate already committed in the run does not count again. "
            "A failed commit does not count. This does not limit how many rows "
            "external sites fetch."
        ),
    )
    role_classify_max_calls: int | None = Field(
        default=None,
        ge=0,
        description=(
            "Role-classification model attempts per process. None does not cap. "
            "Deterministic labels and stored labels do not count. "
            "Each model attempt also reserves an OpenAI request."
        ),
    )
    embed_max_inputs: int | None = Field(
        default=None,
        ge=0,
        description=(
            "Embedding inputs sent to the API per process, across batches and "
            "retries. None does not cap. Inputs past the cap are not sent and "
            "are not given a guessed vector."
        ),
    )
    llm_retry_max_wait_s: float = Field(
        default=30.0,
        ge=0,
        description="Cap on a single backoff sleep between LLM retries",
    )
    score_max_tokens: int = Field(
        default=1024,
        ge=128,
        description="max_output_tokens for scoring (includes Gemini thinking tokens)",
    )
    target_titles_only: bool = Field(
        default=False,
        description=(
            "Drop titles that are not product, consulting, strategy, marketing or "
            "business roles, and unpaid or non-summer internships, before scoring"
        ),
    )
    queue_mix: bool = Field(
        default=False,
        description="Fill the daily queue by the family split in config/queue_mix.yaml",
    )
    kit_answers: bool = Field(
        default=False,
        description="Draft two short answers for each queued job (sent only when on)",
    )
    queue_high_fit_score: int = Field(
        default=80,
        ge=0,
        le=100,
        description="Fit score at or above which a job is always queued, past the daily limit",
    )
    queue_daily_limit: int = Field(
        default=15,
        ge=1,
        description="Most jobs that may take an apply-queue seat in any rolling 24 hours",
    )
    queue_expiry_days: int = Field(
        default=7,
        ge=1,
        description="Days a queued job waits for Applied/Skip/Later before it expires",
    )
    queue_snooze_days: int = Field(
        default=3,
        ge=1,
        description="Days a job tapped Later stays out of the queue",
    )
    ingest_source_timeout_seconds: int = Field(
        default=900,
        ge=60,
        description="Longest one discovery source (JobSpy, Workday, boards) may run",
    )
    fit_max_attempts: int = Field(
        default=3,
        ge=1,
        description="Unusable fit answers allowed per job before it is marked error",
    )
    writer_max_tokens: int = Field(
        default=2048,
        ge=128,
        description="max_output_tokens for outreach / open-ended answers",
    )

    # Anthropic (optional fallback when llm_provider=anthropic)
    anthropic_api_key: str = Field(default="", description="Anthropic API key")
    scorer_model: str = Field(
        default="claude-haiku-4-5-20251001",
        description="Cheap Anthropic model for 0-100 scoring",
    )
    writer_model: str = Field(
        default="claude-sonnet-4-5-20250929",
        description="Stronger Anthropic model for outreach / open-ended answers",
    )

    # OpenAI is the only scoring and embedding provider.
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_scorer_model: str = Field(
        default="gpt-5-mini",
        description="Model for high-volume 0-100 scoring",
    )
    openai_writer_model: str = Field(
        default="gpt-5-mini",
        description="Model for outreach / open-ended answers",
    )

    # Telegram (Step 6+)
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    telegram_api_base: str = "https://api.telegram.org"
    telegram_poll_timeout: int = Field(default=30, ge=1, le=60)
    telegram_webhook_url: str | None = None
    telegram_webhook_secret: str | None = None

    # Scoring / filtering thresholds (tunable without code changes)
    tier_one_min_score: int = Field(
        default=85,
        ge=0,
        le=100,
        description="Minimum score for Tier 1 (dream companies also qualify)",
    )
    tier_two_min_score: int = Field(
        default=65,
        ge=0,
        le=100,
        description="Minimum score for Tier 2; below this is Tier 3 (filtered out)",
    )
    tier_one_drafts_enabled: bool = Field(
        default=False,
        description=(
            "When true, Tier 1 jobs also get an outreach note and a cover letter. "
            "Off keeps scoring to the score call only."
        ),
    )
    max_jd_chars: int = Field(
        default=9000,
        ge=1000,
        description="Chars of job description kept for storage and scoring prompts",
    )
    internship_only: bool = Field(
        default=False,
        description=(
            "When true, reject postings whose title has no internship signal. "
            "The code default stays false so tests and a full-time search still work. "
            "GitHub Actions production sets INTERNSHIP_ONLY=true. A local run that "
            "omits the variable will score full-time titles."
        ),
    )
    jobspy_query_timeout_seconds: int = Field(
        default=180,
        ge=1,
        description=(
            "Seconds one JobSpy query process may run before its process group is killed. "
            "This is the hard bound. asyncio.wait_for on a worker thread does not stop "
            "JobSpy's blocking HTTP calls. Installed python-jobspy does not pass "
            "ScraperInput.request_timeout into scrape_jobs. LinkedIn and Indeed set "
            "per-request timeouts of 10s or 5s; Google and ZipRecruiter set none. "
            "Those request timeouts do not bound the whole query."
        ),
    )
    enable_seniority_filter: bool = Field(
        default=True,
        description="Drop over-senior titles (director/vp/principal/...) before scoring",
    )
    seniority_title_keywords: list[str] = Field(
        default_factory=lambda: [
            "director",
            "vp",
            "avp",
            "svp",
            "evp",
            "principal",
            "chief",
            "head of",
        ],
        description="Title keywords treated as over-senior when the filter is enabled",
    )
    max_required_years_experience: int | None = Field(
        default=None,
        description="Reject JDs demanding more YOE than this; None derives it from profile",
    )
    years_experience_slack: int = Field(
        default=3,
        ge=0,
        description="Years above the candidate's experience still considered reachable",
    )
    company_cooldown_days: int = Field(
        default=30,
        ge=1,
        description="Days after a submission before the same company is re-eligible",
    )

    # Database — SQLite for local/tests; Neon Postgres for cron / production:
    # DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx.us-west-2.aws.neon.tech/neondb?sslmode=require
    # Plain postgresql:// URLs are auto-upgraded to postgresql+asyncpg://.
    database_url: str = "sqlite+aiosqlite:///storage/job_agent.db"

    # Schedule (Step 7)
    schedule_times: list[str] = Field(default_factory=lambda: ["08:00", "13:00", "18:00"])
    timezone: str = "America/Los_Angeles"
    enable_apply: bool = Field(
        default=True,
        description="Run Workday pre-fill stage in the scheduled pipeline",
    )
    enable_reviews: bool = Field(
        default=True,
        description="Send Telegram review cards after pre-fill",
    )
    enable_prep_pack: bool = Field(
        default=True,
        description="Generate and send LinkedIn/Indeed application prep packs via Telegram",
    )
    prep_pack_limit: int = Field(
        default=20,
        ge=1,
        description="Max jobs per prep-pack run. Caps LLM calls when a backlog exists.",
    )
    prep_pack_brief: bool = Field(
        default=False,
        description=(
            "When true, send the persisted shortlist as one text file. "
            "Telegram does not choose or fill that list. "
            "No LLM calls are made in brief mode. Set full mode when you need drafted answers."
        ),
    )

    # Storage paths (relative to project root unless absolute)
    resumes_dir: Path = Path("storage/resumes")
    screenshots_dir: Path = Path("storage/screenshots")
    sessions_dir: Path = Path("storage/sessions")
    prep_packs_dir: Path = Path("storage/prep_packs")
    baselines_dir: Path = Path("storage/baselines")
    benchmarks_dir: Path = Path("storage/benchmarks")

    # Resume tailoring (two-tier baseline + incremental suggestions)
    resume_skill_placement: str = Field(
        default="skills_only",
        description="skills_only | skills_and_experience",
    )
    resume_use_llm_tailoring: bool = Field(
        default=True,
        description="Use LLM for JD skill extraction when a client is available",
    )
    resume_baseline_jd_limit: int = Field(
        default=20,
        ge=5,
        le=50,
        description="Max JDs to aggregate when building a role baseline",
    )
    enable_suggestions: bool = Field(
        default=True,
        description="Generate Telegram skill suggestions after scoring staged jobs",
    )
    enable_benchmark: bool = Field(
        default=False,
        description=(
            "Run LinkedIn peer benchmarks for Tier-1 staged jobs during the pipeline "
            "(requires ENABLE_LINKEDIN_SCRAPE + saved session; off by default)"
        ),
    )

    # LinkedIn peer benchmarking (off by default — ban risk)
    enable_linkedin_scrape: bool = Field(
        default=False,
        description="Allow LinkedIn profile scraping for peer benchmarks",
    )
    linkedin_auto_search: bool = Field(
        default=False,
        description="Fully-automated LinkedIn people search (higher ban risk)",
    )
    linkedin_max_peers: int = Field(default=8, ge=1, le=25)
    linkedin_headless: bool = Field(
        default=False,
        description="Headless LinkedIn scraping (default headful for safety)",
    )

    # Browser / automation (Step 5)
    browser_headless: bool = True
    browser_channel: str | None = None
    action_delay_ms_min: int = Field(default=80, ge=0)
    action_delay_ms_max: int = Field(default=250, ge=0)
    typing_delay_ms_min: int = Field(default=30, ge=0)
    typing_delay_ms_max: int = Field(default=90, ge=0)
    credentials_path: Path = Path("config/credentials.yaml")
    apply_limit: int = Field(default=10, ge=1)
    apply_pacing_enabled: bool = True
    apply_gap_min_s: int = Field(default=420, ge=0)
    apply_gap_max_s: int = Field(default=1080, ge=0)
    apply_gap_multiplier_cap: int = Field(default=8, ge=1)
    apply_clean_streak: int = Field(default=3, ge=1)

    log_level: str = "INFO"

    def resolve_path(self, path: Path) -> Path:
        """Return an absolute path rooted at the project directory when relative."""
        return path if path.is_absolute() else PROJECT_ROOT / path

    @property
    def resumes_path(self) -> Path:
        return self.resolve_path(self.resumes_dir)

    @property
    def screenshots_path(self) -> Path:
        return self.resolve_path(self.screenshots_dir)

    @property
    def sessions_path(self) -> Path:
        return self.resolve_path(self.sessions_dir)

    @property
    def prep_packs_path(self) -> Path:
        return self.resolve_path(self.prep_packs_dir)

    @property
    def baselines_path(self) -> Path:
        return self.resolve_path(self.baselines_dir)

    @property
    def benchmarks_path(self) -> Path:
        return self.resolve_path(self.benchmarks_dir)

    @property
    def credentials_file(self) -> Path:
        return self.resolve_path(self.credentials_path)

    @property
    def base_resume_file(self) -> Path:
        """Fixed path for the candidate's personal resume PDF (default for applications)."""
        return self.resolve_path(Path("config/base_resume.pdf"))

    @property
    def active_scorer_model(self) -> str:
        """Model id used for scoring. Always the OpenAI scorer."""
        return self.openai_scorer_model

    @property
    def active_writer_model(self) -> str:
        """Model id used for outreach / open-ended answers. Always OpenAI."""
        return self.openai_writer_model

    @property
    def is_gemini(self) -> bool:
        return self.llm_provider.strip().lower() == "gemini"

    def fallback_models_for(self, model: str) -> list[str]:
        """Ordered alternates for a primary model (Gemini only), excluding duplicates."""
        if not self.is_gemini:
            return []
        seen = {model.strip()}
        out: list[str] = []
        for candidate in self.gemini_fallback_models:
            name = candidate.strip()
            if name and name not in seen:
                seen.add(name)
                out.append(name)
        return out


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()

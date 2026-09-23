# Playwright Python image includes Chromium + OS deps (matches playwright 1.62).
FROM mcr.microsoft.com/playwright/python:v1.62.0-jammy

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Project metadata first for better layer caching
COPY pyproject.toml README.md ./
COPY config ./config
COPY core ./core
COPY scraper ./scraper
COPY scorer ./scorer
COPY resume ./resume
COPY automation ./automation
COPY bot ./bot
COPY orchestrator ./orchestrator
COPY prep ./prep
COPY benchmark ./benchmark
COPY main.py ./
COPY uv.lock ./

# Install runtime deps only (no --extra dev)
RUN uv sync --frozen --no-dev

# Runtime storage (overridden by compose volumes in production)
RUN mkdir -p storage/sessions storage/resumes storage/screenshots

ENV PYTHONUNBUFFERED=1
ENV BROWSER_HEADLESS=true

CMD ["uv", "run", "python", "main.py", "serve"]

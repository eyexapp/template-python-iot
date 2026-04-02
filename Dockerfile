# syntax=docker/dockerfile:1
# Multi-arch Dockerfile for myapp IoT application
# Supports: linux/amd64, linux/arm64, linux/arm/v7 (Raspberry Pi)
#
# Build:
#   docker build -t myapp .
#
# Multi-arch build:
#   docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t myapp .

# ── Stage 1: Builder ─────────────────────────────────────────────
FROM python:3.11-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Install deps first (cache layer)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Copy source and install project
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ── Stage 2: Runtime ─────────────────────────────────────────────
FROM python:3.11-slim AS runtime

LABEL maintainer="your-team"
LABEL description="myapp IoT Sensor Collector"

RUN groupadd --gid 1000 app && \
    useradd --uid 1000 --gid app --create-home app

WORKDIR /app

# Copy virtual env from builder
COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --from=builder --chown=app:app /app/src /app/src

# Data directory for SQLite
RUN mkdir -p /app/data && chown app:app /app/data
VOLUME ["/app/data"]

ENV PATH="/app/.venv/bin:$PATH" \
    APP_ENV=production \
    DB_PATH=/app/data/sensor_data.db

USER app

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import myapp; print('ok')" || exit 1

ENTRYPOINT ["python", "-m", "myapp"]

# ── Build stage ───────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

# Install uv — fast Python package / dependency manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /build

# Copy dependency manifest first so Docker can cache this layer
COPY pyproject.toml .

# Create a virtual environment and install only runtime deps
RUN uv venv /opt/venv && \
    UV_PROJECT_ENVIRONMENT=/opt/venv uv pip install --no-cache -e .

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

LABEL org.opencontainers.image.title="MATM Backend" \
      org.opencontainers.image.description="Multi-Agent Threat Monitor — FastAPI backend" \
      org.opencontainers.image.version="0.1.0"

# Non-root user for security
RUN addgroup --system matm && adduser --system --ingroup matm matm

WORKDIR /app

# Copy the pre-built venv from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application source
COPY app/ ./app/

# Ensure the venv is on PATH
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER matm

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

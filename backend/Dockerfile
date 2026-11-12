# ADA Backend — Production Dockerfile
# Multi-stage build for minimal final image size

# --- Build stage ---
FROM python:3.12-slim AS builder

WORKDIR /build

# Copy uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency manifest and lock file
COPY pyproject.toml uv.lock* ./

# Install production dependencies into /build/.venv
RUN uv sync --frozen --no-dev --no-install-project

# --- Runtime stage ---
FROM python:3.12-slim AS runtime

# Security: non-root user
RUN useradd --create-home --uid 1001 appuser

WORKDIR /app

# Copy venv from builder
COPY --from=builder /build/.venv /app/.venv

# Copy application code
COPY ada/ ./ada/

# Owned by appuser
RUN chown -R appuser:appuser /app

USER appuser

# Activate venv by prepending to PATH
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

# Health check — Render and k8s will probe /health
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "ada.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--loop", "uvloop"]

# ADA Backend — Production Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install curl for healthcheck probe
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8000

# Copy manifests and source code
COPY pyproject.toml ./
COPY ada/ ./ada/

# Upgrade pip and install package with all production dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Security: non-root user
RUN useradd --create-home --uid 1001 appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Start Uvicorn bound to Render's dynamic $PORT
CMD ["sh", "-c", "uvicorn ada.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]

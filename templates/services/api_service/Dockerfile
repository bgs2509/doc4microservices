# ════════════════════════════════════════════════════════════════════════════════
# Multi-stage Dockerfile for FastAPI service
# ════════════════════════════════════════════════════════════════════════════════

ARG PYTHON_VERSION=3.12

# ══════════════════════════════════════════════════════════════════════════════
# Base stage - shared dependencies
# ══════════════════════════════════════════════════════════════════════════════
FROM python:${PYTHON_VERSION}-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -m -u 1000 app && \
    mkdir -p /app /var/log/app && \
    chown -R app:app /app /var/log/app

WORKDIR /app

# ══════════════════════════════════════════════════════════════════════════════
# Development stage
# ══════════════════════════════════════════════════════════════════════════════
FROM base as development

USER app

# Copy requirements
COPY --chown=app:app requirements.txt .

# Install Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy source code
COPY --chown=app:app . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run with hot reload
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ══════════════════════════════════════════════════════════════════════════════
# Production builder stage
# ══════════════════════════════════════════════════════════════════════════════
FROM base as builder

USER app

# Copy requirements
COPY --chown=app:app requirements.txt .

# Install dependencies to user site-packages
RUN pip install --user --no-cache-dir -r requirements.txt

# ══════════════════════════════════════════════════════════════════════════════
# Production stage
# ══════════════════════════════════════════════════════════════════════════════
FROM base as production

USER app

# Copy only dependencies from builder
COPY --from=builder /home/app/.local /home/app/.local

# Make sure scripts in .local are usable
ENV PATH=/home/app/.local/bin:$PATH

# Copy source code
COPY --chown=app:app src ./src

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run with multiple workers
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

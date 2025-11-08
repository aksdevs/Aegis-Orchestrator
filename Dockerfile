# ==============================================================================
# STAGE 1: Dependencies Builder (Cached Layer)
# ==============================================================================
FROM python:3.11-slim as deps-builder

# Install only essential build tools for Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment for better isolation and faster installs
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install Python dependencies (this layer will be cached)
COPY requirements-prod.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements-prod.txt

# ==============================================================================
# STAGE 2: Runtime Image (Minimal and Fast)
# ==============================================================================
FROM python:3.11-slim as runtime

# Set working directory
WORKDIR /app

# Install minimal runtime dependencies in single layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && groupadd -r aegis \
    && useradd -r -g aegis -d /app -s /bin/bash aegis

# Copy virtual environment from builder stage
COPY --from=deps-builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code (in order of change frequency for better caching)
COPY --chown=aegis:aegis config/ ./config/
COPY --chown=aegis:aegis services/ ./services/
COPY --chown=aegis:aegis agents/ ./agents/
COPY --chown=aegis:aegis main.py .

# Create workspace directory
RUN mkdir -p /workspace && chown aegis:aegis /workspace

# Set optimized environment variables
ENV PYTHONPATH=/app \
    WORKSPACE_DIR=/workspace \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Add health check (lightweight)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=2 \
    CMD curl -f http://localhost:8080/health || exit 1

# Switch to non-root user for security
USER aegis

# Expose application port
EXPOSE 8080

# Run in server mode for Cloud Run deployment
CMD ["python", "main.py", "--server"]
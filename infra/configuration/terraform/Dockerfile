FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY agents/ ./agents/
COPY services/ ./services/
COPY tests/ ./tests/

# Create workspace directory
RUN mkdir -p /workspace

# Set environment variables
ENV WORKSPACE_DIR=/workspace
ENV PYTHONPATH=/app

# Run the application
CMD ["python", "-m", "agents.orchestrator_app"]

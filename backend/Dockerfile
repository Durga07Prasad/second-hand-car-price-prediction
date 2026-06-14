# ============================================================
# CarValueAI — FastAPI Backend Dockerfile
# ============================================================
# NOTE: The SQLite database file (car_predictions.db) is created
# at runtime INSIDE the container. It resets on every redeploy.
# This is fine for demo/development purposes.
#
# For production persistence, add a Render PostgreSQL addon
# and set DATABASE_URL to the connection string provided.
# The code auto-detects and switches — no code changes needed.
# ============================================================

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for some Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code (including app_models/)
COPY . .

# Create data directory for SQLite persistence via volume mount
RUN mkdir -p /app/data

# Expose the default port
EXPOSE 8000

# Use shell form so $PORT env var is respected (Render/Railway set $PORT)
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

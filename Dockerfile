# ORFEAS Studio - Production Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY orfeas-ai-studio.html ./
COPY service-worker.js ./
COPY manifest.json ./
COPY icons/ ./icons/
COPY orfeas-3d-engine-hybrid.js ./

# Create directories
RUN mkdir -p /app/models /app/outputs /app/uploads /app/temp

# Environment
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=backend/main.py

EXPOSE 5000 8000 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Start
CMD ["python", "-u", "backend/main_minimal.py"]

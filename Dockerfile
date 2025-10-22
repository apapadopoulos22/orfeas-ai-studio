# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║ ⚔️ THERION ORFEAS - LOCAL GPU PRODUCTION DOCKERFILE ⚔️                      ║
# ║ Optimized for RTX 3090 24GB VRAM - Maximum Performance                      ║
# ║ DEUS VULT - EREVUS COLLECTIVE                                               ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# Stage 1: Python Dependencies Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY backend/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: CUDA Runtime (NVIDIA GPU Support)
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# Install Python 3.11
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    python3.11-dev \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Create symbolic link for python
RUN ln -s /usr/bin/python3.11 /usr/bin/python

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY backend/ ./backend/
COPY orfeas-studio.html ./
COPY service-worker.js ./
COPY manifest.json ./
COPY icons/ ./icons/
COPY orfeas-3d-engine-hybrid.js ./

# Create necessary directories
RUN mkdir -p /app/models /app/outputs /app/uploads /app/temp

# Set environment variables for MAXIMUM GPU PERFORMANCE
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    CUDA_VISIBLE_DEVICES=0 \
    XFORMERS_DISABLED=1 \
    DISABLE_XFORMERS=1 \
    PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512 \
    CUDA_LAUNCH_BLOCKING=0 \
    TORCH_CUDA_ARCH_LIST="8.6" \
    FORCE_CUDA=1 \
    TORCH_USE_CUDA_DSA=1

# Expose ports
EXPOSE 5000 8000 8080

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health', timeout=5)" || exit 1

# Start ORFEAS backend with GPU optimization
CMD ["python", "-u", "backend/main.py"]

#!/bin/bash
# ORFEAS Linux Deployment Quick-Start Script
# Usage: bash deploy_linux.sh

set -e

echo "════════════════════════════════════════════════════════════"
echo "  ORFEAS AI 2D3D Studio - Linux Deployment"
echo "════════════════════════════════════════════════════════════"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${YELLOW}[1/7] Checking prerequisites...${NC}"

# Check for NVIDIA driver
if ! command -v nvidia-smi &> /dev/null; then
    echo -e "${RED}✗ NVIDIA driver not found${NC}"
    echo "  Install from: https://www.nvidia.com/Download/driverDetails.aspx"
    exit 1
fi
echo -e "${GREEN}✓ NVIDIA driver found$(nvidia-smi --query-gpu=driver_version --format=csv,noheader)${NC}"

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker not found${NC}"
    echo "  Install from: https://docs.docker.com/engine/install/"
    exit 1
fi
echo -e "${GREEN}✓ Docker found$(docker --version)${NC}"

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose not found${NC}"
    echo "  Install from: https://docs.docker.com/compose/install/"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose found$(docker-compose --version)${NC}"

# Check for NVIDIA Container Toolkit
if ! docker run --rm --gpus all nvidia/cuda:12.1.0-runtime-ubuntu22.04 nvidia-smi > /dev/null 2>&1; then
    echo -e "${RED}✗ NVIDIA Container Toolkit not configured properly${NC}"
    echo "  Install from: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
    exit 1
fi
echo -e "${GREEN}✓ NVIDIA Container Toolkit working${NC}"

echo ""

# Get ORFEAS directory
echo -e "${YELLOW}[2/7] Setting up ORFEAS directory...${NC}"
ORFEAS_DIR="${1:-.}"

if [ ! -f "$ORFEAS_DIR/docker-compose.yml" ]; then
    echo -e "${RED}✗ docker-compose.yml not found in $ORFEAS_DIR${NC}"
    exit 1
fi

cd "$ORFEAS_DIR"
echo -e "${GREEN}✓ ORFEAS directory: $(pwd)${NC}"

# Create required directories
echo ""
echo -e "${YELLOW}[3/7] Creating required directories...${NC}"
mkdir -p models outputs uploads temp logs
chmod 777 outputs uploads temp logs
echo -e "${GREEN}✓ Directories ready${NC}"

# Prepare environment
echo ""
echo -e "${YELLOW}[4/7] Configuring environment...${NC}"

if [ ! -f .env ]; then
    cat > .env << 'EOF'
# ORFEAS Configuration for Linux Deployment
ORFEAS_MODE=full_ai
FLASK_ENV=production
LOG_LEVEL=INFO
DEBUG=false

# GPU Configuration
DEVICE=cuda
CUDA_VISIBLE_DEVICES=0
XFORMERS_DISABLED=0
GPU_MEMORY_LIMIT=0.85
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512,expandable_segments:True

# Server Configuration
HOST=0.0.0.0
PORT=5000
WORKERS=4
CORS_ORIGINS=*

# Model Configuration
HUNYUAN3D_PRECISION=float16
HUNYUAN3D_BATCH_SIZE=1

# Memory Management
MAX_CONCURRENT_JOBS=3
WORKER_TIMEOUT=600
REQUEST_TIMEOUT=180

# Features
ENABLE_MONITORING=true
ENABLE_CACHING=true
EOF
    echo -e "${GREEN}✓ .env created with optimal Linux settings${NC}"
else
    echo -e "${GREEN}✓ .env already exists${NC}"
fi

# Download Hunyuan3D model (optional but recommended)
echo ""
echo -e "${YELLOW}[5/7] Model preparation${NC}"

HF_CACHE="${HOME}/.cache/huggingface/hub/models--tencent--Hunyuan3D-2"
if [ -d "$HF_CACHE" ]; then
    echo -e "${GREEN}✓ Hunyuan3D model found in HuggingFace cache${NC}"
else
    echo -e "${YELLOW}⚠ Hunyuan3D model not found (will download during first startup)${NC}"
    echo "  This will take 30-60 seconds on first run"
    echo "  Subsequent startups will be <1 second"
fi

# Build Docker image
echo ""
echo -e "${YELLOW}[6/7] Building Docker image...${NC}"
docker-compose build --no-cache

# Start services
echo ""
echo -e "${YELLOW}[7/7] Starting ORFEAS services...${NC}"
docker-compose up -d

# Wait for services to be ready
echo ""
echo -e "${YELLOW}Waiting for services to start (model loading in background)...${NC}"
WAIT_COUNT=0
while [ $WAIT_COUNT -lt 120 ]; do
    if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
        break
    fi
    echo -n "."
    WAIT_COUNT=$((WAIT_COUNT + 1))
    sleep 1
done

# Verify deployment
echo ""
echo -e "${YELLOW}Verifying deployment...${NC}"

HEALTH=$(curl -s http://localhost:5000/api/health 2>/dev/null || echo "error")
if [ "$HEALTH" = "error" ]; then
    echo -e "${RED}✗ Server not responding${NC}"
    echo "  Check logs: docker-compose logs backend"
    exit 1
fi

echo "$HEALTH" | grep -q '"status":"ok"' && STATUS="ok" || STATUS="loading"

if [ "$STATUS" = "ok" ]; then
    echo -e "${GREEN}✓ Model ready!${NC}"
else
    echo -e "${YELLOW}⚠ Model still loading (check logs in 30 seconds)${NC}"
fi

# Summary
echo ""
echo "════════════════════════════════════════════════════════════"
echo -e "${GREEN}✓ ORFEAS Deployment Complete!${NC}"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Web Interface:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:5000"
echo ""
echo "Useful Commands:"
echo "  View logs:           docker-compose logs -f backend"
echo "  Check GPU memory:    docker exec orfeas-backend-production nvidia-smi"
echo "  Stop services:       docker-compose down"
echo "  Restart backend:     docker-compose restart backend"
echo ""
echo "Next Steps:"
echo "  1. Open http://localhost:3000 in your browser"
echo "  2. Upload an image to generate 3D model"
echo "  3. Download the generated .stl file"
echo ""
echo "Documentation:"
echo "  Deployment Guide: LINUX_DEPLOYMENT_GUIDE.md"
echo "  CUDA Optimization: CUDA_MEMORY_OPTIMIZATION.md"
echo ""

# Monitor logs for a moment
echo "Monitor logs for 10 seconds (Ctrl+C to stop):"
timeout 10 docker-compose logs -f backend || true

echo ""
echo -e "${GREEN}Deployment ready! Check backend status: docker-compose logs backend${NC}"

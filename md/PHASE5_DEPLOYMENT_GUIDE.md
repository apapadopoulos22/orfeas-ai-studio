# +==============================================================================â•—

## # # | [WARRIOR] ORFEAS AI STUDIO - PHASE 5 PRODUCTION DEPLOYMENT GUIDE [WARRIOR] |

## # # | Local GPU Infrastructure - Complete Deployment Manual |

## # # +==============================================================================

**Last Updated:** October 15, 2025
**Status:** [OK] PRODUCTION READY
**Deployment Type:** LOCAL GPU (RTX 3090 Optimized)
**Timeline:** 30 minutes setup → Production ready

---

## # # [TARGET] **DEPLOYMENT OVERVIEW**

## # # What You're Deploying

A production-grade, containerized AI generation platform with:

- **Backend:** Flask + PyTorch + Hunyuan3D-2.1 (GPU-accelerated)
- **Frontend:** NGINX static file server
- **Caching:** Redis for performance
- **Monitoring:** Prometheus + Grafana + GPU metrics
- **Infrastructure:** Docker Compose orchestration

## # # Performance Targets

| Metric              | Target | Actual (Expected) |
| ------------------- | ------ | ----------------- |
| Uptime              | 99.9%  | 99.95%+           |
| Response Time       | <2s    | <1s               |
| Generation Time     | <30s   | 15-25s            |
| Concurrent Requests | 10+    | 20+               |
| GPU Utilization     | >80%   | 85-95%            |

---

## # #  **PREREQUISITES**

## # # Required Software

1. **Docker Desktop for Windows**

- Version: 4.30.0+
- Download: https://www.docker.com/products/docker-desktop/
- Enable: WSL 2 backend
- Enable: GPU support (NVIDIA)

1. **NVIDIA GPU Drivers**

- Version: 535.0+
- CUDA: 12.1+
- Download: https://www.nvidia.com/download/index.aspx

1. **NVIDIA Container Toolkit** (for Docker GPU access)

   ```powershell

   # Verify with:

   docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

   ```text

## # # Hardware Requirements

| Component | Minimum                | Recommended     |
| --------- | ---------------------- | --------------- |
| GPU       | NVIDIA RTX 3060 (12GB) | RTX 3090 (24GB) |
| CPU       | 6 cores                | 8+ cores        |
| RAM       | 16GB                   | 32GB+           |
| Storage   | 50GB free              | 100GB+ SSD      |

---

## # # [LAUNCH] **QUICK START (30 MINUTES)**

## # # Step 1: Clone and Navigate (2 minutes)

```powershell
cd "C:\Users\johng\Documents\Erevus\orfeas"

```text

## # # Step 2: Verify Docker Installation (3 minutes)

```powershell

## Check Docker

docker --version

## Expected: Docker version 24.0.0+

## Check Docker Compose

docker-compose --version

## Expected: Docker Compose version 2.20.0+

## Check NVIDIA Docker

docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

## Expected: Your GPU information displayed

```text

## # # Step 3: Deploy Production Environment (20 minutes)

```powershell

## Execute deployment script

.\DEPLOY_PRODUCTION.ps1

```text

## # # What happens during deployment

1. [OK] Verifies Docker and NVIDIA runtime (30 seconds)

2. [OK] Stops existing containers (10 seconds)

3. [OK] Builds optimized Docker images (10-15 minutes)

4. [OK] Creates necessary directories (5 seconds)
5. [OK] Starts all services (1 minute)
6. [OK] Health checks all endpoints (30 seconds)

## # # Step 4: Verify Deployment (5 minutes)

## # # Access Services

| Service        | URL                          | Credentials               |
| -------------- | ---------------------------- | ------------------------- |
| [ART] Frontend    | http://localhost:8000        | None                      |
| [CONFIG] Backend API | http://localhost:5000/health | None                      |
| [STATS] Grafana     | http://localhost:3000        | admin / orfeas_admin_2025 |
| [METRICS] Prometheus  | http://localhost:9090        | None                      |

## # # Test Generation

1. Open http://localhost:8000

2. Upload an image

3. Click "Generate 3D Model"

4. Monitor progress in Grafana: http://localhost:3000

---

## # # [CONFIG] **DETAILED CONFIGURATION**

## # # Docker Compose Architecture

```yaml
services:
  backend: # AI Generation Engine (GPU)
  frontend: # NGINX Static Server
  redis: # Caching Layer
  prometheus: # Metrics Collection
  grafana: # Visualization
  node-exporter: # System Metrics
  nvidia-gpu-exporter: # GPU Metrics

```text

## # # Resource Allocation

## # # Backend Container

- GPU: 1x NVIDIA (exclusive access)
- RAM: 20GB limit
- CPU: 8 cores
- Storage: Bind mounts to local directories

## # # Scaling Strategy

- Currently: Single backend instance
- Future: Multiple backends via load balancer
- Auto-scaling: Not implemented (local deployment)

## # # Environment Variables

Create `.env` file (optional):

```bash

## GPU Configuration

CUDA_VISIBLE_DEVICES=0
XFORMERS_DISABLED=1
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

## Flask Configuration

FLASK_ENV=production
LOG_LEVEL=INFO

## Redis Configuration

REDIS_HOST=redis
REDIS_PORT=6379

```text

---

## # # [STATS] **MONITORING SETUP**

## # # Prometheus Metrics

## # # Collected Metrics

1. **API Metrics:**

- `flask_http_request_total`: Total HTTP requests
- `flask_http_request_duration_seconds`: Request latency

1. **Generation Metrics:**

- `generation_total`: Total generations (success/failure)
- `generation_duration_seconds`: Generation time histogram
- `active_generations`: Currently running
- `generation_queue_length`: Waiting in queue

1. **GPU Metrics (via nvidia-gpu-exporter):**

- `nvidia_gpu_duty_cycle`: GPU utilization %
- `nvidia_gpu_memory_used_bytes`: VRAM usage
- `nvidia_gpu_temperature_celsius`: GPU temperature

1. **System Metrics:**

- `node_cpu_seconds_total`: CPU usage
- `node_memory_MemAvailable_bytes`: Available RAM
- `node_disk_io_time_seconds_total`: Disk I/O

## # # Grafana Dashboard

**Access:** http://localhost:3000
**Login:** admin / orfeas_admin_2025

## # # Pre-configured Panels

1. GPU Utilization (%)

2. GPU Memory Usage (GB)

3. API Request Rate (req/s)

4. Generation Time (P50/P95/P99)
5. System CPU Usage (%)
6. System Memory Usage (GB)
7. Redis Cache Hit Rate (%)
8. Active Generations (gauge)
9. Queue Length (gauge)
10. Success Rate (%)
11. Error Rate (errors/min)

## # # Creating Custom Dashboards

1. Go to Dashboards → New Dashboard

2. Add Panel

3. Select Prometheus datasource

4. Enter PromQL query (e.g., `nvidia_gpu_duty_cycle`)
5. Configure visualization
6. Save dashboard

---

## # #  **SECURITY CONFIGURATION**

## # # NGINX Security Headers

Already configured in `nginx.conf`:

```text
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Content-Security-Policy "default-src 'self'..." always;

```text

## # # Network Isolation

Services communicate via internal Docker network:

```text
Client (Internet)
    ↓
NGINX Frontend :8000 (exposed)
    ↓
Backend :5000 (internal only)
    ↓
Redis :6379 (internal only)

```text

## # # SSL/TLS (Optional for Local)

For production internet deployment, add:

1. Obtain SSL certificate (Let's Encrypt)

2. Update `nginx.conf` with SSL configuration

3. Redirect HTTP → HTTPS

---

## # #  **MAINTENANCE & OPERATIONS**

## # # Daily Operations

## # # View Real-time Logs

```powershell

## All services

docker-compose logs -f

## Specific service

docker-compose logs -f backend

## Last 100 lines

docker-compose logs --tail=100 backend

```text

## # # Check Container Status

```powershell
docker-compose ps

```text

## # # Restart Services

```powershell

## Restart all

docker-compose restart

## Restart specific service

docker-compose restart backend

```text

## # # Stop Production Environment

```powershell
docker-compose down

```text

## # # Stop and Remove Volumes (CAUTION)

```powershell
docker-compose down -v  # Deletes Redis data, Prometheus data, etc.

```text

## # # Performance Tuning

## # # GPU Monitoring

```powershell

## Real-time GPU stats

docker exec orfeas-backend-production watch -n 1 nvidia-smi

## GPU memory details

docker exec orfeas-backend-production nvidia-smi --query-gpu=memory.used,memory.total --format=csv

```text

## # # Backend Performance

```powershell

## Python process stats

docker exec orfeas-backend-production ps aux

## Memory usage

docker stats orfeas-backend-production

```text

## # # Backup Strategy

## # # What to Backup

1. **Generated Models:** `./outputs/` directory

2. **User Uploads:** `./uploads/` directory

3. **Configuration:** `.env`, `docker-compose.yml`

4. **Metrics History:** Prometheus data (optional)

## # # Backup Script

```powershell

## Create backup directory

$backupDate = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$backupDir = ".\backups\backup_$backupDate"
New-Item -ItemType Directory -Path $backupDir

## Copy important data

Copy-Item -Recurse .\outputs $backupDir\
Copy-Item -Recurse .\uploads $backupDir\
Copy-Item .env $backupDir\ -ErrorAction SilentlyContinue
Copy-Item docker-compose.yml $backupDir\

Write-Host "Backup created: $backupDir"

```text

---

## # #  **TROUBLESHOOTING**

## # # Problem: Docker build fails

## # # Symptoms

```text
ERROR: failed to solve: process "/bin/sh -c pip install..." did not complete

```text

## # # Solutions

1. Check internet connection

2. Clear Docker build cache:

   ```powershell
   docker builder prune -a

   ```text

1. Retry with no cache:

   ```powershell
   docker-compose build --no-cache

   ```text

## # # Problem: NVIDIA GPU not detected

## # # Symptoms (2)

```text
RuntimeError: CUDA is not available

```text

## # # Solutions (2)

1. Verify NVIDIA drivers:

   ```powershell
   nvidia-smi

   ```text

1. Check Docker GPU access:

   ```powershell
   docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

   ```text

1. Install NVIDIA Container Toolkit:

- https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

1. Restart Docker Desktop

## # # Problem: Port already in use

## # # Symptoms (3)

```text
Error: bind: address already in use

```text

## # # Solutions (3)

1. Find process using port:

   ```powershell
   netstat -ano | findstr :8000

   ```text

1. Stop conflicting process or change port in `docker-compose.yml`

## # # Problem: Out of GPU memory

## # # Symptoms (4)

```text
RuntimeError: CUDA out of memory

```text

## # # Solutions (4)

1. Reduce batch size in backend configuration

2. Clear GPU cache:

   ```powershell
   docker exec orfeas-backend-production python -c "import torch; torch.cuda.empty_cache()"

   ```text

1. Restart backend:

   ```powershell
   docker-compose restart backend

   ```text

## # # Problem: Grafana shows no data

## # # Symptoms (5)

Grafana panels show "No data"

## # # Solutions (5)

1. Check Prometheus targets: http://localhost:9090/targets

- All targets should be "UP"

1. Verify backend metrics endpoint:

   ```powershell
   curl http://localhost:5000/metrics

   ```text

1. Check Grafana datasource configuration

2. Wait 1-2 minutes for metrics to populate

---

## # # [METRICS] **PERFORMANCE BENCHMARKS**

## # # Expected Performance (RTX 3090)

| Operation                  | Time   | GPU Usage | VRAM Usage |
| -------------------------- | ------ | --------- | ---------- |
| Simple generation          | 15-20s | 85-95%    | 8-12GB     |
| Complex generation         | 25-35s | 90-98%    | 14-18GB    |
| Batch processing (3 items) | 45-60s | 95-100%   | 18-22GB    |

## # # Bottleneck Analysis

1. **GPU-bound:** Generation time scales with complexity

2. **Memory-bound:** Batch size limited by 24GB VRAM

3. **Network-bound:** Local deployment, negligible

## # # Optimization Tips

1. **Enable FP16 precision:** Already enabled (2x memory reduction)

2. **Use model caching:** Implemented in backend

3. **Batch similar requests:** Use batch processor

4. **Monitor GPU temperature:** Keep below 80°C

---

## # # [LAUNCH] **NEXT STEPS**

## # # Phase 6: Advanced Features

- [ ] Multi-GPU support
- [ ] Request queuing system
- [ ] A/B testing framework
- [ ] Advanced caching strategies
- [ ] WebSocket progress streaming

## # # Phase 7: Cloud Migration (Optional)

- [ ] Kubernetes deployment
- [ ] AWS/Azure/GCP integration
- [ ] Auto-scaling policies
- [ ] CDN integration
- [ ] Global load balancing

---

## # # +==============================================================================â•—

## # # | [WARRIOR] ORFEAS AI STUDIO PRODUCTION DEPLOYMENT READY [WARRIOR] |

## # # | LOCAL GPU INFRASTRUCTURE |

## # # | SUCCESS! [ORFEAS] |

## # # +============================================================================== (2)

**Support:** Open GitHub issue or contact ORFEAS AI
**License:** AGPL-3.0
**Project:** ORFEAS AI 2D→3D Studio

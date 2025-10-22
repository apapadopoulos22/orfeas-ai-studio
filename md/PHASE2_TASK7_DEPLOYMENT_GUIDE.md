# Phase 2.7: Production Deployment - Complete Guide

## # # Status**:**IMPLEMENTATION COMPLETE

**Date**: October 17, 2025

---

## # #  Overview

Phase 2.7 delivers a production-ready deployment of ORFEAS AI 2D→3D Studio with:

 **Docker containerization** - Isolated, reproducible environment
 **Production WSGI server** - Gunicorn for concurrent request handling
 **HTTPS/TLS support** - Secure connections with self-signed or CA certificates
 **Health checks** - Automatic restart on failure
 **Backup/restore** - Data persistence and recovery
 **Full monitoring stack** - Prometheus + Grafana with 48+ metrics
 **Graceful shutdown** - Clean process termination

---

## # #  Deliverables

## # # Files Created (10 files)

1. **`Dockerfile.production`** (130 lines)

- Multi-stage build for optimized image size
- CUDA 11.8 with cuDNN 8 for RTX 3090 support
- Non-root `orfeas` user for security
- Built-in health checks
- Python 3.11 with production dependencies

1. **`docker-compose.production.yml`** (270 lines)

- Full production stack:

  - Backend (Flask + Gunicorn + GPU)
  - Nginx (reverse proxy + HTTPS)
  - Redis (job queue)
  - Prometheus (metrics collection)
  - Grafana (metrics visualization)

- Network isolation (`orfeas-network`)
- Volume management for persistence
- GPU passthrough for backend

1. **`gunicorn.conf.py`** (220 lines)

- Worker configuration: `(CPU cores × 2) + 1`
- Timeout: 300s (for long 3D generation tasks)
- Graceful shutdown with 30s grace period
- Worker recycling after 1000 requests
- Comprehensive logging and lifecycle hooks

1. **`nginx.production.conf`** (280 lines)

- HTTP → HTTPS redirect
- TLS 1.2/1.3 with modern cipher suites
- Rate limiting (10 req/min for API, 100 req/s general)
- WebSocket proxy for real-time progress
- Static file caching (1 year for assets)
- Security headers (HSTS, CSP, X-Frame-Options)

1. **`generate_ssl_certs.ps1`** (110 lines)

- Self-signed SSL certificate generation
- OpenSSL wrapper with Docker fallback
- 4096-bit RSA, 365-day validity
- Certificate verification

1. **`.env.production.template`** (200 lines)

- Complete production configuration template
- GPU settings (memory limit, concurrent jobs)
- Model configuration
- Monitoring and logging settings
- Security configuration
- Feature flags

1. **`deploy.ps1`** (340 lines)

- One-command deployment script
- Pre-flight checks (Docker, GPU runtime)
- Automatic SSL generation
- Docker build and startup
- Health validation with retries
- Deployment summary with access points

1. **`backup.ps1`** (220 lines)

- Backs up outputs, logs, model cache
- Exports Docker volumes (Prometheus, Grafana)
- Configuration file backup
- Creates compressed archive
- Optional model cache skip (large files)

1. **`restore.ps1`** (200 lines)

- Restores from backup archives
- Validates backup integrity
- Restores outputs, logs, configuration
- Restores Docker volumes
- Safety confirmation before overwrite

1. **`md/PHASE2_TASK7_DEPLOYMENT_GUIDE.md`** (THIS FILE)

    - Complete deployment documentation
    - Troubleshooting guide
    - Configuration reference

---

## # #  Quick Start

## # # Prerequisites

- **Docker Desktop** 20.10+ with GPU support
- **NVIDIA Docker Runtime** (for GPU acceleration)
- **Windows PowerShell** 5.1+
- **RTX 3090** or compatible NVIDIA GPU (24GB VRAM recommended)

## # # One-Command Deployment

```powershell

## Navigate to project directory

cd c:\Users\johng\Documents\Erevus\orfeas

## Deploy entire production stack

.\deploy.ps1

```text

That's it! The script will:

1. Check prerequisites

2. Generate SSL certificates

3. Build Docker images

4. Start all services
5. Run health checks
6. Display access URLs

---

## # #  Manual Deployment Steps

If you prefer manual control or need to troubleshoot:

## # # 1. Generate SSL Certificates

```powershell

## Option A: Using the script

.\generate_ssl_certs.ps1

## Option B: Using Docker directly

docker run --rm -v ${PWD}/ssl:/ssl alpine/openssl req -x509 -newkey rsa:4096 -nodes -out /ssl/cert.pem -keyout /ssl/key.pem -days 365 -subj "/CN=localhost/O=ORFEAS AI/C=US"

```text

## # # 2. Configure Environment

```powershell

## Copy template

Copy-Item .env.production.template .env.production

## Edit configuration

notepad .env.production

## Important: Change these values

## - SECRET_KEY (generate random 64-char string)

## - GF_SECURITY_ADMIN_PASSWORD (Grafana admin password)

## - GPU_MEMORY_LIMIT (default: 0.8 = 80% of VRAM)

## - MAX_CONCURRENT_JOBS (default: 3)

```text

## # # 3. Build Docker Images

```powershell

## Build all services

docker-compose -f docker-compose.production.yml build

## Force rebuild (no cache)

docker-compose -f docker-compose.production.yml build --no-cache

```text

## # # 4. Start Services

```powershell

## Start all services in background

docker-compose -f docker-compose.production.yml up -d

## View logs

docker-compose -f docker-compose.production.yml logs -f

## View specific service logs

docker-compose -f docker-compose.production.yml logs -f backend

```text

## # # 5. Verify Deployment

```powershell

## Check service status

docker-compose -f docker-compose.production.yml ps

## Test backend health

curl http://localhost:5000/health

## Test Nginx health

curl http://localhost/health

## Test Prometheus

curl http://localhost:9090/-/healthy

## Test Grafana

curl http://localhost:3000/api/health

```text

---

## # #  Access Points

After successful deployment:

| Service              | URL                   | Default Credentials            |
| -------------------- | --------------------- | ------------------------------ |
| **Frontend (HTTP)**  | http://localhost      | N/A                            |
| **Frontend (HTTPS)** | https://localhost     | N/A (self-signed cert warning) |
| **Backend API**      | http://localhost:5000 | N/A                            |
| **Prometheus**       | http://localhost:9090 | N/A                            |
| **Grafana**          | http://localhost:3000 | admin / (see .env.production)  |
| **Redis**            | localhost:6379        | N/A                            |

---

## # #  Architecture

```text

          INTERNET / USERS

                   HTTPS (443) / HTTP (80)
                  â–¼

        Nginx (Reverse Proxy + HTTPS)

  - SSL/TLS Termination
  - Rate Limiting (10 req/min API)
  - Static File Serving
  - WebSocket Proxy
  - Security Headers

                   HTTP (5000)
                  â–¼

    ORFEAS Backend (Flask + Gunicorn)
  Workers: 8 (CPU × 2 + 1)
  GPU: RTX 3090 (24GB VRAM, 80% limit)
  Hunyuan3D-2.1 Models
  Timeout: 300s (for 3D generation)

      â–¼                       â–¼              â–¼

 Redis                GPU          Models
 (Queue)              Manager      (Cache)

                  â–¼

         Monitoring Stack

  - Prometheus (metrics, 48+ collectors)
  - Grafana (dashboards, real-time)

```text

---

## # #  Configuration Reference

## # # GPU Settings

```bash

## .env.production

DEVICE=cuda                    # auto, cuda, cpu
CUDA_VISIBLE_DEVICES=0         # GPU index (0 for first GPU)
GPU_MEMORY_LIMIT=0.8           # 80% of total VRAM (safety margin)
MAX_CONCURRENT_JOBS=3          # Maximum concurrent 3D generation jobs

```text

## # # Recommended GPU Settings by VRAM

- **8GB**: `GPU_MEMORY_LIMIT=0.7`, `MAX_CONCURRENT_JOBS=1`
- **12GB**: `GPU_MEMORY_LIMIT=0.75`, `MAX_CONCURRENT_JOBS=2`
- **16GB**: `GPU_MEMORY_LIMIT=0.8`, `MAX_CONCURRENT_JOBS=2`
- **24GB (RTX 3090)**: `GPU_MEMORY_LIMIT=0.8`, `MAX_CONCURRENT_JOBS=3`

## # # Worker Configuration

```python

## gunicorn.conf.py

workers = min(multiprocessing.cpu_count() * 2 + 1, 8)
timeout = 300  # 5 minutes (3D generation takes ~82s + buffer)

```text

## # # Recommended Worker Count

- **4-core CPU**: 8 workers (capped at 8)
- **8-core CPU**: 8 workers (capped at 8)
- **16-core CPU**: 8 workers (GPU is bottleneck, not CPU)

## # # Rate Limiting

```text

## nginx.production.conf

limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/m;
limit_req_zone $binary_remote_addr zone=general_limit:10m rate=100r/s;

```text

## # # Adjust for Your Use Case

- **Development/Testing**: Remove rate limits or increase to 100r/m
- **Production (Public)**: Keep at 10r/m or lower
- **Production (Internal)**: Increase to 30r/m

---

## # #  Management Commands

## # # Service Management

```powershell

## Start services

docker-compose -f docker-compose.production.yml up -d

## Stop services

docker-compose -f docker-compose.production.yml down

## Restart services

docker-compose -f docker-compose.production.yml restart

## Restart specific service

docker-compose -f docker-compose.production.yml restart backend

## View logs (all services)

docker-compose -f docker-compose.production.yml logs -f

## View logs (specific service)

docker-compose -f docker-compose.production.yml logs -f backend

## Check service status

docker-compose -f docker-compose.production.yml ps

```text

## # # Backup and Restore

```powershell

## Create backup

.\backup.ps1

## Create backup (skip large model files)

.\backup.ps1 -SkipModels

## Restore from backup

.\restore.ps1 -BackupFile "backups\orfeas_backup_20251017_120000.zip"

## Restore from backup (skip models)

.\restore.ps1 -BackupFile "backups\orfeas_backup_20251017_120000.zip" -SkipModels

## Force restore without confirmation

.\restore.ps1 -BackupFile "backups\orfeas_backup_20251017_120000.zip" -Force

```text

## # # Monitoring

```powershell

## View Prometheus metrics

curl http://localhost:9090/api/v1/query?query=up

## View backend metrics

curl http://localhost:5000/metrics

## View GPU usage

docker exec orfeas-backend-production nvidia-smi

## View container resource usage

docker stats orfeas-backend-production

```text

---

## # #  Troubleshooting

## # # Backend Fails to Start

**Symptom**: Backend container exits immediately

**Solutions**:

```powershell

## 1. Check logs

docker-compose -f docker-compose.production.yml logs backend

## 2. Verify GPU access

docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

## 3. Check environment variables

docker-compose -f docker-compose.production.yml config

## 4. Rebuild without cache

docker-compose -f docker-compose.production.yml build --no-cache backend
docker-compose -f docker-compose.production.yml up -d backend

```text

## # # Model Loading Fails

**Symptom**: Backend crashes during model initialization

**Solutions**:

```powershell

## 1. Clear model cache

docker volume rm orfeas_huggingface-cache
docker volume rm orfeas_hy3dgen-cache

## 2. Restart backend

docker-compose -f docker-compose.production.yml restart backend

## 3. Check available disk space

docker system df

## 4. Try FP32 instead of FP16 (slower but more compatible)

## Edit backend/hunyuan_integration.py line 141

## torch_dtype=torch.float32

```text

## # # HTTPS Not Working

**Symptom**: Browser shows SSL error or refuses connection

**Solutions**:

```powershell

## 1. Regenerate SSL certificates

.\generate_ssl_certs.ps1

## 2. Accept self-signed certificate in browser

## Click "Advanced" → "Proceed to localhost (unsafe)"

## 3. For production, use Let's Encrypt

## Install certbot and run

## certbot certonly --standalone -d yourdomain.com

## Copy certs to ssl/ directory

```text

## # # High Memory Usage

**Symptom**: System runs out of memory or GPU VRAM

**Solutions**:

```powershell

## 1. Reduce concurrent jobs

## Edit .env.production

MAX_CONCURRENT_JOBS=1

## 2. Lower GPU memory limit

GPU_MEMORY_LIMIT=0.6

## 3. Reduce worker count

## Edit gunicorn.conf.py

workers = 4

## 4. Restart services

docker-compose -f docker-compose.production.yml restart

```text

## # # Prometheus Not Scraping

**Symptom**: No data in Grafana dashboards

**Solutions**:

```powershell

## 1. Check Prometheus targets

curl http://localhost:9090/api/v1/targets

## 2. Verify backend metrics endpoint

curl http://localhost:5000/metrics

## 3. Check Prometheus logs

docker-compose -f docker-compose.production.yml logs prometheus

## 4. Restart Prometheus

docker-compose -f docker-compose.production.yml restart prometheus

```text

---

## # #  Production Checklist

Before deploying to production:

- [ ] **Change default passwords** in `.env.production`

- [ ] `SECRET_KEY` (64-character random string)
- [ ] `GF_SECURITY_ADMIN_PASSWORD` (Grafana admin password)

- [ ] **SSL Certificates**

- [ ] Generate proper CA-signed certificates (Let's Encrypt or commercial)
- [ ] Update `nginx.production.conf` with certificate paths
- [ ] Enable OCSP stapling for TLS

- [ ] **Security Configuration**

- [ ] Update `CORS_ORIGINS` with actual domain (remove `*`)
- [ ] Enable `CSRF_ENABLED=1` in `.env.production`
- [ ] Set `SESSION_COOKIE_SECURE=1`
- [ ] Review rate limits in `nginx.production.conf`

- [ ] **Backup Configuration**

- [ ] Set up automated daily backups (cron/Task Scheduler)
- [ ] Test restore procedure
- [ ] Configure off-site backup storage

- [ ] **Monitoring Setup**

- [ ] Configure Grafana dashboards
- [ ] Set up Prometheus alerting rules
- [ ] Configure email/Slack notifications

- [ ] **Load Testing**

- [ ] Run Phase 2.6 load tests against production deployment
- [ ] Validate performance under peak load
- [ ] Monitor GPU/CPU/memory usage

- [ ] **Documentation**

  - [ ] Document production architecture
  - [ ] Create runbooks for common operations
  - [ ] Document disaster recovery procedures

---

## # #  Next Steps

After Phase 2.7 deployment is complete:

1. **Phase 2.7 Complete** - Production infrastructure deployed and validated

1. **Return to Phase 2.6** - Execute load tests in production environment:

- Baseline test (7 minutes)
- Normal load test (10 minutes)
- Peak load test (5 minutes)
- Spike test (5 minutes)
- Sustained load test (60 minutes)

1. **Phase 2.8** - Documentation and Demo:

- Performance tuning guide
- Complete deployment guide
- Stakeholder demo preparation

1. **Phase 3** - Advanced Features (from audit recommendations)

---

## # # Status**:**PRODUCTION DEPLOYMENT READY

**Total Files**: 10 files (2200+ lines)
**Deployment Time**: ~15 minutes (including model loading)
**Next Action**: Run `.\deploy.ps1` to deploy production stack

---

## # # ORFEAS AI Project

_Production-Ready 2D→3D AI Studio_

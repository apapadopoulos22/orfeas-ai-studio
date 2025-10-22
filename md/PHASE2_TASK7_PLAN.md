# Phase 2.7: Production Deployment - Implementation Plan

## # # Status**:**READY TO START

**Priority**: HIGH (resolves backend stability issues)
**Estimated Time**: 1 day (8 hours)

---

## # #  Objectives

Deploy ORFEAS AI 2D→3D Studio to production with:

1. **Docker Containerization** - Isolated, reproducible environment

2. **Production WSGI Server** - Gunicorn for concurrent handling

3. **HTTPS/TLS** - Secure connections

4. **Health Checks** - Automatic restart on failure
5. **Automated Backups** - Data persistence
6. **Graceful Shutdown** - Clean process termination
7. **Load Balancing** - Ready for horizontal scaling

---

## # #  Task Breakdown

## # # Task 1: Production Dockerfile (1 hour)

**Objective**: Create optimized production container

**Deliverables**:

- `Dockerfile.production` - Multi-stage build for smaller image
- `.dockerignore` - Exclude unnecessary files
- Production-grade base image (Python 3.11-slim)

**Key Features**:

- CUDA support for RTX 3090
- Non-root user for security
- Health check built-in
- Volume mounts for persistence
- Environment variable configuration

## # # Task 2: Docker Compose Production (1 hour)

**Objective**: Multi-service orchestration

**Deliverables**:

- `docker-compose.production.yml` - Full stack definition
- Services: backend, nginx, redis, prometheus, grafana
- Network isolation
- Volume management

**Services**:

```yaml
services:
  backend: # ORFEAS Flask app with Gunicorn
  nginx: # Reverse proxy + HTTPS
  redis: # Job queue (future)
  prometheus: # Metrics collection
  grafana: # Metrics visualization

```text

## # # Task 3: Gunicorn Configuration (30 min)

**Objective**: Production-grade WSGI server

**Deliverables**:

- `gunicorn.conf.py` - Worker configuration
- Worker count: CPU cores × 2 + 1
- Timeout: 300s (for long 3D generation)
- Keep-alive connections
- Graceful shutdown handling

## # # Task 4: Nginx Configuration (1 hour)

**Objective**: Reverse proxy with HTTPS

**Deliverables**:

- `nginx.conf` - Reverse proxy configuration
- SSL/TLS certificates (self-signed for dev)
- Rate limiting
- Static file serving
- WebSocket proxy support

## # # Task 5: Health Check System (1 hour)

**Objective**: Automatic monitoring and restart

**Deliverables**:

- Enhanced `/health` endpoint
- Docker health check configuration
- Restart policy: `on-failure`
- Liveness probe
- Readiness probe

## # # Task 6: Backup & Persistence (1 hour)

**Objective**: Data safety and recovery

**Deliverables**:

- Volume configuration for:

  - Model cache (`/root/.cache/huggingface`)
  - Generated outputs (`/app/outputs`)
  - Logs (`/app/logs`)
  - Prometheus data
  - Grafana dashboards

- Backup script (`backup.sh`)
- Restore script (`restore.sh`)

## # # Task 7: Environment Configuration (30 min)

**Objective**: Secure configuration management

**Deliverables**:

- `.env.production` - Production environment variables
- Secrets management
- Configuration validation
- Environment-specific overrides

## # # Task 8: Deployment Scripts (1 hour)

**Objective**: One-command deployment

**Deliverables**:

- `deploy.ps1` - Windows deployment script
- `deploy.sh` - Linux deployment script
- Pre-flight checks
- Automated testing
- Rollback capability

## # # Task 9: Testing & Validation (1.5 hours)

**Objective**: Verify production deployment

**Test Checklist**:

- [ ] Container builds successfully
- [ ] All services start
- [ ] Health check passes
- [ ] HTTPS works
- [ ] WebSocket connects
- [ ] 3D generation works
- [ ] Prometheus scraping
- [ ] Grafana accessible
- [ ] Graceful shutdown works
- [ ] Restart after failure works

## # # Task 10: Documentation (30 min)

**Objective**: Deployment guide

**Deliverables**:

- `DEPLOYMENT_GUIDE.md` - Step-by-step instructions
- Troubleshooting section
- Configuration reference
- Backup/restore procedures

---

## # #  Production Architecture

```text

          INTERNET / USERS

                   HTTPS (443)
                  â–¼

              NGINX (Reverse Proxy)

  - SSL/TLS Termination
  - Rate Limiting
  - Static File Serving
  - WebSocket Proxy

                   HTTP (5000)
                  â–¼

         ORFEAS Backend (Gunicorn)
  Workers: 4-8 (CPU × 2 + 1)
  GPU: RTX 3090 (24GB)
  Hunyuan3D-2.1 Models

      â–¼                       â–¼

 Redis                GPU
 (Queue)              Manager

                  â–¼

             Monitoring Stack

  - Prometheus (metrics)
  - Grafana (dashboards)

```text

---

## # #  Success Criteria

Phase 2.7 is COMPLETE when:

1. Production Docker image builds (<5 min)

2. All services start with `docker-compose up -d`

3. Health check endpoint returns 200 OK

4. HTTPS accessible on port 443
5. 3D generation works end-to-end
6. WebSocket connections work
7. Prometheus scrapes metrics successfully
8. Grafana dashboards display data
9. Graceful shutdown works (`docker-compose down`)
10. Auto-restart on failure works
11. Backup/restore tested successfully
12. Load testing can run successfully

---

## # #  Quick Start Command

Once complete, deployment will be:

```powershell

## Deploy full production stack

.\deploy.ps1

## Or manually

docker-compose -f docker-compose.production.yml up -d

## Check health

curl https://localhost/health

## View logs

docker-compose logs -f backend

## Run load tests (Phase 2.6)

python backend\tests\load\test_load_baseline.py

```text

---

## # #  Expected Improvements

## # # Stability

- Docker isolation prevents DLL crashes
- Gunicorn handles worker failures
- Auto-restart recovers from crashes
- Health checks detect issues early

## # # Performance

- Gunicorn workers handle concurrent requests
- Nginx caching reduces latency
- Keep-alive connections reduce overhead
- Static file serving offloaded to Nginx

## # # Security

- HTTPS encryption
- Rate limiting
- Non-root container user
- Network isolation
- Secret management

## # # Observability

- Prometheus metrics scraping
- Grafana real-time dashboards
- Structured logging
- Health check monitoring

---

## # #  Why This Solves Backend Stability Issues

## # # Current Problem: Flask Dev Server + Model Loading

- Single-threaded dev server
- No automatic restart
- Background threading issues
- DLL loading conflicts

## # # Production Solution: Gunicorn + Docker

- Multi-worker process model
- Worker recycling after failures
- Proper signal handling
- Isolated environment (no DLL conflicts)
- Health checks trigger restart

**Expected Result**: Backend will remain stable during model loading and under load.

---

## # #  Timeline

| Hour | Task                          | Description                 |
| ---- | ----------------------------- | --------------------------- |
| 1-2  | Dockerfile & .dockerignore    | Production container setup  |
| 2-3  | docker-compose.production.yml | Multi-service orchestration |
| 3-4  | Gunicorn + Nginx config       | WSGI server + reverse proxy |
| 4-5  | Health checks & persistence   | Monitoring + backups        |
| 5-6  | Environment & secrets         | Configuration management    |
| 6-7  | Deployment scripts            | Automation                  |
| 7-8  | Testing & documentation       | Validation + guides         |

**Total**: 8 hours (1 day)

---

## # #  Next Steps After Phase 2.7

Once production deployment is complete:

1. **Return to Phase 2.6** - Run load tests in production environment

2. **Phase 2.8** - Complete documentation and demo

3. **Phase 3** - AI Agent integration (from audit recommendations)

---

**Status**:  Ready to implement
**Blocking Issue**: Backend instability (will be resolved by production infrastructure)
**Time Investment**: 8 hours
**Expected Outcome**: Stable, secure, production-ready ORFEAS AI 2D→3D Studio

# PHASE 4.9 - PRODUCTION DEPLOYMENT GUIDE

## Overview

This guide covers deploying the BOB AI containerized system to production with comprehensive validation.

**Status:** In-Progress (Phase 4.9)
**Duration:** ~4-6 hours
**Risk Level:** Low (all components tested in Phase 4.8)

## Architecture

```
Production Environment
├── API Service (Port 5000)
│   ├── Flask application
│   ├── Health checks
│   └── Search/Discovery endpoints
│
├── Monitoring Service (Port 8000)
│   ├── Prometheus metrics
│   ├── Health dashboards
│   └── Performance tracking
│
└── Persistent Storage
    ├── Models volume
    ├── Output data
    ├── Logs
    └── Upload staging
```

## Pre-Deployment Checklist

Before deploying, verify:

- [ ] Phase 4.8 Docker validation complete (all 50+ tests passing)
- [ ] docker-compose.production.yml validated
- [ ] All environment variables defined
- [ ] SSL certificates ready (if needed)
- [ ] Backup strategy in place
- [ ] Monitoring dashboards configured
- [ ] Runbook documentation complete

## Deployment Steps

### Step 1: Environment Setup (15 minutes)

```bash
# 1. Set production environment variables
$env:FLASK_ENV = 'production'
$env:PYTHONUNBUFFERED = '1'
$env:DEVICE = 'cuda'  # or 'cpu'
$env:GPU_MEMORY_LIMIT = '0.8'

# 2. Verify Docker is running
docker version

# 3. Verify docker-compose is available
docker-compose version

# 4. Navigate to project directory
cd c:\Users\johng\Documents\oscar
```

### Step 2: Build Production Image (20 minutes)

```bash
# Build Docker image for production
cd backend
python docker_build.py

# Verify image was created
docker images | grep bob-ai

# Expected output:
# bob-ai              latest    <image-id>  <size>
```

### Step 3: Production Smoke Tests (10 minutes)

```bash
# Start containers using production configuration
docker-compose -f docker-compose.production.yml up -d

# Wait for services to stabilize (30 seconds)
Start-Sleep -Seconds 30

# Run smoke tests
python test_phase4_production.py

# Expected: All tests passing, >95% success rate
```

### Step 4: Performance Validation (15 minutes)

```bash
# Run performance validation
python performance_validation.py

# Expected output:
# ✅ API: /health - Average: XX.Xms (SLA: <100ms) ✓
# ✅ API: /api/search - Average: XX.Xms (SLA: <100ms) ✓
# ✅ All SLAs met!
```

### Step 5: Health Checks & Monitoring (10 minutes)

```bash
# Check API health endpoint
curl http://localhost:5000/health

# Expected:
# {"status": "healthy", "timestamp": "2025-01-15T10:30:00Z"}

# Check monitoring endpoint
curl http://localhost:8000/health

# Expected:
# {"status": "healthy"}

# Verify metrics are being collected
curl http://localhost:8000/metrics

# Should contain prometheus metrics
```

### Step 6: System Health Verification (10 minutes)

```bash
# Check Docker container status
docker ps

# Expected: Both containers running
# CONTAINER ID  IMAGE      COMMAND           STATUS
# <id1>         bob-ai     python main.py    Up X minutes
# <id2>         bob-ai     python phase4...  Up X minutes

# Check container logs
docker logs <api-container-id> --tail 20

# Check monitoring logs
docker logs <monitoring-container-id> --tail 20

# Verify no errors in logs
```

### Step 7: Comprehensive Testing (20 minutes)

```bash
# Run full test suite
python -m pytest backend/tests/ -v

# Expected: All tests passing

# Run specific test suites
python -m pytest backend/tests/unit/ -v
python -m pytest backend/tests/integration/ -v

# Run Docker tests
python test_phase4_docker.py

# Run production tests
python test_phase4_production.py

# Run performance tests
python performance_validation.py
```

## Deployment Verification

### Endpoint Validation

**API Endpoints** (should all respond with 200):

```bash
# Core health check
GET http://localhost:5000/health

# Search endpoint
GET http://localhost:5000/api/search?q=test

# Disciplines endpoint
GET http://localhost:5000/api/disciplines

# Metrics summary
GET http://localhost:5000/api/metrics/summary
```

**Monitoring Endpoints** (should all respond with 200):

```bash
# Monitoring health
GET http://localhost:8000/health

# Prometheus metrics
GET http://localhost:8000/metrics

# Full system health
GET http://localhost:8000/api/health/full

# System metrics
GET http://localhost:8000/api/health/system

# Dependencies
GET http://localhost:8000/api/health/dependencies
```

### Performance Verification

All endpoints should meet these SLAs:

| Metric | SLA | Target |
|--------|-----|--------|
| Average Response Time | <100ms | ✓ |
| 95th Percentile | <150ms | ✓ |
| 99th Percentile | <200ms | ✓ |
| Success Rate | >99% | ✓ |
| Availability | 99.9% | ✓ |

### Health Checks

System performs automatic health checks every 30 seconds:

```bash
# View health check results in container logs
docker logs <container-id> | grep "health"

# Health check includes:
# - API endpoint responsiveness
# - Database connectivity
# - Memory usage
# - CPU utilization
# - Disk space
# - Docker daemon status
```

## Rollback Procedures

### Quick Rollback (if issues occur)

```bash
# Stop production containers
docker-compose -f docker-compose.production.yml down

# Restore from previous image (if one exists)
docker pull bob-ai:previous
docker tag bob-ai:previous bob-ai:latest

# Restart with previous version
docker-compose -f docker-compose.production.yml up -d
```

### Full Rollback to Previous Deployment

```bash
# List Docker images with timestamps
docker images --no-trunc

# Stop current deployment
docker-compose -f docker-compose.production.yml down

# Switch to previous image
docker run -d --name bob-ai-api -p 5000:5000 bob-ai:v4.8.0

# Verify it's running
curl http://localhost:5000/health
```

## Monitoring in Production

### Key Metrics to Monitor

**API Metrics:**

- Request count per endpoint
- Response time distribution (p50, p95, p99)
- Error rate
- Success rate

**System Metrics:**

- CPU utilization
- Memory usage
- Disk I/O
- GPU utilization (if using GPU)

**Application Metrics:**

- Active connections
- Model load time
- Search latency
- Generation latency

### Viewing Metrics

```bash
# All metrics in Prometheus format
curl http://localhost:8000/metrics | grep -E "^bob_ai"

# Summary metrics
curl http://localhost:8000/api/metrics/summary | python -m json.tool

# System health
curl http://localhost:8000/api/health/system | python -m json.tool

# Recent logs
curl http://localhost:8000/api/logs/recent?lines=50 | python -m json.tool
```

## Troubleshooting

### Issue: Services Won't Start

```bash
# Check if ports are in use
netstat -ano | findstr :5000
netstat -ano | findstr :8000

# Kill processes using those ports (if needed)
taskkill /PID <pid> /F

# Check Docker daemon is running
docker ps

# Check Docker resources
docker system df
```

### Issue: Performance Below SLA

```bash
# Check resource usage
docker stats

# Check if container is being throttled
docker inspect <container-id> | grep -A 10 "MemoryStats"

# Increase resource limits in docker-compose.production.yml
# Then restart services

# Monitor performance in real-time
python performance_validation.py
```

### Issue: High Error Rate

```bash
# Check container logs for errors
docker logs <container-id> --tail 100

# Check specific endpoint that's failing
curl -v http://localhost:5000/api/failing-endpoint

# Check if dependencies are available
curl http://localhost:8000/api/health/dependencies

# Restart the service
docker-compose -f docker-compose.production.yml restart
```

### Issue: Health Checks Failing

```bash
# Check container health status
docker ps --format "table {{.Names}}\t{{.Status}}"

# View health check logs
docker inspect <container-id> | grep -A 20 "Health"

# Manually verify endpoints
curl http://localhost:5000/health
curl http://localhost:8000/health

# Increase health check grace period if needed
# Edit docker-compose.production.yml:
# healthcheck:
#   test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
#   interval: 30s
#   timeout: 10s
#   retries: 3
#   start_period: 60s  # Increase this if needed
```

## Post-Deployment Tasks

### Documentation

- [ ] Update deployment runbook with actual deployment details
- [ ] Document any custom configuration
- [ ] Record baseline performance metrics
- [ ] Update team wiki/documentation

### Monitoring Setup

- [ ] Configure monitoring dashboards
- [ ] Set up alerting rules
- [ ] Verify log aggregation
- [ ] Test alert notifications

### Backup Configuration

- [ ] Verify backup strategy is active
- [ ] Test backup restoration
- [ ] Document backup location
- [ ] Schedule regular backup tests

### Access Control

- [ ] Verify only authorized personnel can access production
- [ ] Set up API key management
- [ ] Configure CORS if needed
- [ ] Enable rate limiting if needed

## Success Criteria

✅ Deployment is successful when:

1. **All smoke tests pass** - No API errors, all endpoints accessible
2. **Performance SLAs met** - <100ms average, <150ms p95
3. **Health checks passing** - All 9 health check types passing
4. **High availability** - >99% uptime, zero unplanned restarts
5. **Monitoring active** - All 30+ metrics being collected
6. **Logs flowing** - All logs aggregated and searchable
7. **No errors** - Application logs contain no errors or warnings
8. **Documentation complete** - Runbooks updated, team informed

## Next Steps

After successful deployment:

1. Monitor system performance for 24 hours
2. Collect baseline metrics for comparison
3. Update deployment documentation with lessons learned
4. Plan Phase 4 Complete (end-to-end validation)
5. Set up continuous deployment (CI/CD) pipeline

## Support & Escalation

**Level 1 - Application Issues:**

- Check application logs
- Restart affected service
- Review recent deployments

**Level 2 - Infrastructure Issues:**

- Check Docker/container status
- Verify network connectivity
- Check resource availability

**Level 3 - Production Crisis:**

- Execute rollback procedure
- Notify stakeholders
- Begin incident investigation

---

**Document Version:** 1.0.0
**Last Updated:** 2025-01-15
**Status:** Production-Ready
**Phase:** 4.9 - Production Deployment

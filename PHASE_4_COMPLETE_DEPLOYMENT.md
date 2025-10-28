# Phase 4 Complete: Production Deployment & Operations Guide

**BOB AI v10.0 - Enterprise Deployment Manual**

Status: Production-Ready
Version: 1.0.0
Last Updated: October 28, 2025

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Production Deployment](#production-deployment)
4. [Scaling & Load Balancing](#scaling--load-balancing)
5. [Health Monitoring](#health-monitoring)
6. [Maintenance Procedures](#maintenance-procedures)
7. [Disaster Recovery](#disaster-recovery)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Single-Command Deployment

```powershell
# Production deployment (Windows)
docker-compose -f docker-compose.production.yml up -d

# Verify deployment
curl http://localhost:5000/health
curl http://localhost:8000/health
```

### System Verification

```powershell
# Check all services running
docker ps | grep orfeas

# View logs
docker-compose -f docker-compose.production.yml logs -f backend

# Health check
docker-compose -f docker-compose.production.yml exec backend curl http://localhost:5000/health
```

---

## Pre-Deployment Checklist

### Infrastructure Requirements

**Hardware Specifications:**

| Component | Minimum | Recommended | Maximum |
|-----------|---------|-------------|---------|
| CPU Cores | 4 | 8 | 16 |
| RAM | 8GB | 16GB | 32GB |
| Storage | 50GB | 100GB | 500GB |
| Network | 100Mbps | 1Gbps | 10Gbps |

**Docker Requirements:**

- Docker Desktop 4.0+
- Docker Compose 2.0+
- Windows 10/11 Pro or Enterprise (Hyper-V support)
- WSL 2 backend configured
- Minimum 4GB allocated to Docker

**Network Requirements:**

- Firewall rules: Ports 5000 (API), 8000 (Monitoring), 3000 (Frontend)
- Outbound HTTPS (443) for external API calls
- Internal DNS resolution
- NTP time synchronization

**Security Prerequisites:**

- SSL/TLS certificates for production domain
- Environment secrets configured (API keys, credentials)
- Database backups configured
- Log rotation enabled

### Pre-Deployment Tasks

**1. Environment Configuration**

```powershell
# Create .env.production file
$env:DEVICE = 'cuda'
$env:XFORMERS_DISABLED = '1'
$env:ORT_TENSORRT_UNAVAILABLE = '1'
$env:FLASK_ENV = 'production'
$env:LOG_LEVEL = 'INFO'
$env:ENABLE_MONITORING = 'true'

# Secure secrets
$env:API_KEY = '<secure-key-here>'
$env:DATABASE_URL = '<secure-db-url>'
```

**2. Database Preparation**

```powershell
# Initialize database
docker-compose -f docker-compose.production.yml exec backend python -c "
from app import db
db.create_all()
print('Database initialized')
"

# Verify database
docker-compose -f docker-compose.production.yml exec backend python -c "
from app import db
result = db.session.execute('SELECT COUNT(*) FROM information_schema.tables')
print(f'Tables created: {result.scalar()}')
"
```

**3. Storage Preparation**

```powershell
# Create data directories
$dataDirs = @(
    './data/models',
    './data/uploads',
    './data/cache',
    './data/backups',
    './logs'
)

foreach ($dir in $dataDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

Write-Host "Data directories created"
```

**4. Certificate Installation**

```powershell
# Copy SSL certificates
Copy-Item -Path "C:\certs\*.crt" -Destination "./certs/" -Force
Copy-Item -Path "C:\certs\*.key" -Destination "./certs/" -Force

# Verify certificate validity
# (Requires openssl - available via WSL or Git Bash)
# openssl x509 -in ./certs/server.crt -text -noout
```

---

## Production Deployment

### Deployment Phases

#### Phase 1: Infrastructure Setup (15 minutes)

```powershell
# Step 1: Verify Docker resources
docker stats --no-stream | Select-Object -First 5

# Step 2: Build production images
docker-compose -f docker-compose.production.yml build --no-cache

# Step 3: Verify image sizes
docker images | grep orfeas

# Expected output:
# orfeas-backend          latest          2.5GB
# orfeas-monitoring       latest          1.8GB
# orfeas-frontend         latest          0.8GB
```

#### Phase 2: Container Startup (10 minutes)

```powershell
# Step 1: Start services (detached)
docker-compose -f docker-compose.production.yml up -d

# Step 2: Wait for startup (monitor logs)
for ($i = 0; $i -lt 60; $i++) {
    $backend = docker ps --filter "name=orfeas-backend" --quiet
    if ($backend) {
        Write-Host "Backend container running"
        break
    }
    Write-Host "Waiting for backend startup... ($i/60)"
    Start-Sleep -Seconds 1
}

# Step 3: Verify all services
docker-compose -f docker-compose.production.yml ps
```

#### Phase 3: Health Verification (15 minutes)

```powershell
# Step 1: API health check
$apiHealth = curl -s http://localhost:5000/health | ConvertFrom-Json
Write-Host "API Status: $($apiHealth.status)"

# Step 2: Monitoring health check
$monHealth = curl -s http://localhost:8000/health | ConvertFrom-Json
Write-Host "Monitoring Status: $($monHealth.status)"

# Step 3: Component verification
$components = @('api', 'monitoring', 'database', 'cache')
foreach ($component in $components) {
    $response = curl -s "http://localhost:8000/api/health/$component"
    Write-Host "$component : $response"
}
```

#### Phase 4: Performance Validation (15 minutes)

```powershell
# Step 1: Run baseline test
python backend/test_phase4_production.py

# Step 2: Monitor metrics
curl http://localhost:8000/metrics | Select-String "duration_seconds" -Context 2

# Step 3: Verify SLAs
# Expected:
# - p50 latency: <50ms
# - p95 latency: <100ms
# - p99 latency: <200ms
# - Success rate: >99.5%
```

### Deployment Validation

**Successful Deployment Indicators:**

- ✓ All containers running (docker ps shows 3 containers)
- ✓ API responding with 200 OK (curl /health)
- ✓ Monitoring collecting metrics (curl /metrics)
- ✓ Database initialized (verified tables exist)
- ✓ All tests passing (test_phase4_production.py)
- ✓ Performance within SLA (<100ms p95)
- ✓ Logs show no errors (check docker logs)

**Post-Deployment Checklist:**

```powershell
# Create post-deployment validation script
@"
# Deployment Validation
Date: $(Get-Date)
Deployment Version: 1.0.0

Services Running:
$(docker-compose -f docker-compose.production.yml ps)

API Health:
$(curl -s http://localhost:5000/health)

Monitoring Health:
$(curl -s http://localhost:8000/health)

Disk Usage:
$(docker exec orfeas-backend du -sh /data)

Memory Usage:
$(docker stats --no-stream orfeas-backend)
"@ | Out-File -Path "./logs/deployment_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
```

---

## Scaling & Load Balancing

### Horizontal Scaling

**Multi-Instance Deployment:**

```yaml
# docker-compose.production.yml (modified for scaling)
version: '3.8'

services:
  nginx:
    image: nginx:latest
    ports:
      - "5000:5000"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend-1
      - backend-2
      - backend-3

  backend-1:
    build: ./backend
    environment:
      - INSTANCE_ID=1
    expose:
      - "5000"

  backend-2:
    build: ./backend
    environment:
      - INSTANCE_ID=2
    expose:
      - "5000"

  backend-3:
    build: ./backend
    environment:
      - INSTANCE_ID=3
    expose:
      - "5000"

  redis:
    image: redis:latest
    ports:
      - "6379:6379"

  postgres:
    image: postgres:latest
    environment:
      - POSTGRES_DB=orfeas
```

**Nginx Load Balancing Configuration:**

```nginx
upstream backend {
    least_conn;
    server backend-1:5000;
    server backend-2:5000;
    server backend-3:5000;
}

server {
    listen 5000;
    server_name _;

    location / {
        proxy_pass http://backend;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /health {
        access_log off;
        proxy_pass http://backend/health;
    }
}
```

**Deployment Script:**

```powershell
# Scale deployment
param([int]$Instances = 3)

$compose = @"
version: '3.8'
services:
  backend-1: { image: orfeas-backend, expose: ['5000'] }
"@

for ($i = 2; $i -le $Instances; $i++) {
    $compose += "`n  backend-$i`: { image: orfeas-backend, expose: ['5000'] }"
}

$compose | Out-File -Path "./docker-compose.scale.yml"
docker-compose -f ./docker-compose.scale.yml up -d
```

### Vertical Scaling

**Resource Limits Configuration:**

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G
```

---

## Health Monitoring

### Real-Time Monitoring

**Prometheus Metrics:**

```powershell
# Access Prometheus UI
# http://localhost:9090

# Query examples:
# - Request latency: histogram_quantile(0.95, rate(request_duration_seconds_bucket[5m]))
# - Error rate: rate(requests_total{status=~"5.."}[5m])
# - Container memory: container_memory_usage_bytes{name="orfeas-backend"}
```

**Health Check Endpoints:**

| Endpoint | Interval | Timeout | Purpose |
|----------|----------|---------|---------|
| `/health` | 30s | 5s | API liveness |
| `/health/ready` | 30s | 5s | Readiness check |
| `/metrics` | 60s | 10s | Prometheus metrics |
| `/api/health/full` | 5m | 15s | Comprehensive check |

### Alert Thresholds

**Critical Alerts (Page On-Call):**

```
- API latency p99 > 500ms
- Error rate > 5%
- Container CPU > 90% sustained
- Disk usage > 90%
- Database connection pool exhausted
```

**Warning Alerts (Create ticket):**

```
- API latency p95 > 200ms
- Error rate > 1%
- Container memory > 80%
- Disk usage > 80%
- Slow query detected (>1s)
```

### Monitoring Dashboard

**Key Metrics to Track:**

1. **Performance**
   - Request latency (p50, p95, p99)
   - Request throughput (req/s)
   - Error rate (%)
   - Database query time (ms)

2. **Resource Usage**
   - CPU usage (%)
   - Memory usage (GB)
   - Disk I/O (MB/s)
   - Network I/O (Mbps)

3. **Business Metrics**
   - Active users
   - Requests per user
   - API calls per minute
   - Feature usage breakdown

---

## Maintenance Procedures

### Scheduled Maintenance

**Daily Tasks (Automated):**

```powershell
# Task: Log rotation
Get-ChildItem -Path "./logs" -Filter "*.log" |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) } |
    Remove-Item

# Task: Cache cleanup
docker-compose exec redis redis-cli FLUSHDB

# Task: Database maintenance
docker-compose exec postgres vacuumdb -d orfeas -U postgres
```

**Weekly Tasks (Manual):**

```powershell
# 1. Full backup
.\scripts\backup_full.ps1

# 2. Performance analysis
python backend/analyze_performance.py

# 3. Log analysis
Get-Content "./logs/error.log" |
    Select-String "ERROR" |
    Sort-Object |
    Get-Unique
```

**Monthly Tasks (Manual):**

```powershell
# 1. Security audit
.\scripts\security_audit.ps1

# 2. Capacity planning
python backend/analyze_capacity.py

# 3. Documentation update
# Review and update deployment guide
```

### Database Maintenance

**Backup Procedures:**

```powershell
function Backup-Database {
    param([string]$BackupPath = "./data/backups")

    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $filename = "orfeas_backup_$timestamp.sql"

    docker-compose exec postgres pg_dump -U postgres orfeas |
        Out-File -Path "$BackupPath/$filename"

    Write-Host "Backup created: $filename"
}

# Run backup
Backup-Database
```

**Restore Procedures:**

```powershell
function Restore-Database {
    param([string]$BackupFile)

    Get-Content $BackupFile |
        docker-compose exec -T postgres psql -U postgres

    Write-Host "Restore completed"
}

# Restore from backup
Restore-Database "./data/backups/orfeas_backup_20251028_120000.sql"
```

---

## Disaster Recovery

### Backup Strategy

**RPO/RTO Targets:**

| Component | RPO | RTO | Strategy |
|-----------|-----|-----|----------|
| Database | 1 hour | 15 min | Automated hourly backups |
| Application | 24 hours | 5 min | Blue-green deployment |
| Configuration | Immediate | 1 min | Version control |
| Logs | 24 hours | 30 min | Centralized logging |

**Backup Implementation:**

```powershell
# Automated backup schedule
$trigger = New-JobTrigger -Daily -At 2:00AM
$action = New-ScheduledJobOption -RunElevated
$job = Register-ScheduledJob `
    -Name "DailyDatabaseBackup" `
    -Trigger $trigger `
    -ScriptBlock { Backup-Database } `
    -ScheduledJobOption $action
```

### Failover Procedures

**Active-Passive Failover:**

```powershell
# Health check every 30 seconds
while ($true) {
    $primary = curl -s http://primary.example.com/health

    if (-not $primary) {
        Write-Host "Primary down, activating secondary"

        # Promote secondary to primary
        docker-compose -f docker-compose.secondary.yml up -d

        # Update DNS/routing
        Update-DnsRecord -Name "api.example.com" -Target "secondary-ip"
    }

    Start-Sleep -Seconds 30
}
```

### Disaster Recovery Drills

**Monthly DR Test Schedule:**

```powershell
# Test 1: Database recovery
Backup-Database
# Delete database
docker-compose exec postgres psql -c "DROP DATABASE orfeas;"
# Restore from backup
Restore-Database "./data/backups/latest.sql"
# Verify data integrity
python backend/verify_database.py
```

---

## Troubleshooting

### Common Issues & Solutions

**Issue 1: API responding slowly**

```powershell
# Diagnose
docker exec orfeas-backend ps aux
docker stats orfeas-backend

# Solutions
# 1. Increase container memory
docker-compose down
# Edit docker-compose.yml - increase memory limit
docker-compose -f docker-compose.production.yml up -d

# 2. Check database performance
docker-compose exec postgres explain analyze SELECT * FROM large_table;

# 3. Enable caching
curl -X POST http://localhost:5000/api/cache/enable
```

**Issue 2: High memory usage**

```powershell
# Diagnose
docker exec orfeas-backend python -c "import tracemalloc; tracemalloc.start()"

# Solution options
# 1. Reduce cache size
# 2. Implement memory pooling
# 3. Add garbage collection
# 4. Scale horizontally
```

**Issue 3: Database connection pool exhausted**

```powershell
# Diagnose
docker-compose exec postgres SELECT count(*) FROM pg_stat_activity;

# Solution
# 1. Increase pool size in config
# 2. Identify long-running queries
SELECT query, now() - query_start AS duration FROM pg_stat_activity;

# 3. Kill idle connections
SELECT pg_terminate_backend(pid) FROM pg_stat_activity
WHERE idle_in_transaction AND now() - query_start > interval '1 hour';
```

**Issue 4: Disk space running out**

```powershell
# Diagnose
docker exec orfeas-backend df -h

# Solutions
# 1. Delete old logs
Remove-Item "./logs/*.log" -Include *.log |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) }

# 2. Clear cache
redis-cli FLUSHALL

# 3. Archive old backups
Move-Item "./data/backups/*.sql" -Destination "./archive/" -Filter *.sql
```

**Issue 5: Certificate expiration warning**

```powershell
# Check certificate expiration
openssl x509 -in ./certs/server.crt -noout -dates

# Renew certificate (example with Let's Encrypt)
certbot renew --cert-name api.example.com

# Copy new certificate
Copy-Item "C:\Program Files (x86)\certbot\live\api.example.com\*.pem" -Destination "./certs/"

# Restart services
docker-compose -f docker-compose.production.yml restart
```

### Performance Tuning

**Database Query Optimization:**

```powershell
# Enable query logging
docker-compose exec postgres psql -d orfeas -c "
    ALTER SYSTEM SET log_min_duration_statement = 1000;
    SELECT pg_reload_conf();
"

# Analyze query performance
docker-compose exec postgres EXPLAIN ANALYZE SELECT * FROM disciplines LIMIT 100;

# Create indexes for frequently queried columns
docker-compose exec postgres psql -d orfeas -c "
    CREATE INDEX idx_disciplines_name ON disciplines (name);
    CREATE INDEX idx_disciplines_category ON disciplines (category);
"
```

**Cache Configuration:**

```powershell
# Optimize Redis
docker-compose exec redis redis-cli CONFIG SET maxmemory 2gb
docker-compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru

# Monitor Redis
docker-compose exec redis redis-cli INFO memory
```

---

## Appendix: Commands Reference

```powershell
# Deployment
docker-compose -f docker-compose.production.yml up -d
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml ps

# Logs
docker-compose logs -f backend
docker-compose logs --tail=100 backend
docker-compose logs backend --since 1h

# Health
curl http://localhost:5000/health
curl http://localhost:8000/health
curl http://localhost:8000/metrics

# Database
docker-compose exec postgres psql -d orfeas -U postgres
docker-compose exec postgres pg_dump -U postgres orfeas > backup.sql

# Backups
Backup-Database
Restore-Database "./backup.sql"

# Metrics
docker stats
docker top orfeas-backend
```

---

**End of Deployment Guide**

For questions or issues: Refer to troubleshooting section or contact operations team.

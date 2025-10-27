# BOB AI v8.0 - Deployment Guide

**Version:** 8.0.0 | **Status:** Production | **Last Updated:** October 27, 2025

## Deployment Checklist

- [ ] System Requirements Verified
- [ ] Python Environment Configured
- [ ] Dependencies Installed
- [ ] Configuration Files Set
- [ ] Module Discovery Tested
- [ ] All Tests Passing
- [ ] Performance Verified
- [ ] Documentation Reviewed
- [ ] Logging Configured
- [ ] Monitoring Active
- [ ] Rollback Plan Ready

---

## System Requirements

### Minimum Requirements

- **Python:** 3.10 or higher
- **OS:** Linux, macOS, or Windows
- **Disk:** 500MB free space
- **Memory:** 2GB RAM
- **Network:** Internet connection for initialization (optional)

### Production Requirements

- **Python:** 3.11+ recommended
- **OS:** Linux (Ubuntu 20.04+) or Windows Server 2019+
- **Disk:** 1GB free space
- **Memory:** 4GB+ RAM
- **Network:** Dedicated connectivity
- **Monitoring:** New Relic, Datadog, or Prometheus

---

## Installation

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd oscar/backend
```

### Step 2: Create Virtual Environment

**Linux/macOS:**

```bash
python3.11 -m venv venv
source venv/bin/activate
```

**Windows:**

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt --upgrade
```

### Step 4: Verify Installation

```bash
python -c "from bob_ai_v8_loader import BobAIV8ModuleLoader; print('OK')"
```

---

## Configuration

### Environment Variables

Create `.env` file in backend directory:

```bash
# Logger configuration
BOB_AI_LOG_LEVEL=INFO
BOB_AI_LOG_FILE=./logs/bob_ai.log

# Performance
BOB_AI_CACHE_ENABLED=true
BOB_AI_CACHE_SIZE=1000

# Module loader
BOB_AI_BACKEND_PATH=./backend
BOB_AI_AUTO_RELOAD=false

# Features
BOB_AI_PROFILING_ENABLED=false
BOB_AI_STRICT_VALIDATION=true

# Production
FLASK_ENV=production
DEBUG=false
WORKERS=4
```

### Load Environment

```bash
# Linux/macOS
export $(cat .env | xargs)

# Windows PowerShell
Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*[^#]*=') {
        $name, $value = $_ -split '=', 2
        [Environment]::SetEnvironmentVariable($name.Trim(), $value.Trim())
    }
}
```

---

## Module Discovery & Validation

### Validate All Modules

```bash
python -m pytest backend/bob_ai_v8_test_suite_comprehensive.py -v
```

**Expected output:**

```
======================== 50 passed in 2.5s =========================
```

### Test Integration

```bash
python -m pytest backend/bob_ai_v8_cross_discipline_tests.py -v
```

**Expected output:**

```
======================== 21 passed in 0.9s =========================
```

### Module Discovery Check

```python
from bob_ai_v8_loader import BobAIV8ModuleLoader

loader = BobAIV8ModuleLoader()
loaded, failed, errors = loader.load_all_modules()
print(f"Loaded: {loaded}, Failed: {failed}")

status = loader.get_status_report()
print(f"Status: {status}")
```

---

## Performance Validation

### Run Performance Profiler

```bash
python backend/bob_ai_v8_performance_optimizer.py
```

**Expected targets:**

- Bootstrap: <500ms ✓
- Cross-Discipline: <50ms ✓
- Batch (10 ops): <1000ms ✓

### Performance Monitoring

```python
from bob_ai_v8_performance_optimizer import PerformanceProfiler

profiler = PerformanceProfiler()
report = profiler.generate_report()
print(report)
```

---

## Deployment Options

### Option 1: Docker Deployment

**Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/

ENV BOB_AI_LOG_LEVEL=INFO
ENV FLASK_ENV=production

CMD ["python", "backend/main.py"]
```

**Build and run:**

```bash
docker build -t bob-ai-v8 .
docker run -p 5000:5000 bob-ai-v8
```

### Option 2: Systemd Service (Linux)

**Create `/etc/systemd/system/bob-ai.service`:**

```ini
[Unit]
Description=BOB AI v8.0 Service
After=network.target

[Service]
Type=simple
User=bobai
WorkingDirectory=/opt/bob-ai
Environment="FLASK_ENV=production"
ExecStart=/opt/bob-ai/venv/bin/python backend/main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**

```bash
sudo systemctl enable bob-ai
sudo systemctl start bob-ai
sudo systemctl status bob-ai
```

### Option 3: Manual Deployment

```bash
# 1. Navigate to deployment directory
cd /opt/bob-ai

# 2. Create virtual environment
python3.11 -m venv venv

# 3. Activate and install
source venv/bin/activate
pip install -r requirements.txt

# 4. Start application
nohup python backend/main.py > bob_ai.log 2>&1 &

# 5. Verify running
curl http://localhost:5000/health
```

---

## Health Checks

### API Health Endpoint

```bash
curl http://localhost:5000/health
```

**Expected response:**

```json
{
  "status": "healthy",
  "uptime_seconds": 1234,
  "loaded_modules": 27,
  "failed_modules": 0,
  "cache_hits": 1024,
  "cache_misses": 56
}
```

### Readiness Check

```bash
curl http://localhost:5000/ready
```

**Expected response:**

```json
{
  "ready": true,
  "modules_loaded": 27,
  "bootstrap_time_ms": 245,
  "timestamp": "2025-10-27T21:10:00Z"
}
```

### Metrics Endpoint

```bash
curl http://localhost:5000/metrics
```

Returns Prometheus metrics (if ENABLE_MONITORING=true)

---

## Logging Configuration

### Log Levels

```python
import logging

logger = logging.getLogger('bob_ai_v8')

# File handler (INFO and above)
file_handler = logging.FileHandler('logs/bob_ai.log')
file_handler.setLevel(logging.INFO)

# Console handler (WARNING and above)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
```

### Log Locations

```
logs/
├── bob_ai.log          # Main application log
├── modules.log         # Module loading logs
├── performance.log     # Performance metrics
└── errors.log          # Error log
```

---

## Monitoring

### Key Metrics

1. **Bootstrap Time:** <500ms target
2. **Module Load Success:** >95% success rate
3. **API Response Time:** <200ms p99
4. **Memory Usage:** <500MB baseline
5. **Cache Hit Rate:** >70%

### Prometheus Configuration

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'bob-ai'
    static_configs:
      - targets: ['localhost:5000']
    metrics_path: '/metrics'
```

### Alerting Rules

```yaml
groups:
  - name: bob_ai_alerts
    rules:
      - alert: HighBootstrapTime
        expr: bob_ai_bootstrap_time_ms > 600
        for: 1m

      - alert: ModuleLoadFailure
        expr: bob_ai_failed_modules > 0
        for: 5m

      - alert: HighMemoryUsage
        expr: process_resident_memory_bytes > 1000000000
        for: 5m
```

---

## Backup & Recovery

### Backup Procedure

```bash
# Backup module knowledge bases
tar -czf bob_ai_backup_$(date +%Y%m%d).tar.gz backend/

# Store in safe location
mv bob_ai_backup_*.tar.gz /mnt/backups/
```

### Recovery Procedure

```bash
# 1. Stop service
systemctl stop bob-ai

# 2. Restore backup
tar -xzf /mnt/backups/bob_ai_backup_20251027.tar.gz

# 3. Verify integrity
python -m pytest backend/bob_ai_v8_test_suite_comprehensive.py

# 4. Restart service
systemctl start bob-ai

# 5. Verify health
curl http://localhost:5000/health
```

---

## Scaling

### Horizontal Scaling

Deploy multiple instances behind load balancer:

```yaml
# Load Balancer Configuration (nginx)
upstream bob_ai_cluster {
    server 192.168.1.10:5000;
    server 192.168.1.11:5000;
    server 192.168.1.12:5000;
}

server {
    listen 80;
    location / {
        proxy_pass http://bob_ai_cluster;
    }
}
```

### Vertical Scaling

Increase resources on single instance:

```bash
# Increase worker processes
export WORKERS=8

# Increase cache size
export BOB_AI_CACHE_SIZE=5000

# Restart service
systemctl restart bob-ai
```

---

## Troubleshooting

### Module Load Failures

```python
loader = BobAIV8ModuleLoader()
loaded, failed, errors = loader.load_all_modules()

if failed > 0:
    for module, error in errors.items():
        print(f"ERROR: {module}: {error}")
```

### Performance Issues

```bash
# Profile bootstrap
python backend/bob_ai_v8_performance_optimizer.py

# Check memory usage
ps aux | grep python

# Monitor load
top -u bobai
```

### API Not Responding

```bash
# Check service status
systemctl status bob-ai

# View recent logs
tail -f logs/bob_ai.log

# Test connectivity
curl -v http://localhost:5000/health
```

---

## Rollback Procedure

### Quick Rollback

```bash
# 1. Stop current version
systemctl stop bob-ai

# 2. Switch to previous version
cd /opt/bob-ai
git checkout previous-version-tag

# 3. Reactivate venv and install
source venv/bin/activate
pip install -r requirements.txt

# 4. Start service
systemctl start bob-ai

# 5. Verify
curl http://localhost:5000/health
```

### Full Rollback

```bash
# Restore from backup
tar -xzf /mnt/backups/bob_ai_backup_previous.tar.gz

# Run tests
pytest backend/bob_ai_v8_test_suite_comprehensive.py

# Restart
systemctl restart bob-ai
```

---

## Production Checklist

**Pre-Launch:**

- [ ] All 50+ tests passing
- [ ] Performance targets met (<500ms bootstrap)
- [ ] Security audit completed
- [ ] Load testing passed (min 100 concurrent)
- [ ] Backup procedure tested
- [ ] Monitoring configured and verified
- [ ] Documentation reviewed by team
- [ ] Rollback plan tested

**Post-Launch:**

- [ ] Health check running continuously
- [ ] Logs being aggregated and monitored
- [ ] Metrics tracked (bootstrap, response time, module load)
- [ ] On-call rotation established
- [ ] Post-mortem process ready
- [ ] Update process documented

---

## Support

For deployment issues:

1. Check `BOB_AI_V8_TROUBLESHOOTING.md`
2. Review logs: `tail -f logs/bob_ai.log`
3. Run validation: `python -m pytest backend/bob_ai_v8_*_tests.py`
4. Contact: <devops@example.com>

---

## Version History

| Version | Release Date | Key Changes |
|---------|-------------|-------------|
| 8.0.0 | 2025-10-27 | Production release, 14 disciplines, 50+ tests |
| 7.9.0 | 2025-10-20 | Beta release, 10 disciplines |
| 7.5.0 | 2025-10-01 | Initial alpha, 5 disciplines |

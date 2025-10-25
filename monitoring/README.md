# 📊 ORFEAS AI - Monitoring Setup Guide

**Version:** 1.0.0
**Last Updated:** October 25, 2025

---

## 📋 Overview

This directory contains monitoring dashboards and configuration for tracking
ORFEAS AI optimization performance with Prometheus and Grafana.

### Key Metrics Tracked

- **Progressive Rendering** - Stage latencies (LOW/MEDIUM/HIGH)
- **Cache Performance** - Hit rate, memory usage, entry count
- **GPU Utilization** - Utilization %, VRAM usage, temperature
- **Batch Processing** - Concurrent jobs, batch size, queue depth
- **Rate Limiting** - Requests by tier, blocked requests
- **Compression** - Savings by encoding type (gzip/brotli)
- **WebSocket** - Event rate, throttled events, connected clients
- **Model Quantization** - Usage by mode (FP32/FP16/INT8/adaptive)
- **API Response Times** - P50, P95, P99 latencies
- **Error Rates** - 4xx, 5xx, 429 responses

---

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Prometheus (included in docker-compose.yml)
- Grafana (included in docker-compose.yml)

### Step 1: Start Monitoring Stack

```powershell
# Start Prometheus + Grafana
docker-compose up -d prometheus grafana

# Verify services
docker ps | Select-String "prometheus|grafana"
```

### Step 2: Import Grafana Dashboard

1. Open Grafana: <http://localhost:3000>
2. Login: admin / admin (change on first login)
3. Navigate: Dashboards → Import
4. Upload file: `monitoring/dashboards/orfeas-optimizations.json`
5. Select Prometheus datasource
6. Click Import

### Step 3: Verify Metrics

```powershell
# Check Prometheus is scraping
curl http://localhost:9090/targets

# View raw metrics from backend
curl http://localhost:5000/metrics
```

---

## 📂 Directory Structure

```text
monitoring/
├── dashboards/
│   └── orfeas-optimizations.json   # Grafana dashboard
├── prometheus/
│   └── prometheus.yml              # Prometheus config
├── alerts/
│   └── orfeas-alerts.yml          # Alert rules
└── README.md                       # This file
```

---

## 🔧 Configuration

### Prometheus Configuration

Create `monitoring/prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'orfeas-production'
    environment: 'production'

scrape_configs:
  - job_name: 'orfeas-backend'
    static_configs:
      - targets: ['backend:5000']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

### Alert Rules

Create `monitoring/alerts/orfeas-alerts.yml`:

```yaml
groups:
  - name: orfeas_optimizations
    interval: 30s
    rules:
      # High GPU temperature
      - alert: HighGPUTemperature
        expr: orfeas_gpu_temperature_celsius > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "GPU temperature is high"
          description: "GPU temperature is {{ $value }}°C (threshold: 85°C)"

      # High error rate
      - alert: HighErrorRate
        expr: rate(orfeas_requests_total{status=~"5.."}[5m]) > 1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High server error rate"
          description: "Error rate is {{ $value }} req/sec"

      # Low cache hit rate
      - alert: LowCacheHitRate
        expr: |
          rate(orfeas_cache_hits_total[5m]) /
          rate(orfeas_cache_requests_total[5m]) * 100 < 15
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Cache hit rate is low"
          description: "Cache hit rate is {{ $value }}% (threshold: 15%)"

      # High P95 latency
      - alert: HighLatency
        expr: |
          histogram_quantile(0.95,
            rate(orfeas_request_duration_seconds_bucket{
              endpoint="/api/generate-3d/progressive"
            }[5m])
          ) > 20
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High API latency"
          description: "P95 latency is {{ $value }}s (threshold: 20s)"

      # GPU VRAM nearly full
      - alert: HighVRAMUsage
        expr: |
          orfeas_gpu_memory_used_bytes /
          orfeas_gpu_memory_total_bytes * 100 > 90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "GPU VRAM usage is high"
          description: "VRAM usage is {{ $value }}% (threshold: 90%)"
```

---

## 📊 Dashboard Panels

### Overview Row

- **Requests/sec** - Current request rate
- **GPU Utilization** - Real-time GPU usage
- **Cache Hit Rate** - Percentage of cached responses
- **Concurrent Jobs** - Active GPU jobs

### Progressive Rendering

- **Stage Latencies** - P50 and P95 for LOW/MEDIUM/HIGH
- Shows improvement from baseline (60s → 0.5s/15s/60s)

### Cache Performance

- **Cache Hits/Misses** - Rate over time
- **Hit Rate %** - Trending cache efficiency
- **Memory Usage** - Cache size and entry count

### GPU Metrics

- **Utilization & VRAM** - GPU usage and memory
- **Temperature** - GPU temperature monitoring
- **Batch Processing** - Concurrent jobs, batch size, queue depth

### Rate Limiting

- **Requests by Tier** - FREE/BASIC/PREMIUM/ENTERPRISE
- **Blocked Requests** - 429 rate limit responses

### Compression

- **Bytes/sec** - Uncompressed vs gzip vs brotli
- **Savings %** - Compression effectiveness

### WebSocket

- **Event Rate** - Events sent per second
- **Throttled Events** - Events batched/delayed
- **Connected Clients** - Active WebSocket connections

### Model Quantization

- **Usage by Mode** - Pie chart (FP32/FP16/INT8/adaptive)

### API Response Times

- **Latency** - P50, P95, P99 for all endpoints
- **Comparison** - Progressive vs standard generation

### Error Tracking

- **5xx Errors** - Server errors
- **429 Rate Limited** - Rate limit blocks
- **4xx Errors** - Client errors

---

## 🔔 Alerting

### Slack Integration

1. Create Slack webhook: <https://api.slack.com/messaging/webhooks>
2. Update Grafana alert notification channel:
   - Type: Slack
   - Webhook URL: Your webhook URL
   - Channel: #orfeas-alerts

### Email Alerts

1. Configure SMTP in Grafana:
   - Edit: /etc/grafana/grafana.ini
   - Section: [smtp]
   - Add: host, user, password

2. Create email notification channel:
   - Type: Email
   - Addresses: <ops@example.com>

### PagerDuty Integration

1. Create PagerDuty integration key
2. Add notification channel:
   - Type: PagerDuty
   - Integration Key: Your key

---

## 📈 Metrics Collection

### Backend Integration

Metrics are automatically collected from `backend/prometheus_metrics.py`:

```python
from prometheus_metrics import get_metrics

metrics = get_metrics()

# Track progressive rendering stage
metrics.track_progressive_stage('low', duration=0.5)

# Track cache hit
metrics.track_cache_request(hit=True)

# Update GPU stats
metrics.update_gpu_stats(
    utilization=75.0,
    memory_used=12*1024**3,
    memory_total=24*1024**3,
    temperature=65.0
)

# Track rate limiting
metrics.track_rate_limit(tier='BASIC', blocked=False)
```

### Metrics Endpoint

Prometheus scrapes: `http://localhost:5000/metrics`

Example output:

```text
# HELP orfeas_requests_total Total HTTP requests
# TYPE orfeas_requests_total counter
orfeas_requests_total{endpoint="/api/generate-3d/progressive",method="POST",status="200"} 1234

# HELP orfeas_cache_hits_total Total cache hits
# TYPE orfeas_cache_hits_total counter
orfeas_cache_hits_total 345

# HELP orfeas_gpu_utilization_percent GPU utilization percentage
# TYPE orfeas_gpu_utilization_percent gauge
orfeas_gpu_utilization_percent 75.2
```

---

## 🧪 Testing

### Generate Test Metrics

```powershell
# Generate progressive rendering requests
for ($i=1; $i -le 10; $i++) {
    curl -X POST http://localhost:5000/api/generate-3d/progressive `
         -F "image=@test.jpg" `
         -F "quality=7"
    Start-Sleep -Seconds 2
}

# Check metrics updated
curl http://localhost:5000/metrics | Select-String "orfeas_progressive"
```

### Load Testing

```powershell
# Run Locust load test
locust -f load/locustfile.py --host http://localhost:5000

# Open http://localhost:8089
# Set: 10 users, 2 spawn rate, 5 min duration

# Monitor in Grafana dashboard
# Open: http://localhost:3000
```

---

## 📊 Performance Baselines

### Pre-Optimization

| Metric | Baseline |
|--------|----------|
| Response Time (P95) | 124s |
| First Result | 60s |
| GPU Utilization | 20% |
| Concurrent Jobs | 3-4 |
| Cache Hit Rate | 0% |

### Post-Optimization Targets

| Metric | Target |
|--------|--------|
| Response Time (P95) | < 20s |
| First Result | < 1s |
| GPU Utilization | 60-80% |
| Concurrent Jobs | 10-15 |
| Cache Hit Rate | 25-30% |

---

## 🔍 Troubleshooting

### Prometheus Not Scraping

```powershell
# Check Prometheus targets
curl http://localhost:9090/targets

# Check backend metrics endpoint
curl http://localhost:5000/metrics

# Check Prometheus logs
docker logs prometheus
```

### Grafana Dashboard Not Loading

```powershell
# Check Grafana datasource
# Grafana → Configuration → Data Sources → Prometheus
# URL should be: http://prometheus:9090

# Test connection
# Click "Save & Test"

# Check Grafana logs
docker logs grafana
```

### Missing Metrics

```powershell
# Verify metrics are being generated
curl http://localhost:5000/metrics | Select-String "orfeas_"

# Check backend logs
Get-Content backend\logs\backend_requests.log -Tail 50

# Restart backend
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
cd backend
python main.py
```

---

## 📚 Additional Resources

- **Prometheus Docs:** <https://prometheus.io/docs/>
- **Grafana Docs:** <https://grafana.com/docs/>
- **PromQL Guide:** <https://prometheus.io/docs/prometheus/latest/querying/basics/>
- **Dashboard Design:** <https://grafana.com/docs/grafana/latest/dashboards/>

---

## 🎯 Next Steps

1. **Deploy Monitoring Stack**
   - Start Prometheus + Grafana
   - Import dashboard

2. **Verify Metrics Collection**
   - Check /metrics endpoint
   - Verify Prometheus scraping

3. **Configure Alerts**
   - Set up Slack/email notifications
   - Test alert rules

4. **Baseline Performance**
   - Run load tests
   - Capture baseline metrics

5. **Deploy Optimizations**
   - Follow PRODUCTION_ROLLOUT_PLAN.md
   - Monitor metrics at each phase

---

**Document Version:** 1.0.0
**Last Updated:** October 25, 2025
**Maintainer:** ORFEAS AI Monitoring Team

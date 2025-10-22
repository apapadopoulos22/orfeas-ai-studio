# Phase 2.5: Monitoring Stack Implementation Plan

**Start Date**: January 2025 (Day 2)
**Duration**: 2 days

## # # Status**:**IN PROGRESS

---

## # #  Objectives

Add comprehensive monitoring infrastructure to ORFEAS with:

1. **Extended Prometheus Metrics** (15+ new metrics)

2. **Grafana Dashboards** (3 dashboards)

3. **Alert Rules** (10+ alerts)

4. **Docker Compose Stack** (Prometheus + Grafana + Alertmanager)
5. **Health Reports** (Automated daily summaries)

---

## # #  Current State Assessment

## # #  Already Implemented

**Files Found**:

- `backend/prometheus_metrics.py` (738 lines) - Basic metrics
- `backend/production_metrics.py` - Production metrics helpers
- `backend/monitoring.py` - Monitoring utilities

**Existing Metrics**:

- HTTP requests (total, duration, size)
- Error tracking (total, validation, rate limits)
- Text-to-image generations
- Basic system metrics

## # #  Needs Implementation

**Missing Metrics** (Priority for Phase 2.5):

1. GPU utilization % (CRITICAL)

2. VRAM usage/free MB (CRITICAL)

3. GPU temperature (HIGH)

4. 3D generation metrics (HIGH)
5. Pipeline stage durations (HIGH)
6. WebSocket connections (MEDIUM)
7. Progress update rate (MEDIUM)
8. Queue depth/wait time (MEDIUM)
9. Cache hit rate (MEDIUM)
10. Quality scores (MEDIUM)

**Missing Infrastructure**:

- Grafana dashboards (JSON configs)
- Prometheus alert rules (YAML)
- Docker Compose monitoring stack
- Alertmanager configuration

---

## # #  Implementation Tasks

## # # Task 1: Extend Prometheus Metrics (4 hours)

**Files to Modify**:

1. `backend/prometheus_metrics.py` - Add GPU and 3D generation metrics

2. `backend/gpu_manager.py` - Add GPU metrics collection

3. `backend/progress_tracker.py` - Add progress metrics export

4. `backend/websocket_manager.py` - Add WebSocket metrics

**New Metrics to Add**:

```python

## GPU Metrics (CRITICAL)

gpu_utilization_percent = Gauge('orfeas_gpu_utilization_percent', 'GPU utilization %', ['gpu_id'])
gpu_memory_used_mb = Gauge('orfeas_gpu_memory_used_mb', 'GPU memory used (MB)', ['gpu_id'])
gpu_memory_free_mb = Gauge('orfeas_gpu_memory_free_mb', 'GPU memory free (MB)', ['gpu_id'])
gpu_temperature_celsius = Gauge('orfeas_gpu_temperature_celsius', 'GPU temperature (°C)', ['gpu_id'])

## 3D Generation Metrics (HIGH)

generation_3d_total = Counter('orfeas_generation_3d_total', 'Total 3D generations', ['format', 'status'])
generation_3d_duration_seconds = Histogram('orfeas_generation_3d_duration_seconds', 'Time to generate 3D model', ['format'])
generation_3d_quality_score = Histogram('orfeas_generation_3d_quality_score', 'Quality score of generated model')

## Pipeline Stage Metrics (HIGH)

pipeline_stage_duration_seconds = Histogram('orfeas_pipeline_stage_duration_seconds', 'Pipeline stage duration', ['stage'])
pipeline_bottleneck_stage = Gauge('orfeas_pipeline_bottleneck_stage', 'Current bottleneck stage', ['stage'])

## WebSocket Metrics (MEDIUM)

websocket_connections_active = Gauge('orfeas_websocket_connections_active', 'Active WebSocket connections')
websocket_messages_sent_total = Counter('orfeas_websocket_messages_sent_total', 'WebSocket messages sent', ['event_type'])
websocket_progress_updates_total = Counter('orfeas_websocket_progress_updates_total', 'Progress updates sent')

## Queue Metrics (MEDIUM)

queue_depth = Gauge('orfeas_queue_depth', 'Number of jobs in queue')
queue_wait_time_seconds = Histogram('orfeas_queue_wait_time_seconds', 'Time jobs wait in queue')

## Cache Metrics (MEDIUM)

cache_hits_total = Counter('orfeas_cache_hits_total', 'Cache hits', ['cache_type'])
cache_misses_total = Counter('orfeas_cache_misses_total', 'Cache misses', ['cache_type'])
cache_size_bytes = Gauge('orfeas_cache_size_bytes', 'Cache size in bytes', ['cache_type'])

```text

---

## # # Task 2: Create Grafana Dashboards (3 hours)

**Dashboard 1: GPU Performance** (`monitoring/grafana_dashboards/orfeas_gpu_dashboard.json`)

**Panels**:

1. GPU Utilization % (Time series, 0-100%)

2. VRAM Usage (Time series, MB)

3. GPU Temperature (Time series, °C)

4. GPU Memory Trend (Area chart)
5. GPU Utilization Heatmap (Last 24h)

**Dashboard 2: 3D Generation Performance** (`monitoring/grafana_dashboards/orfeas_generation_dashboard.json`)

**Panels**:

1. Generation Time Distribution (Histogram)

2. Generations per Minute (Graph)

3. Success/Failure Rate (Pie chart)

4. Pipeline Stage Durations (Stacked area)
5. Quality Score Distribution (Histogram)
6. Average Generation Time Trend (Line graph)
7. Bottleneck Stages (Table)

**Dashboard 3: System Health** (`monitoring/grafana_dashboards/orfeas_system_dashboard.json`)

**Panels**:

1. HTTP Request Rate (Graph)

2. Error Rate % (Graph)

3. WebSocket Connections (Graph)

4. Queue Depth (Graph)
5. Cache Hit Rate % (Graph)
6. Response Time P50/P95/P99 (Graph)
7. Active Jobs (Gauge)
8. System Uptime (Stat)

---

## # # Task 3: Prometheus Alert Rules (2 hours)

**File**: `monitoring/prometheus/alert_rules.yml`

**Alert Categories**:

1. **GPU Alerts** (CRITICAL)

- GPU utilization >95% for 5 minutes
- GPU temperature >85°C
- VRAM usage >90%
- GPU not responding

1. **Performance Alerts** (HIGH)

- Generation time >120s (P95)
- Error rate >5%
- Queue depth >10 jobs
- Response time >30s (P95)

1. **Availability Alerts** (HIGH)

- Service down for >1 minute
- No successful generations in 10 minutes
- WebSocket connections dropped significantly

1. **Resource Alerts** (MEDIUM)

- CPU usage >80%
- Memory usage >90%
- Disk space <10%

**Example Alert**:

```yaml
groups:

  - name: orfeas_gpu_alerts

    interval: 30s
    rules:

      - alert: GPUUtilizationHigh

        expr: orfeas_gpu_utilization_percent > 95
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "GPU utilization very high"
          description: "GPU {{ $labels.gpu_id }} utilization is {{ $value }}%"

      - alert: GPUTemperatureHigh

        expr: orfeas_gpu_temperature_celsius > 85
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "GPU temperature critical"
          description: "GPU {{ $labels.gpu_id }} temperature is {{ $value }}°C"

```text

---

## # # Task 4: Docker Compose Monitoring Stack (2 hours)

**File**: `docker-compose-monitoring.yml`

**Services**:

```yaml
version: "3.8"

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: orfeas-prometheus
    ports:

      - "9090:9090"

    volumes:

      - ./monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./monitoring/prometheus/alert_rules.yml:/etc/prometheus/alert_rules.yml
      - prometheus-data:/prometheus

    command:

      - "--config.file=/etc/prometheus/prometheus.yml"
      - "--storage.tsdb.path=/prometheus"
      - "--storage.tsdb.retention.time=30d"

    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: orfeas-grafana
    ports:

      - "3000:3000"

    environment:

      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=orfeas_monitoring_2025
      - GF_USERS_ALLOW_SIGN_UP=false

    volumes:

      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
      - ./monitoring/grafana_dashboards:/var/lib/grafana/dashboards
      - grafana-data:/var/lib/grafana

    depends_on:

      - prometheus

    restart: unless-stopped

  alertmanager:
    image: prom/alertmanager:latest
    container_name: orfeas-alertmanager
    ports:

      - "9093:9093"

    volumes:

      - ./monitoring/alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml
      - alertmanager-data:/alertmanager

    command:

      - "--config.file=/etc/alertmanager/alertmanager.yml"
      - "--storage.path=/alertmanager"

    restart: unless-stopped

volumes:
  prometheus-data:
  grafana-data:
  alertmanager-data:

```text

---

## # # Task 5: Prometheus Configuration (1 hour)

**File**: `monitoring/prometheus/prometheus.yml`

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: "orfeas-production"
    environment: "production"

## Alertmanager configuration

alerting:
  alertmanagers:

    - static_configs:
        - targets: ["alertmanager:9093"]

## Load alert rules

rule_files:

  - "alert_rules.yml"

## Scrape configurations

scrape_configs:

  # ORFEAS Backend

  - job_name: "orfeas-backend"

    static_configs:

      - targets: ["host.docker.internal:5000"]

    metrics_path: "/metrics"
    scrape_interval: 10s

  # Prometheus itself

  - job_name: "prometheus"

    static_configs:

      - targets: ["localhost:9090"]

  # Node Exporter (optional - for host metrics)

  - job_name: "node"

    static_configs:

      - targets: ["node-exporter:9100"]

```text

---

## # # Task 6: Alertmanager Configuration (1 hour)

**File**: `monitoring/alertmanager/alertmanager.yml`

```yaml
global:
  resolve_timeout: 5m
  smtp_smarthost: "smtp.gmail.com:587"
  smtp_from: "orfeas-alerts@example.com"
  smtp_auth_username: "your-email@gmail.com"
  smtp_auth_password: "your-app-password"

## Alert routing

route:
  group_by: ["alertname", "cluster", "service"]
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: "default"

  routes:

    # Critical alerts - immediate notification

    - match:

        severity: critical
      receiver: "critical-alerts"
      group_wait: 0s
      repeat_interval: 1h

    # Warning alerts - grouped notification

    - match:

        severity: warning
      receiver: "warning-alerts"
      group_wait: 30s
      repeat_interval: 4h

## Alert receivers

receivers:

  - name: "default"

    email_configs:

      - to: "team@example.com"

        headers:
          Subject: "[ORFEAS] {{ .GroupLabels.alertname }}"

  - name: "critical-alerts"

    email_configs:

      - to: "oncall@example.com"

        headers:
          Subject: "[CRITICAL] ORFEAS: {{ .GroupLabels.alertname }}"

  - name: "warning-alerts"

    email_configs:

      - to: "team@example.com"

        headers:
          Subject: "[WARNING] ORFEAS: {{ .GroupLabels.alertname }}"

## Inhibition rules (suppress alerts)

inhibit_rules:

  # Suppress warning if critical alert is firing

  - source_match:

      severity: "critical"
    target_match:
      severity: "warning"
    equal: ["alertname", "cluster", "service"]

```text

---

## # # Task 7: Grafana Provisioning (1 hour)

**File**: `monitoring/grafana/provisioning/datasources/prometheus.yml`

```yaml
apiVersion: 1

datasources:

  - name: Prometheus

    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false

```text

**File**: `monitoring/grafana/provisioning/dashboards/dashboard.yml`

```yaml
apiVersion: 1

providers:

  - name: "ORFEAS Dashboards"

    orgId: 1
    folder: ""
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards

```text

---

## # #  Success Metrics

## # # Monitoring Coverage

- 15+ custom Prometheus metrics
- 3 Grafana dashboards
- 10+ alert rules
- Docker Compose stack deployed
- Metrics endpoint accessible at `/metrics`

## # # Dashboard Requirements

**GPU Dashboard**:

- Real-time GPU utilization graph
- VRAM usage trend (last 24h)
- Temperature monitoring
- Historical utilization heatmap

**Generation Dashboard**:

- Generation time distribution (histogram)
- Success/failure rate (pie chart)
- Pipeline stage breakdown (stacked area)
- Quality score trend

**System Dashboard**:

- Request rate and error rate
- WebSocket connection count
- Queue depth and wait time
- Cache hit rate %

## # # Alert Coverage

- GPU utilization >95% for 5min → Warning
- GPU temperature >85°C → Critical
- VRAM usage >90% → Warning
- Error rate >5% → Warning
- Service down >1min → Critical
- Queue depth >10 → Warning
- No generations 10min → Warning

---

## # #  Testing Strategy

## # # Test 1: Metrics Collection

```bash

## Start monitoring stack

docker-compose -f docker-compose-monitoring.yml up -d

## Verify Prometheus is scraping

curl http://localhost:9090/api/v1/targets

## Check metrics endpoint

curl http://localhost:5000/metrics | grep orfeas_

## Expected: 15+ orfeas_* metrics visible

```text

## # # Test 2: Dashboard Visualization

```bash

## Access Grafana

open http://localhost:3000

## Login: admin / orfeas_monitoring_2025

## Verify dashboards

## 1. ORFEAS GPU Performance

## 2. ORFEAS Generation Performance

## 3. ORFEAS System Health

## Expected: All panels showing data

```text

## # # Test 3: Alert Firing

```bash

## Trigger high GPU usage (simulation)

python test_gpu_alert.py

## Check Prometheus alerts

open http://localhost:9090/alerts

## Expected: GPUUtilizationHigh alert firing

```text

## # # Test 4: Load Test with Monitoring

```bash

## Run load test while monitoring

python test_load_with_monitoring.py

## Monitor in Grafana

## - Request rate increases

## - Generation time distribution updates

## - Queue depth fluctuates

## - Cache hit rate changes

## Expected: All metrics updating in real-time

```text

---

## # #  Timeline

**Day 1 (4 hours)**:

- Morning: Extend Prometheus metrics (GPU, 3D gen, WebSocket)
- Afternoon: Create Grafana dashboards (3 dashboards)

**Day 2 (4 hours)**:

- Morning: Prometheus alert rules + Docker Compose stack
- Afternoon: Testing, validation, documentation

---

## # #  Acceptance Criteria

Phase 2.5 is complete when:

1. 15+ custom Prometheus metrics implemented

2. 3 Grafana dashboards created and working

3. 10+ alert rules configured

4. Docker Compose monitoring stack deployed
5. All dashboards showing real data
6. Alerts firing correctly for simulated issues
7. Documentation complete (access URLs, credentials, troubleshooting)

---

## # #  Documentation Deliverables

1. **Monitoring Setup Guide** - How to deploy stack

2. **Metrics Reference** - All metrics explained

3. **Dashboard Guide** - How to use each dashboard

4. **Alert Runbook** - How to respond to each alert
5. **Troubleshooting Guide** - Common issues and fixes

---

## # # Status**:**READY TO START

**Priority**: HIGH
**Estimated Duration**: 2 days (8 hours)

---

_ORFEAS AI Project_
_ORFEAS AI 2D→3D Studio - Phase 2.5_
_Start Date: January 2025_

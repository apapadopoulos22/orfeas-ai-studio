# ORFEAS MONITORING VERIFICATION CHECKLIST

## # # [OK] Prerequisites

- [ ] Docker Desktop installed and running
- [ ] Backend server running (`python backend/main.py`)
- [ ] Monitoring stack deployed (`cd backend/monitoring_stack && docker-compose up -d`)

## # # [STATS] Verification Steps

## # # 1. Verify Prometheus (http://localhost:9090)

## # # Expected

- Web interface accessible at http://localhost:9090
- Status > Targets shows `orfeas` endpoint as UP
- Query `up{job="orfeas"}` returns value `1`

## # # Test Queries

```text

## Check if ORFEAS is up

up{job="orfeas"}

## Request rate (requests per second)

rate(orfeas_http_requests_total[5m])

## P95 response time

histogram_quantile(0.95, sum(rate(orfeas_http_request_duration_seconds_bucket[5m])) by (endpoint, le))

## GPU memory usage percentage

(orfeas_gpu_memory_used_bytes / orfeas_gpu_memory_total_bytes) * 100

## Generation success rate

sum(rate(orfeas_generation_success_total[5m])) / sum(rate(orfeas_generation_total[5m])) * 100

```text

## # # Verification Commands

```bash

## Check Prometheus container status

docker ps | grep prometheus

## Check Prometheus logs

docker logs monitoring_stack_prometheus_1

## Test Prometheus API

curl http://localhost:9090/api/v1/query?query=up

```text

---

## # # 2. Verify Grafana (http://localhost:3000)

## # # Default Credentials

- Username: `admin`
- Password: `admin` (will prompt to change on first login)

## # # Expected (2)

- Web interface accessible at http://localhost:3000
- Prometheus datasource configured and working
- ORFEAS Production Dashboard visible with 11 panels

## # # Dashboard Panels

1. Request Rate (requests/second) - Time series graph

2. Response Time P95 (milliseconds) - Time series with threshold

3. Generation Success Rate (%) - Time series with gauge

4. GPU Memory Usage (%) - Gauge with color thresholds
5. CPU Usage (%) - Time series graph
6. Active Jobs in Queue - Stat panel
7. Error Rate (5xx errors) - Time series with alert
8. Generation Duration Distribution - Heatmap
9. Current Active Generations - Stat panel
10. Memory Usage (RAM) - Time series graph
11. Prometheus Targets Status - Table

## # # Verification Steps

1. Login to Grafana

2. Navigate to Dashboards > ORFEAS AI Production Dashboard

3. Verify all panels are loading data (not showing "No data")

4. Check datasource: Configuration > Data Sources > Prometheus > Test
5. Verify alerts configured: Alerting > Alert Rules

## # # Verification Commands (2)

```bash

## Check Grafana container status

docker ps | grep grafana

## Check Grafana logs

docker logs monitoring_stack_grafana_1

## Test Grafana API

curl -u admin:admin http://localhost:3000/api/health

```text

---

## # # 3. Verify Metrics Endpoint (http://localhost:5000/metrics)

## # # Expected (3)

- Accessible at http://localhost:5000/metrics
- Returns Prometheus-formatted metrics
- Includes ORFEAS-specific metrics

## # # Sample Metrics

```text

## HELP orfeas_http_requests_total Total HTTP requests

## TYPE orfeas_http_requests_total counter

orfeas_http_requests_total{method="GET",endpoint="/api/health",status_code="200"} 1234.0

## HELP orfeas_http_request_duration_seconds HTTP request duration

## TYPE orfeas_http_request_duration_seconds histogram

orfeas_http_request_duration_seconds_bucket{endpoint="/api/health",le="0.1"} 1000.0
orfeas_http_request_duration_seconds_bucket{endpoint="/api/health",le="0.2"} 1200.0

## HELP orfeas_gpu_memory_used_bytes GPU memory used in bytes

## TYPE orfeas_gpu_memory_used_bytes gauge

orfeas_gpu_memory_used_bytes{device_id="0"} 2147483648.0

## HELP orfeas_generation_total Total generations

## TYPE orfeas_generation_total counter

orfeas_generation_total 567.0

## HELP orfeas_generation_success_total Successful generations

## TYPE orfeas_generation_success_total counter

orfeas_generation_success_total 543.0

```text

## # # Verification Commands (3)

```bash

## Check if backend server is running

curl http://localhost:5000/api/health

## Fetch metrics endpoint

curl http://localhost:5000/metrics

## Verify specific metric exists

curl http://localhost:5000/metrics | grep "orfeas_http_requests_total"

## Count total metrics exposed

curl -s http://localhost:5000/metrics | grep "^# HELP" | wc -l

```text

---

## # # 4. Verify Alertmanager (http://localhost:9093)

## # # Expected (4)

- Web interface accessible at http://localhost:9093
- Alert routing configured for email/Slack/webhook
- Active alerts visible if thresholds exceeded

## # # Verification Commands (4)

```bash

## Check Alertmanager container status

docker ps | grep alertmanager

## Check Alertmanager logs

docker logs monitoring_stack_alertmanager_1

## Test Alertmanager API

curl http://localhost:9093/api/v1/alerts

```text

---

## # # [LAB] End-to-End Test Scenario

## # # Test Flow

1. Start backend server: `python backend/main.py`

2. Start monitoring stack: `cd backend/monitoring_stack && docker-compose up -d`

3. Wait 30 seconds for stack initialization

4. Generate load: `pytest backend/tests/performance/test_response_times.py -v`
5. Check Prometheus: http://localhost:9090

- Query: `rate(orfeas_http_requests_total[1m])`
- Should show increasing request rate

6. Check Grafana: http://localhost:3000

- Dashboard should show real-time metrics
- Request Rate panel should show spikes
- Response Time panel should show latency

7. Check metrics endpoint: `curl http://localhost:5000/metrics`

- Should show updated counters and histograms

## # # Expected Results

- [OK] All containers running (4 total: prometheus, grafana, alertmanager, orfeas backend)
- [OK] Prometheus scraping metrics every 15 seconds
- [OK] Grafana dashboard updating every 5 seconds
- [OK] No errors in container logs
- [OK] All panels showing data (not "No data")
- [OK] Response times within SLA (P95 < 200ms)

---

## # #  Troubleshooting

## # # Issue: Prometheus shows target as DOWN

## # # Solution

```bash

## Check if backend server is running

curl http://localhost:5000/api/health

## Check Prometheus config

docker exec monitoring_stack_prometheus_1 cat /etc/prometheus/prometheus.yml

## Restart Prometheus

docker restart monitoring_stack_prometheus_1

```text

## # # Issue: Grafana shows "No data"

## # # Solution (2)

```bash

## Check datasource configuration

## Grafana UI: Configuration > Data Sources > Prometheus > Test

## Verify Prometheus URL (should be http://prometheus:9090)

## Check if data exists in Prometheus first

curl 'http://localhost:9090/api/v1/query?query=up'

## Restart Grafana

docker restart monitoring_stack_grafana_1

```text

## # # Issue: Metrics endpoint not accessible

## # # Solution (3)

```bash

## Check if backend server is running

ps aux | grep "python.*main.py"

## Check if port 5000 is in use

netstat -an | grep 5000

## Check backend logs

tail -f backend/logs/app.log

## Restart backend

python backend/main.py

```text

## # # Issue: Docker containers not starting

## # # Solution (4)

```bash

## Check Docker Desktop status

docker info

## Check container logs

docker logs monitoring_stack_prometheus_1
docker logs monitoring_stack_grafana_1

## Rebuild and restart

cd backend/monitoring_stack
docker-compose down
docker-compose up -d --build

## Check disk space

df -h

```text

---

## # # [METRICS] Performance Baselines

## # # Expected Metrics (No Load)

- Request Rate: 0-1 requests/second (health checks only)
- Response Time P95: < 50ms
- CPU Usage: < 10%
- Memory Usage: < 500MB
- GPU Memory: < 2GB (with model loaded)

## # # Expected Metrics (Under Load - 50 concurrent users)

- Request Rate: 50-100 requests/second
- Response Time P95: < 200ms (SLA target)
- Response Time P99: < 500ms (SLA target)
- CPU Usage: 30-60%
- Memory Usage: 1-2GB
- GPU Memory: 4-8GB (during generation)
- Error Rate: < 1%
- Success Rate: > 99%

---

## # # [OK] Final Verification Checklist

- [ ] Prometheus accessible and scraping metrics
- [ ] Grafana accessible with dashboard loaded
- [ ] All 11 dashboard panels showing data
- [ ] Metrics endpoint returning Prometheus-formatted data
- [ ] Alertmanager accessible and configured
- [ ] Backend server logs show no errors
- [ ] Performance tests pass with P95 < 200ms
- [ ] Unit tests pass (66+ tests)
- [ ] Integration tests pass (32+ tests)
- [ ] No memory leaks detected
- [ ] GPU metrics visible (if GPU available)
- [ ] Documentation updated with monitoring info

---

## # #  Additional Resources

## # # Prometheus Documentation

- Query Language: https://prometheus.io/docs/prometheus/latest/querying/basics/
- Best Practices: https://prometheus.io/docs/practices/naming/

## # # Grafana Documentation

- Dashboard Guide: https://grafana.com/docs/grafana/latest/dashboards/
- Alerting: https://grafana.com/docs/grafana/latest/alerting/

## # # ORFEAS Monitoring

- Monitoring Code: `backend/monitoring.py`
- Metrics Decorators: Applied to `backend/main.py`
- Dashboard JSON: `backend/monitoring_stack/grafana/provisioning/dashboards/dashboard.json`
- Docker Compose: `backend/monitoring_stack/docker-compose.yml`

---

## # # [TARGET] Success Criteria

## # # Monitoring is OPERATIONAL when

1. [OK] All 4 containers running (prometheus, grafana, alertmanager, backend)

2. [OK] Prometheus target shows UP status

3. [OK] Grafana dashboard displays real-time metrics

4. [OK] Metrics endpoint returns valid Prometheus data
5. [OK] Performance tests show P95 < 200ms
6. [OK] No critical errors in logs
7. [OK] Alert rules configured and testable
8. [OK] Documentation complete and accurate

---

**Last Updated:** 2024-01-XX
**ORFEAS Version:** 1.0.0
**Monitoring Stack Version:** Prometheus 2.45.0, Grafana 10.0.0

## # # ORFEAS AI

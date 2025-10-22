<!-- markdownlint-disable MD036 MD022 MD032 MD040 -->

# PHASE 4 QUICK REFERENCE - DEVELOPER GUIDE

## ORFEAS AI 2D→3D Studio - Phase 4 (99%+) Quick Integration

---

## 🚀 QUICK START (5 MINUTES)

### Import All Phase 4 Components

```python

## backend/main.py - Add these imports

from backend.advanced_gpu_optimizer import get_advanced_gpu_optimizer
from backend.performance_dashboard_realtime import get_dashboard
from backend.distributed_cache_manager import get_distributed_cache
from backend.predictive_performance_optimizer import get_predictive_optimizer
from backend.alerting_system import get_alerting_system, AlertSeverity
from backend.ml_anomaly_detector import get_anomaly_detector
from backend.distributed_tracing import get_tracing_system, TraceSpan

## Initialize systems

gpu_opt = get_advanced_gpu_optimizer()
dashboard = get_dashboard()
cache = get_distributed_cache()
predictor = get_predictive_optimizer()
alerts = get_alerting_system()
anomaly = get_anomaly_detector()
tracer = get_tracing_system()

```text

---

## 📡 API ENDPOINTS (Add to main.py)

### GPU Optimization

```python
@app.route('/api/gpu/profile')
def gpu_profile():
    """Get detailed GPU optimization report"""
    return jsonify(gpu_opt.get_optimization_report())

@app.route('/api/gpu/cleanup', methods=['POST'])
def gpu_cleanup():
    """Trigger aggressive GPU cleanup"""
    result = gpu_opt.aggressive_cleanup()
    return jsonify(result)

```text

### Caching

```python
@app.route('/api/cache/stats')
def cache_stats():
    """Get cache statistics"""
    return jsonify(cache.get_stats())

@app.route('/api/cache/clear', methods=['POST'])
def cache_clear():
    """Clear cache"""
    result = cache.clear()
    return jsonify(result)

```text

### Predictions

```python
@app.route('/api/predictions')
def get_predictions():
    """Get performance predictions"""
    # Collect current metrics
    metrics = {
        'gpu_memory': gpu_opt.get_detailed_memory_profile().allocated_mb,
        'cpu_usage': psutil.cpu_percent(),
        'cache_hit_rate': cache.get_stats()['hit_rate_percent'] / 100,
        'latency_ms': get_avg_latency(),
        'error_rate': get_error_rate()
    }
    report = predictor.generate_prediction_report(metrics)
    return jsonify(report)

```text

### Alerts

```python
@app.route('/api/alerts/active')
def active_alerts():
    """Get active alerts"""
    return jsonify({'alerts': alerts.get_active_alerts()})

@app.route('/api/alerts/history')
def alert_history():
    """Get alert history"""
    limit = request.args.get('limit', 100, type=int)
    return jsonify({'history': alerts.get_alert_history(limit)})

@app.route('/api/alerts/<alert_name>/acknowledge', methods=['POST'])
def ack_alert(alert_name):
    """Acknowledge an alert"""
    result = alerts.acknowledge_alert(alert_name)
    return jsonify({'acknowledged': result})

```text

### Anomalies

```python
@app.route('/api/anomalies')
def get_anomalies():
    """Get anomaly detection report"""
    metrics = collect_metrics()
    anomaly.detect_anomalies(metrics)
    report = anomaly.get_anomaly_report()
    return jsonify(report)

```text

### Tracing

```python
@app.route('/api/traces')
def list_traces():
    """List active and recent traces"""
    return jsonify({
        'active': tracer.get_active_traces(),
        'recent': tracer.get_completed_traces(limit=10),
        'stats': tracer.get_trace_statistics()
    })

@app.route('/api/traces/<trace_id>')
def get_trace(trace_id):
    """Get specific trace"""
    trace = tracer.get_trace(trace_id)
    return jsonify(trace.to_dict() if trace else {'error': 'not_found'})

```text

### Dashboard

```python
@app.route('/api/dashboard/summary')
def dashboard_summary():
    """Get dashboard summary"""
    return jsonify(dashboard.get_dashboard_summary())

```text

---

## 🔌 WEBSOCKET METRICS STREAMING

### Add WebSocket Endpoint

```python
from flask_sockets import Sockets

sockets = Sockets(app)

@sockets.route('/ws/metrics')
def metrics_stream(ws):
    """WebSocket stream for real-time metrics"""
    client_id = dashboard.subscribe()
    try:
        while True:
            # Get latest metrics
            summary = dashboard.get_dashboard_summary()

            # Send to client
            ws.send(json.dumps({
                'type': 'metrics_update',
                'timestamp': datetime.now().isoformat(),
                'data': summary
            }))

            time.sleep(1.0)  # Send every 1 second

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        dashboard.unsubscribe(client_id)

```text

---

## 📊 METRICS COLLECTION LOOP

### Add to your main event loop

```python
import asyncio
import psutil

async def collect_metrics_loop():
    """Continuously collect and broadcast metrics"""
    while True:
        try:
            # Start trace for metrics collection
            trace_id = tracer.start_trace("metrics_collection")

            # GPU metrics
            gpu_profile = gpu_opt.get_detailed_memory_profile()

            # Cache metrics
            cache_stats = cache.get_stats()

            # System metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            system_mem = psutil.virtual_memory()

            # Calculate application metrics
            latency = get_avg_response_time()  # Your function
            throughput = get_current_throughput()  # Your function
            error_rate = get_error_rate()  # Your function

            # Compile metrics
            metrics = {
                'gpu_memory': gpu_profile.allocated_mb,
                'gpu_memory_percent': (gpu_profile.allocated_mb / gpu_profile.total_mb * 100),
                'gpu_fragmentation': gpu_profile.fragmentation_ratio,
                'cpu_percent': cpu_percent,
                'system_memory_mb': system_mem.used / 1024 / 1024,
                'cache_hit_rate': cache_stats['hit_rate_percent'] / 100,
                'cache_miss_rate_percent': 100 - cache_stats['hit_rate_percent'],
                'latency_ms': latency,
                'throughput': throughput,
                'error_rate_percent': error_rate,
                'active_requests': get_active_request_count()
            }

            # Broadcast to dashboard
            await dashboard.broadcast_metrics(metrics)

            # Check alerts
            alerts.check_alerts(metrics)

            # Detect anomalies
            anomalies = anomaly.detect_anomalies(metrics)

            # Generate predictions
            predictor.add_metric_sample(metrics)

            # Log anomalies
            if anomalies:
                for anom in anomalies:
                    logger.warning(
                        f"Anomaly detected: {anom.metric} - {anom.description}"
                    )

            # End trace
            tracer.end_trace()

            # Wait 1 second before next collection
            await asyncio.sleep(1.0)

        except Exception as e:
            logger.error(f"Metrics collection error: {e}")
            await asyncio.sleep(1.0)

## Schedule the metrics loop

asyncio.create_task(collect_metrics_loop())

```text

---

## 🎯 ALERT CONFIGURATION

### Setup Alert Subscribers

```python
def on_critical_alert(alert_event):
    """Handle critical alerts"""
    logger.critical(f"CRITICAL ALERT: {alert_event['message']}")
    # Send notification (email, Slack, etc.)
    send_notification(alert_event)

def on_warning_alert(alert_event):
    """Handle warning alerts"""
    logger.warning(f"WARNING: {alert_event['message']}")

## Subscribe to alerts

alerts.subscribe(AlertSeverity.CRITICAL, on_critical_alert)
alerts.subscribe(AlertSeverity.WARNING, on_warning_alert)
alerts.subscribe(None, lambda e: log_all_alerts(e))  # All severities

```text

### Add Custom Alerts

```python
from backend.alerting_system import Alert, AlertSeverity

## Create custom alert

custom_alert = Alert(
    name="Memory Leak Detection",
    metric="memory_growth_rate",
    threshold=10.0,  # MB per minute
    severity=AlertSeverity.CRITICAL,
    message="Memory leak detected - growth rate too high",
    comparison=">",
    cooldown_seconds=600
)

## Register it

alerts.register_alert(custom_alert)

```text

---

## 🔍 ANOMALY DETECTION

### Using Anomaly Detector

```python

## Detect anomalies in metrics

anomalies = anomaly.detect_anomalies(metrics)

## Get detailed report

report = anomaly.get_anomaly_report()

print(f"Total anomalies: {report['total_anomalies']}")
print(f"Critical: {report['critical_anomalies']}")
print(f"System health: {report['system_health']}")

for anom in report['anomalies']:
    print(f"  - {anom['metric']}: {anom['description']}")
    print(f"    Severity: {anom['severity_percent']}%")
    print(f"    Action: {anom['suggested_action']}")

```text

---

## 📍 DISTRIBUTED TRACING

### Trace Individual Operations

```python

## Manual span management

trace_id = tracer.start_trace("api_request")
span_id = tracer.start_span("database_query", service="postgres")

try:
    # Do work
    result = db.query("SELECT * FROM users")

    # Add tags
    tracer.add_tag("rows_returned", len(result))

    # Add logs
    tracer.add_log("Query executed successfully", {
        'duration_ms': elapsed_time,
        'row_count': len(result)
    })

except Exception as e:
    tracer.end_span(status=SpanStatus.ERROR, error=str(e))
finally:
    tracer.end_span()

tracer.end_trace()

```text

### Using Context Manager (Recommended)

```python
from backend.distributed_tracing import TraceSpan, SpanStatus

## Automatic span management

with TraceSpan("fetch_users", service="api"):
    users = db.query("SELECT * FROM users")
    tracer.add_tag("count", len(users))
    # Automatically ends span on exit

## Access trace

trace_id = tracer._trace_context.trace_id
trace = tracer.get_trace(trace_id)
print(f"Trace duration: {trace.duration():.2f}ms")

```text

---

## 📈 PERFORMANCE PREDICTIONS

### Get Predictions

```python

## Add sample

predictor.add_metric_sample(metrics)

## Generate prediction

predictions = predictor.generate_prediction_report(metrics)

print(f"Memory prediction: {predictions['predictions'][0]['prediction']}")
print(f"Cache prediction: {predictions['predictions'][1]['prediction']}")
print(f"System health: {predictions['overall_system_health']}")
print(f"Top recommendation: {predictions['top_recommendation']}")

```text

---

## 🧪 LOAD TESTING

### Run Load Tests

```python
import asyncio
from backend.tests.integration.test_production_load import ProductionLoadTest

async def run_tests():
    tester = ProductionLoadTest('http://localhost:5000')

    # Load test
    await tester.run_load_test(duration_seconds=60, rps=20)

    # Stress test
    await tester.run_stress_test(max_rps=100)

    # Spike test
    await tester.run_spike_test(sustained_rps=20, spike_rps=100)

    # Save report
    tester.save_report('load_test_report.json')
    tester.print_summary()

asyncio.run(run_tests())

```text

---

## 📊 METRICS COLLECTION HELPERS

### Create Helper Functions

```python
def get_avg_response_time():
    """Get average response time from your monitoring"""
    # Implementation depends on your request tracking
    pass

def get_current_throughput():
    """Get current throughput (requests per second)"""
    # Calculate from request counter
    pass

def get_error_rate():
    """Get current error rate percentage"""
    # Calculate from error counter and total requests
    pass

def get_active_request_count():
    """Get number of active requests"""
    # Track from request context
    pass

def send_notification(alert_event):
    """Send alert notification"""
    # Email, Slack, webhook, etc.
    pass

def collect_metrics():
    """Collect all current metrics"""
    return {
        'gpu_memory': gpu_opt.get_detailed_memory_profile().allocated_mb,
        'cpu_usage': psutil.cpu_percent(),
        'cache_hit_rate': cache.get_stats()['hit_rate_percent'] / 100,
        'latency_ms': get_avg_response_time(),
        'error_rate': get_error_rate()
    }

```text

---

## 🔧 CONFIGURATION

### Optimizer Settings

```python

## GPU Optimizer

gpu_opt.set_config({
    'max_history_samples': 500,
    'fragmentation_warning_threshold': 0.30,
    'memory_pressure_threshold': 0.85,
    'critical_threshold': 0.95
})

## Dashboard

dashboard_config = {
    'max_history': 300,  # 5 minutes at 1-second intervals
    'update_interval_seconds': 1.0
}

## Cache

cache_endpoints = [
    'redis-node-1:6379',
    'redis-node-2:6379',
    'redis-node-3:6379'
]
cache = get_distributed_cache(cache_endpoints)

## Anomaly Detector

detector_config = {
    'lookback_samples': 300,
    'anomaly_threshold': 2.0  # Z-score
}

## Tracing

tracer_config = {
    'service_name': 'orfeas',
    'max_traces': 1000
}

```text

---

## ✅ TESTING CHECKLIST

Before deploying to production:

- [ ] All imports work without errors
- [ ] API endpoints respond correctly
- [ ] WebSocket metrics streaming works
- [ ] Alerts trigger on configured thresholds
- [ ] Anomalies detected in test data
- [ ] Predictions generated successfully
- [ ] Traces record correctly
- [ ] Load tests pass baseline
- [ ] Dashboard displays metrics
- [ ] Cache functions normally
- [ ] GPU optimization working
- [ ] No memory leaks detected

---

## 🐛 TROUBLESHOOTING

### WebSocket Connection Issues

```python

## Check if sockets library installed

pip install Flask-Sockets

## Verify endpoint

## Should be: ws://localhost:5000/ws/metrics (not http://)

```text

### Memory Issues

```python

## Check GPU memory

profile = gpu_opt.get_detailed_memory_profile()
print(f"GPU: {profile.allocated_mb}MB / {profile.total_mb}MB")

## Trigger cleanup

gpu_opt.aggressive_cleanup()

```text

### No Anomalies Detected

```python

## Need enough samples (min 10)

if len(anomaly.metric_history.get('metric_name', [])) < 10:
    print("Insufficient data for anomaly detection")

## Add more metrics

for i in range(20):
    anomaly.add_metric('cpu_usage', random.uniform(20, 80))

```text

### Alerts Not Triggering

```python

## Check if alert is enabled

for alert in alerts.alerts:
    print(f"{alert.name}: {'enabled' if alert.enabled else 'disabled'}")

## Check cooldown

if alert.cooldown_until and datetime.now() < alert.cooldown_until:
    print(f"Alert in cooldown until {alert.cooldown_until}")

```text

---

## 📚 DOCUMENTATION LINKS

- Full Phase 4 docs: `PHASE_4_DEPLOYMENT_COMPLETE_99_PERCENT.md`
- API specifications: See endpoint docstrings
- Configuration: Module-level config dicts
- Examples: This file

---

### Quick Reference Version 1.0 - October 20, 2025

### For Phase 4 (99%+) Deployment

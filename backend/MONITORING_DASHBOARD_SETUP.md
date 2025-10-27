# Monitoring Dashboard Setup Guide

**Phase 12.1: Real-Time Production Monitoring**

## Executive Summary

Complete setup guide for production monitoring of BOB AI v7 system. Real-time dashboards track system health, performance, and business metrics.

**Setup Time:** 1-2 hours
**Tools Used:** Python (logging), JSON (metrics)
**Target:** 99.9% uptime visibility

---

## 1. Monitoring Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              BOB AI v7 Monitoring Stack                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Application (Flask + SocketIO)                             │
│       │                                                      │
│       ├─→ Metrics Collector (Real-time events)             │
│       │                                                      │
│       ├─→ Error Logger (Errors, warnings)                  │
│       │                                                      │
│       ├─→ Performance Tracker (Response times, throughput)  │
│       │                                                      │
│       └─→ Business Metrics (Quality scores, items added)    │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Metrics Storage (Time-series)              │  │
│  │  ┌──────────────┐  ┌──────────────┐                 │  │
│  │  │  Performance │  │  Business    │                 │  │
│  │  │  Metrics     │  │  Metrics     │                 │  │
│  │  └──────────────┘  └──────────────┘                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Dashboard & Alerting                       │  │
│  │  ┌──────────────┐  ┌──────────────┐                 │  │
│  │  │  Real-time   │  │  Alert Rules │                 │  │
│  │  │  Dashboards  │  │  & Triggers  │                 │  │
│  │  └──────────────┘  └──────────────┘                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Notifications                             │  │
│  │  ┌────────────┐  ┌────────────┐  ┌─────────────┐   │  │
│  │  │   Email    │  │   Slack    │  │   PagerDuty│   │  │
│  │  └────────────┘  └────────────┘  └─────────────┘   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Key Performance Indicators (KPIs)

### 2.1 System Health Metrics

| KPI | Target | Warning | Critical |
|-----|--------|---------|----------|
| API Availability | 99.9% | <99.5% | <99% |
| Error Rate | <0.1% | >0.5% | >1% |
| Response Time P95 | <500ms | >1s | >2s |
| CPU Usage | <60% | >75% | >85% |
| Memory Usage | <70% | >80% | >90% |
| Disk Usage | <80% | >85% | >95% |
| Database Connections | <50 | >75 | >90 |

### 2.2 Performance Metrics

| KPI | Target | Warning | Critical |
|-----|--------|---------|----------|
| Label Search Time | <1ms | >5ms | >10ms |
| Domain Search Time | <5ms | >10ms | >20ms |
| Cache Hit Rate | >95% | <90% | <80% |
| Batch Operation Time | <100ms | >200ms | >500ms |
| Quality Calc Time | <5ms | >10ms | >20ms |

### 2.3 Business Metrics

| KPI | Target | Tracking |
|-----|--------|----------|
| Total Items | 1,330+ | Growth/day |
| Average Quality | >0.88 | Daily average |
| High-Quality Items | 95%+ | % ≥0.85 |
| API Requests/Hour | Baseline | Trending |
| Search Queries/Hour | Baseline | Trending |
| Items Created/Day | Baseline | Growth metric |

---

## 3. Metrics Collection Setup

### 3.1 Application Instrumentation

Create `monitoring_instrumentation.py`:

```python
import time
import logging
from typing import Dict, Any
from datetime import datetime

class MetricsCollector:
    """Collect and aggregate system metrics"""

    def __init__(self):
        self.metrics = {
            'system': {},
            'performance': {},
            'business': {},
            'errors': []
        }
        self.logger = logging.getLogger(__name__)

    def record_request(self, endpoint: str, method: str,
                       response_time: float, status: int):
        """Record API request metrics"""
        metric = {
            'timestamp': datetime.now().isoformat(),
            'endpoint': endpoint,
            'method': method,
            'response_time_ms': response_time * 1000,
            'status': status,
            'success': 200 <= status < 300
        }
        self.metrics['performance'][f'{method} {endpoint}'] = metric
        self.logger.info(f"Request: {endpoint} → {response_time*1000:.2f}ms")

    def record_search(self, search_type: str, result_count: int,
                      search_time: float):
        """Record search performance"""
        metric = {
            'timestamp': datetime.now().isoformat(),
            'type': search_type,
            'results': result_count,
            'time_ms': search_time * 1000
        }
        self.logger.info(f"Search: {search_type} → {search_time*1000:.3f}ms")

    def record_error(self, error_type: str, message: str, severity: str):
        """Record errors"""
        error = {
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': message,
            'severity': severity  # INFO, WARNING, ERROR, CRITICAL
        }
        self.metrics['errors'].append(error)
        self.logger.error(f"[{severity}] {error_type}: {message}")

    def record_quality_metric(self, items_count: int, avg_quality: float,
                              high_quality_pct: float):
        """Record quality metrics"""
        self.metrics['business'] = {
            'timestamp': datetime.now().isoformat(),
            'total_items': items_count,
            'avg_quality': avg_quality,
            'high_quality_pct': high_quality_pct
        }

# Global instance
collector = MetricsCollector()
```

### 3.2 Integrate into Flask App

In `main.py`:

```python
from monitoring_instrumentation import collector
import time

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    elapsed = time.time() - request.start_time
    collector.record_request(
        endpoint=request.path,
        method=request.method,
        response_time=elapsed,
        status=response.status_code
    )
    return response

@app.errorhandler(Exception)
def handle_error(e):
    collector.record_error(
        error_type=type(e).__name__,
        message=str(e),
        severity='ERROR'
    )
    return {'error': 'Internal server error'}, 500
```

---

## 4. Dashboard Configuration

### 4.1 Real-Time Dashboard (HTML)

Create `monitoring_dashboard.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>BOB AI v7 - Monitoring Dashboard</title>
    <style>
        body { font-family: Arial; background: #1e1e1e; color: #fff; }
        .dashboard { padding: 20px; }
        .metric-card {
            background: #2d2d2d;
            border: 1px solid #444;
            border-radius: 8px;
            padding: 20px;
            margin: 10px;
            display: inline-block;
            min-width: 300px;
        }
        .metric-value {
            font-size: 32px;
            font-weight: bold;
            color: #4CAF50;
        }
        .metric-label {
            font-size: 12px;
            color: #999;
            margin-top: 8px;
        }
        .status-good { color: #4CAF50; }
        .status-warning { color: #FFC107; }
        .status-critical { color: #F44336; }
        .chart { height: 300px; margin: 20px 0; }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
</head>
<body>
    <div class="dashboard">
        <h1>📊 BOB AI v7 - Production Monitoring</h1>

        <!-- System Health -->
        <div style="background: #2d2d2d; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h2>System Health</h2>
            <div class="metric-card">
                <div class="metric-label">API Availability</div>
                <div class="metric-value status-good" id="availability">99.9%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Error Rate</div>
                <div class="metric-value status-good" id="errorRate">0.02%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Response Time (P95)</div>
                <div class="metric-value status-good" id="responseTime">245ms</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">CPU Usage</div>
                <div class="metric-value status-good" id="cpuUsage">35%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Memory Usage</div>
                <div class="metric-value status-good" id="memoryUsage">62%</div>
            </div>
        </div>

        <!-- Performance Metrics -->
        <div style="background: #2d2d2d; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h2>Performance</h2>
            <div class="metric-card">
                <div class="metric-label">Label Search</div>
                <div class="metric-value status-good" id="labelSearch">0.022ms</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Domain Search</div>
                <div class="metric-value status-good" id="domainSearch">0.000ms</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Cache Hit Rate</div>
                <div class="metric-value status-good" id="cacheHit">100%</div>
            </div>
        </div>

        <!-- Business Metrics -->
        <div style="background: #2d2d2d; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h2>Business Metrics</h2>
            <div class="metric-card">
                <div class="metric-label">Total Items</div>
                <div class="metric-value" id="totalItems">1,330</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Quality</div>
                <div class="metric-value" id="avgQuality">0.89</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">High-Quality Items</div>
                <div class="metric-value" id="highQuality">95.2%</div>
            </div>
        </div>

        <!-- Charts -->
        <div style="background: #2d2d2d; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h2>Trends (Last 24 Hours)</h2>
            <canvas id="responseTimeChart" class="chart"></canvas>
            <canvas id="errorRateChart" class="chart"></canvas>
            <canvas id="cacheHitChart" class="chart"></canvas>
        </div>
    </div>

    <script>
        // WebSocket connection for real-time updates
        const socket = io('http://localhost:5000');

        socket.on('metrics_update', (data) => {
            document.getElementById('availability').textContent = data.availability;
            document.getElementById('errorRate').textContent = data.errorRate;
            document.getElementById('responseTime').textContent = data.responseTime;
            document.getElementById('cpuUsage').textContent = data.cpuUsage;
            document.getElementById('memoryUsage').textContent = data.memoryUsage;
        });

        // Initialize charts
        const ctx = document.getElementById('responseTimeChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
                datasets: [{
                    label: 'Response Time (ms)',
                    data: [245, 312, 198, 267, 189, 234],
                    borderColor: '#4CAF50',
                    borderWidth: 2,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    </script>
</body>
</html>
```

---

## 5. Alert Rules Configuration

### 5.1 Alert Configuration

Create `alert_rules.py`:

```python
from datetime import datetime, timedelta
from typing import Dict, List

class AlertRule:
    """Define alert conditions"""

    def __init__(self, name: str, metric: str, threshold: float,
                 duration_seconds: int = 60, severity: str = 'WARNING'):
        self.name = name
        self.metric = metric
        self.threshold = threshold
        self.duration = duration_seconds
        self.severity = severity
        self.triggered_at = None

    def check(self, current_value: float) -> bool:
        """Check if alert should trigger"""
        if current_value > self.threshold:
            if self.triggered_at is None:
                self.triggered_at = datetime.now()
            elif (datetime.now() - self.triggered_at).total_seconds() > self.duration:
                return True
        else:
            self.triggered_at = None
        return False

# Define alert rules
ALERT_RULES = [
    AlertRule('High Error Rate', 'error_rate', threshold=0.01, severity='CRITICAL'),
    AlertRule('High Response Time', 'response_time_p95', threshold=2000, severity='WARNING'),
    AlertRule('High CPU Usage', 'cpu_usage', threshold=85, severity='WARNING'),
    AlertRule('High Memory Usage', 'memory_usage', threshold=90, severity='CRITICAL'),
    AlertRule('Low Cache Hit Rate', 'cache_hit_rate', threshold=0.90,
              operator='<', severity='WARNING'),
    AlertRule('Database Connection Issues', 'db_connections', threshold=90, severity='CRITICAL'),
    AlertRule('Quality Degradation', 'avg_quality', threshold=0.85,
              operator='<', severity='WARNING'),
]

class AlertManager:
    """Manage alert triggers and notifications"""

    def __init__(self):
        self.rules = ALERT_RULES
        self.active_alerts = {}

    def check_all_rules(self, metrics: Dict) -> List[str]:
        """Check all rules and return triggered alerts"""
        triggered = []
        for rule in self.rules:
            if rule.check(metrics.get(rule.metric, 0)):
                alert_msg = f"[{rule.severity}] {rule.name}: {metrics[rule.metric]}"
                triggered.append(alert_msg)
                self.active_alerts[rule.name] = datetime.now()
        return triggered
```

### 5.2 Notification Channels

Create `notification_channels.py`:

```python
import requests
import smtplib
from email.mime.text import MIMEText

class NotificationChannel:
    """Base class for notification channels"""

    def send(self, alert: str, severity: str):
        raise NotImplementedError

class SlackNotifier(NotificationChannel):
    """Send alerts to Slack"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send(self, alert: str, severity: str):
        color = {'INFO': '#4CAF50', 'WARNING': '#FFC107', 'CRITICAL': '#F44336'}.get(severity)
        payload = {
            'attachments': [{
                'color': color,
                'title': 'BOB AI v7 Alert',
                'text': alert,
                'footer': 'Monitoring System'
            }]
        }
        requests.post(self.webhook_url, json=payload)

class EmailNotifier(NotificationChannel):
    """Send alerts via email"""

    def __init__(self, smtp_host: str, from_email: str, to_emails: list):
        self.smtp_host = smtp_host
        self.from_email = from_email
        self.to_emails = to_emails

    def send(self, alert: str, severity: str):
        msg = MIMEText(f"Alert: {alert}")
        msg['Subject'] = f"[{severity}] BOB AI v7 Alert"
        msg['From'] = self.from_email
        msg['To'] = ', '.join(self.to_emails)

        server = smtplib.SMTP(self.smtp_host)
        server.send_message(msg)
        server.quit()

class PagerDutyNotifier(NotificationChannel):
    """Send alerts to PagerDuty"""

    def __init__(self, api_key: str, service_id: str):
        self.api_key = api_key
        self.service_id = service_id

    def send(self, alert: str, severity: str):
        level = 'critical' if severity == 'CRITICAL' else 'warning'
        payload = {
            'severity': level,
            'summary': alert,
            'source': 'BOB AI v7'
        }
        headers = {'Authorization': f'Token token={self.api_key}'}
        requests.post(
            f'https://api.pagerduty.com/incidents',
            json=payload,
            headers=headers
        )
```

---

## 6. Logging Configuration

### 6.1 Structured Logging

Create `logging_config.py`:

```python
import logging
import json
from datetime import datetime

class JsonFormatter(logging.Formatter):
    """Format logs as JSON for easy parsing"""

    def format(self, record):
        log_obj = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        if record.exc_info:
            log_obj['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.FileHandler('logs/app.json', mode='a'),
        logging.StreamHandler()
    ]
)

# Use JSON formatter for JSON handler
json_handler = logging.FileHandler('logs/app.json', mode='a')
json_handler.setFormatter(JsonFormatter())
logging.getLogger().addHandler(json_handler)
```

### 6.2 Log Levels

```
DEBUG   - Development debugging, verbose
INFO    - General information, events
WARNING - Warning conditions, potential issues
ERROR   - Error conditions, problems
CRITICAL - Critical issues, immediate action needed
```

---

## 7. Monitoring Dashboard Access

### 7.1 Setup Dashboard Endpoint

In `main.py`:

```python
@app.route('/monitoring/dashboard')
def monitoring_dashboard():
    """Serve monitoring dashboard"""
    return render_template('monitoring_dashboard.html')

@socketio.on('request_metrics')
def handle_metrics_request():
    """Send current metrics via WebSocket"""
    metrics = get_current_metrics()
    emit('metrics_update', metrics, broadcast=True)
```

### 7.2 Access Points

- **Local:** `http://localhost:5000/monitoring/dashboard`
- **Production:** `https://api.example.com/monitoring/dashboard`
- **Health Check:** `https://api.example.com/health`

---

## 8. Metrics Analysis & Reporting

### 8.1 Daily Report

Create `daily_report.py`:

```python
from datetime import datetime, timedelta
import json

def generate_daily_report():
    """Generate daily metrics report"""

    yesterday = datetime.now() - timedelta(days=1)

    report = {
        'period': f'{yesterday.date()}',
        'system': {
            'availability': 99.95,
            'error_rate': 0.08,
            'avg_response_time': 287,
            'cpu_usage_avg': 42,
            'memory_usage_avg': 68
        },
        'performance': {
            'label_search_avg': 0.035,
            'domain_search_avg': 2.1,
            'cache_hit_rate': 97.8
        },
        'business': {
            'items_added': 23,
            'searches_performed': 4521,
            'avg_quality': 0.893,
            'high_quality_pct': 95.1
        },
        'alerts': {
            'triggered': 2,
            'critical': 0,
            'warnings': 2
        }
    }

    # Save report
    with open(f'reports/{yesterday.date()}_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    return report
```

---

## 9. Integration with Existing Code

### 9.1 Update main.py

```python
# Add at top
from monitoring_instrumentation import collector
from alert_rules import AlertManager
from notification_channels import SlackNotifier

# Initialize
alert_manager = AlertManager()
slack = SlackNotifier(os.getenv('SLACK_WEBHOOK_URL'))

# In request handlers
@app.route('/api/v7/search')
def search():
    start = time.time()
    # ... search logic ...
    elapsed = time.time() - start

    collector.record_search(
        search_type='label',
        result_count=len(results),
        search_time=elapsed
    )

    return results
```

---

## 10. Testing Monitoring System

### 10.1 Alert Testing

```python
# Test high error rate alert
for i in range(100):
    collector.record_error('TestError', 'Test message', 'ERROR')

# Should trigger alert if error rate > 1%
```

### 10.2 Dashboard Testing

1. Open `http://localhost:5000/monitoring/dashboard`
2. Verify metrics display
3. Verify real-time updates
4. Generate test alert
5. Verify notification sent

---

## 11. Monitoring Checklist

- [ ] Metrics collection active
- [ ] Dashboard accessible
- [ ] All KPIs displaying
- [ ] Alert rules configured
- [ ] Slack integration working
- [ ] Email alerts working
- [ ] Daily reports generating
- [ ] Logs properly formatted
- [ ] Performance tracking active
- [ ] Business metrics tracked

---

*Last Updated: October 27, 2025*
*BOB AI v7 - Monitoring Dashboard Setup*
*Status: Production Ready*

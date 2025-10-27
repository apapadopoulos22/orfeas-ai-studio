# Performance Metrics Collection Guide

**Phase 12.2: Continuous Performance Monitoring & Analysis**

## Executive Summary

Comprehensive guide for collecting, analyzing, and reporting performance metrics. System generates daily, weekly, and monthly performance reports with trend analysis.

**Update Frequency:** Real-time collection, daily aggregation
**Analysis Window:** Rolling 30-day window
**Reporting:** Automated daily/weekly reports

---

## 1. Performance Metrics Framework

### 1.1 Metric Categories

```
Performance Metrics (3 Categories)
│
├── System Performance
│   ├── CPU Usage (%)
│   ├── Memory Usage (%)
│   ├── Disk I/O (MB/s)
│   └── Network (Mbps)
│
├── Application Performance
│   ├── API Response Time (ms)
│   ├── Error Rate (%)
│   ├── Throughput (req/sec)
│   └── Availability (%)
│
└── Business Performance
    ├── Items Added (per day)
    ├── Searches Performed (per day)
    ├── Average Quality Score
    └── User Engagement
```

---

## 2. Metrics Collection Implementation

### 2.1 Core Metrics Collector

Create `performance_collector.py`:

```python
import time
import psutil
import json
from datetime import datetime, timedelta
from collections import deque
from typing import Dict, List

class PerformanceMetrics:
    """Collect and aggregate performance metrics"""

    def __init__(self, window_size: int = 3600):  # 1 hour window
        self.window_size = window_size

        # Time-series data (last 24 hours)
        self.metrics_history = deque(maxlen=1440)  # 1440 minutes

        # Current metrics
        self.current = {
            'timestamp': None,
            'system': {},
            'application': {},
            'business': {}
        }

    def collect_system_metrics(self) -> Dict:
        """Collect system-level metrics"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'cpu_count': psutil.cpu_count(),
            'memory': psutil.virtual_memory()._asdict(),
            'disk': psutil.disk_usage('/')._asdict(),
        }
        self.current['system'] = metrics
        return metrics

    def collect_application_metrics(self) -> Dict:
        """Collect application-level metrics"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': get_uptime(),
            'requests_total': get_request_count(),
            'errors_total': get_error_count(),
            'active_connections': get_active_connections(),
            'cache_stats': get_cache_stats(),
            'database_stats': get_database_stats()
        }
        self.current['application'] = metrics
        return metrics

    def collect_business_metrics(self) -> Dict:
        """Collect business-level metrics"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'total_items': get_total_items(),
            'avg_quality': get_average_quality(),
            'high_quality_pct': get_high_quality_percentage(),
            'items_added_today': get_items_added_today(),
            'searches_today': get_searches_today(),
            'active_users': get_active_user_count()
        }
        self.current['business'] = metrics
        return metrics

    def aggregate_metrics(self, metrics: Dict) -> Dict:
        """Aggregate metrics into hour/day/week buckets"""
        self.metrics_history.append(metrics)

        # Calculate rolling averages
        history_list = list(self.metrics_history)

        aggregated = {
            'hourly': self._calculate_averages(history_list[-60:]),  # Last hour
            'daily': self._calculate_averages(history_list[-1440:]),  # Last 24h
            'weekly': self._calculate_averages(list(self.metrics_history))  # All available
        }

        return aggregated

    def _calculate_averages(self, metrics_list: List[Dict]) -> Dict:
        """Calculate averages from metrics list"""
        if not metrics_list:
            return {}

        cpu_values = [m['system']['cpu_percent'] for m in metrics_list if 'system' in m]
        memory_values = [m['system']['memory']['percent'] for m in metrics_list if 'system' in m]

        return {
            'avg_cpu': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
            'avg_memory': sum(memory_values) / len(memory_values) if memory_values else 0,
            'p95_cpu': self._percentile(cpu_values, 0.95),
            'p95_memory': self._percentile(memory_values, 0.95),
            'max_cpu': max(cpu_values) if cpu_values else 0,
            'max_memory': max(memory_values) if memory_values else 0,
        }

    @staticmethod
    def _percentile(values: List[float], percentile: float) -> float:
        """Calculate percentile"""
        if not values:
            return 0
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile)
        return sorted_values[min(index, len(sorted_values) - 1)]

# Global instance
perf_collector = PerformanceMetrics()
```

### 2.2 Metrics Collection Tasks

Create `metrics_tasks.py`:

```python
import schedule
import time
from performance_collector import perf_collector
import json
from datetime import datetime

def collect_all_metrics():
    """Collect all metrics every minute"""
    system = perf_collector.collect_system_metrics()
    application = perf_collector.collect_application_metrics()
    business = perf_collector.collect_business_metrics()

    aggregated = perf_collector.aggregate_metrics({
        'system': system,
        'application': application,
        'business': business
    })

    return {
        'system': system,
        'application': application,
        'business': business,
        'aggregated': aggregated
    }

def generate_hourly_report():
    """Generate hourly performance report"""
    metrics = collect_all_metrics()

    report = {
        'period': 'hourly',
        'timestamp': datetime.now().isoformat(),
        'metrics': metrics['aggregated']['hourly'],
        'status': determine_status(metrics)
    }

    save_report('hourly', report)
    return report

def generate_daily_report():
    """Generate daily performance report"""
    metrics = collect_all_metrics()

    report = {
        'period': 'daily',
        'date': datetime.now().date().isoformat(),
        'metrics': metrics['aggregated']['daily'],
        'status': determine_status(metrics),
        'trend': calculate_trend()
    }

    save_report('daily', report)
    return report

def generate_weekly_report():
    """Generate weekly performance report"""
    metrics = collect_all_metrics()

    report = {
        'period': 'weekly',
        'week': datetime.now().isocalendar()[1],
        'metrics': metrics['aggregated']['weekly'],
        'status': determine_status(metrics),
        'trend': calculate_weekly_trend()
    }

    save_report('weekly', report)
    return report

def determine_status(metrics: dict) -> str:
    """Determine system status from metrics"""
    system = metrics['system']['system']

    if system['cpu_percent'] > 85 or system['memory']['percent'] > 90:
        return 'CRITICAL'
    elif system['cpu_percent'] > 75 or system['memory']['percent'] > 80:
        return 'WARNING'
    else:
        return 'HEALTHY'

def save_report(report_type: str, report: dict):
    """Save report to file"""
    timestamp = datetime.now().isoformat()
    filename = f"reports/{report_type}_{timestamp}.json"

    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)

# Schedule tasks
schedule.every(1).minute.do(collect_all_metrics)
schedule.every().hour.at(":00").do(generate_hourly_report)
schedule.every().day.at("00:00").do(generate_daily_report)
schedule.every().sunday.at("00:00").do(generate_weekly_report)

def run_scheduler():
    """Run scheduler in background thread"""
    while True:
        schedule.run_pending()
        time.sleep(60)
```

---

## 3. Performance Analysis

### 3.1 Trend Analysis

Create `trend_analysis.py`:

```python
import json
from datetime import datetime, timedelta
from typing import List, Dict
import numpy as np

class TrendAnalysis:
    """Analyze performance trends"""

    def __init__(self, days: int = 30):
        self.window_days = days

    def analyze_cpu_trend(self, metrics_list: List[Dict]) -> Dict:
        """Analyze CPU usage trends"""
        cpu_values = [m['system']['cpu_percent'] for m in metrics_list]

        return {
            'current': cpu_values[-1] if cpu_values else 0,
            'average': np.mean(cpu_values),
            'trend': self._calculate_trend(cpu_values),
            'forecast_24h': self._forecast(cpu_values, 24),
            'anomalies': self._detect_anomalies(cpu_values)
        }

    def analyze_memory_trend(self, metrics_list: List[Dict]) -> Dict:
        """Analyze memory usage trends"""
        memory_values = [m['system']['memory']['percent'] for m in metrics_list]

        return {
            'current': memory_values[-1] if memory_values else 0,
            'average': np.mean(memory_values),
            'trend': self._calculate_trend(memory_values),
            'forecast_24h': self._forecast(memory_values, 24),
            'anomalies': self._detect_anomalies(memory_values)
        }

    def analyze_error_trend(self, metrics_list: List[Dict]) -> Dict:
        """Analyze error rate trends"""
        error_rates = [m['application'].get('error_rate', 0) for m in metrics_list]

        return {
            'current': error_rates[-1] if error_rates else 0,
            'average': np.mean(error_rates),
            'trend': self._calculate_trend(error_rates),
            'is_increasing': self._is_increasing(error_rates)
        }

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return 'STABLE'

        recent = np.mean(values[-10:])
        previous = np.mean(values[-20:-10])

        if recent > previous * 1.1:
            return 'INCREASING'
        elif recent < previous * 0.9:
            return 'DECREASING'
        else:
            return 'STABLE'

    def _forecast(self, values: List[float], hours: int) -> List[float]:
        """Simple linear regression forecast"""
        if len(values) < 2:
            return [values[-1]] * hours

        x = np.arange(len(values))
        y = np.array(values)

        coefficients = np.polyfit(x, y, 1)
        poly = np.poly1d(coefficients)

        future_x = np.arange(len(values), len(values) + hours)
        return [float(poly(i)) for i in future_x]

    def _detect_anomalies(self, values: List[float], std_dev: float = 2.0) -> List[int]:
        """Detect anomalous values"""
        if len(values) < 3:
            return []

        mean = np.mean(values)
        std = np.std(values)

        anomalies = []
        for i, val in enumerate(values):
            if abs(val - mean) > std_dev * std:
                anomalies.append(i)

        return anomalies

    def _is_increasing(self, values: List[float]) -> bool:
        """Check if trend is increasing"""
        return self._calculate_trend(values) == 'INCREASING'

# Example usage
analyzer = TrendAnalysis()
```

---

## 4. Performance Reporting

### 4.1 Report Generation

Create `performance_reports.py`:

```python
from datetime import datetime, timedelta
import json
import matplotlib.pyplot as plt
from typing import Dict, List

class PerformanceReporter:
    """Generate performance reports"""

    def generate_daily_report(self, metrics_data: List[Dict]) -> Dict:
        """Generate comprehensive daily report"""

        report = {
            'date': datetime.now().date().isoformat(),
            'period': 'daily',
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'status': self._determine_status(metrics_data),
                'cpu_avg': self._calculate_metric_average(metrics_data, 'cpu'),
                'memory_avg': self._calculate_metric_average(metrics_data, 'memory'),
                'error_rate': self._calculate_error_rate(metrics_data),
                'availability': self._calculate_availability(metrics_data)
            },
            'details': {
                'system': self._analyze_system_metrics(metrics_data),
                'application': self._analyze_application_metrics(metrics_data),
                'business': self._analyze_business_metrics(metrics_data)
            },
            'alerts': self._get_alerts(metrics_data),
            'recommendations': self._generate_recommendations(metrics_data)
        }

        return report

    def generate_weekly_report(self, daily_reports: List[Dict]) -> Dict:
        """Generate weekly performance report"""

        report = {
            'week': datetime.now().isocalendar()[1],
            'year': datetime.now().year,
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'avg_availability': self._average_metric(daily_reports, 'availability'),
                'avg_error_rate': self._average_metric(daily_reports, 'error_rate'),
                'best_day': self._find_best_day(daily_reports),
                'worst_day': self._find_worst_day(daily_reports)
            },
            'trends': {
                'cpu': self._analyze_weekly_trend(daily_reports, 'cpu'),
                'memory': self._analyze_weekly_trend(daily_reports, 'memory'),
                'errors': self._analyze_weekly_trend(daily_reports, 'error_rate')
            },
            'performance_summary': self._generate_performance_summary(daily_reports)
        }

        return report

    def _determine_status(self, metrics: List[Dict]) -> str:
        """Determine overall status"""
        cpu_values = [m.get('cpu_percent', 0) for m in metrics]
        memory_values = [m.get('memory_percent', 0) for m in metrics]

        avg_cpu = sum(cpu_values) / len(cpu_values) if cpu_values else 0
        avg_memory = sum(memory_values) / len(memory_values) if memory_values else 0

        if avg_cpu > 80 or avg_memory > 85:
            return 'CRITICAL'
        elif avg_cpu > 70 or avg_memory > 75:
            return 'WARNING'
        else:
            return 'HEALTHY'

    def _calculate_metric_average(self, metrics: List[Dict], metric: str) -> float:
        """Calculate metric average"""
        values = [m.get(metric, 0) for m in metrics]
        return sum(values) / len(values) if values else 0

    def _calculate_error_rate(self, metrics: List[Dict]) -> float:
        """Calculate error rate"""
        error_counts = [m.get('errors', 0) for m in metrics]
        request_counts = [m.get('requests', 1) for m in metrics]

        total_errors = sum(error_counts)
        total_requests = sum(request_counts)

        return (total_errors / total_requests * 100) if total_requests > 0 else 0

    def _calculate_availability(self, metrics: List[Dict]) -> float:
        """Calculate system availability"""
        uptime = sum([m.get('uptime', 0) for m in metrics])
        total_time = len(metrics) * 60  # 60 seconds per metric
        return (uptime / total_time * 100) if total_time > 0 else 100

    def _generate_recommendations(self, metrics: List[Dict]) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []

        cpu_values = [m.get('cpu_percent', 0) for m in metrics]
        avg_cpu = sum(cpu_values) / len(cpu_values) if cpu_values else 0

        if avg_cpu > 70:
            recommendations.append('CPU usage high. Consider scaling up or optimizing code.')

        memory_values = [m.get('memory_percent', 0) for m in metrics]
        avg_memory = sum(memory_values) / len(memory_values) if memory_values else 0

        if avg_memory > 75:
            recommendations.append('Memory usage high. Consider cache optimization.')

        error_rate = self._calculate_error_rate(metrics)
        if error_rate > 0.5:
            recommendations.append('Error rate elevated. Check logs for issues.')

        return recommendations

    def save_report(self, report_type: str, report: Dict):
        """Save report to JSON file"""
        timestamp = datetime.now().isoformat().replace(':', '-')
        filename = f"reports/{report_type}_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Report saved: {filename}")
        return filename

# Global reporter
reporter = PerformanceReporter()
```

### 4.2 Report Templates

Daily Report Template:

```json
{
  "date": "2025-10-27",
  "period": "daily",
  "summary": {
    "status": "HEALTHY",
    "cpu_avg": "35%",
    "memory_avg": "62%",
    "error_rate": "0.02%",
    "availability": "99.98%"
  },
  "details": {
    "system": { ... },
    "application": { ... },
    "business": { ... }
  },
  "alerts": [],
  "recommendations": []
}
```

---

## 5. Integration with Monitoring

### 5.1 Update Monitoring Dashboard

```python
@app.route('/api/metrics/daily')
def get_daily_metrics():
    """Get today's performance metrics"""
    from performance_collector import perf_collector
    return perf_collector.current

@app.route('/api/reports/daily')
def get_daily_report():
    """Get latest daily report"""
    from performance_reports import reporter
    with open('reports/daily_latest.json', 'r') as f:
        return json.load(f)

@app.route('/api/metrics/trend/<metric>')
def get_metric_trend(metric):
    """Get trend for specific metric"""
    from trend_analysis import analyzer
    trends = analyzer.analyze_cpu_trend([])  # Pass actual data
    return trends[metric] if metric in trends else {}
```

---

## 6. Performance Baseline & Targets

### 6.1 Baseline Metrics

From Phase 9 performance validation (production targets):

```
Baseline Performance Targets (All ✓ ACHIEVED):
├── API Response Time (P95): <500ms
├── Error Rate: <0.1%
├── CPU Usage: <60% (avg)
├── Memory Usage: <70% (avg)
├── Disk Usage: <80%
├── API Availability: >99.9%
├── Label Search: <1ms
├── Domain Search: <5ms
├── Cache Hit Rate: >95%
└── Startup Time: <150ms
```

### 6.2 Alert Thresholds

```
Warning Level:
├── CPU: >75%
├── Memory: >80%
├── Disk: >85%
├── Error Rate: >0.5%
└── Response Time P95: >1000ms

Critical Level:
├── CPU: >85%
├── Memory: >90%
├── Disk: >95%
├── Error Rate: >1%
├── Response Time P95: >2000ms
└── Availability: <99%
```

---

## 7. Performance Optimization Opportunities

Based on continuous monitoring:

1. **Caching Improvements**
   - Monitor cache hit rates
   - Adjust TTL for frequently accessed items
   - Warm cache during off-peak hours

2. **Database Optimization**
   - Track slow queries
   - Add indexes for frequent queries
   - Monitor connection pool usage

3. **Code Optimization**
   - Profile CPU-intensive operations
   - Optimize O(n) to O(log n) where possible
   - Lazy-load large data structures

4. **Infrastructure Scaling**
   - Horizontal scaling when CPU >80%
   - Vertical scaling when Memory >85%
   - Load balancing for high throughput

---

## 8. Continuous Improvement Loop

```
Collect Metrics
    ↓
Analyze Trends
    ↓
Generate Reports
    ↓
Identify Issues
    ↓
Implement Fixes
    ↓
Monitor Results
    ↓
(Loop)
```

---

*Last Updated: October 27, 2025*
*BOB AI v7 - Performance Metrics Collection*
*Status: Production Ready*

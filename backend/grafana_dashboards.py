#!/usr/bin/env python3
"""
Grafana Dashboards Configuration
Pre-built dashboards for ORFEAS AI monitoring
"""

import json
import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GrafanaDashboardBuilder:
    """Build Grafana dashboards programmatically"""

    @staticmethod
    def build_overview_dashboard() -> Dict:
        """System overview dashboard"""
        return {
            "dashboard": {
                "title": "ORFEAS AI - System Overview",
                "description": "Real-time system performance and health",
                "tags": ["orfeas", "overview"],
                "panels": [
                    {
                        "title": "Requests/sec",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(http_requests_total[1m])"
                        }]
                    },
                    {
                        "title": "Error Rate",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(errors_total[1m])"
                        }]
                    },
                    {
                        "title": "Active Sessions",
                        "type": "stat",
                        "targets": [{
                            "expr": "auth_active_sessions"
                        }]
                    },
                    {
                        "title": "CPU Usage",
                        "type": "gauge",
                        "targets": [{
                            "expr": "cpu_usage_percent"
                        }]
                    },
                    {
                        "title": "Memory Usage",
                        "type": "gauge",
                        "targets": [{
                            "expr": "(memory_usage_bytes / memory_available_bytes) * 100"
                        }]
                    },
                    {
                        "title": "Response Time (p95)",
                        "type": "stat",
                        "targets": [{
                            "expr": "histogram_quantile(0.95, http_request_duration_seconds)"
                        }]
                    }
                ]
            }
        }

    @staticmethod
    def build_authentication_dashboard() -> Dict:
        """Authentication and authorization metrics dashboard"""
        return {
            "dashboard": {
                "title": "ORFEAS AI - Authentication",
                "description": "Authentication, OAuth2, 2FA, and session metrics",
                "tags": ["orfeas", "authentication"],
                "panels": [
                    {
                        "title": "Login Success Rate",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(auth_login_total{status=\"success\"}[5m]) / rate(auth_login_total[5m])"
                        }]
                    },
                    {
                        "title": "Total Logins (5min)",
                        "type": "stat",
                        "targets": [{
                            "expr": "increase(auth_login_total[5m])"
                        }]
                    },
                    {
                        "title": "Failed Logins (5min)",
                        "type": "stat",
                        "targets": [{
                            "expr": "increase(auth_failed_login_attempts[5m])"
                        }]
                    },
                    {
                        "title": "Account Lockouts (Today)",
                        "type": "stat",
                        "targets": [{
                            "expr": "increase(auth_account_lockouts[24h])"
                        }]
                    },
                    {
                        "title": "Active Sessions",
                        "type": "stat",
                        "targets": [{
                            "expr": "auth_active_sessions"
                        }]
                    },
                    {
                        "title": "2FA Enabled Count",
                        "type": "stat",
                        "targets": [{
                            "expr": "increase(twofa_enabled_total[24h])"
                        }]
                    },
                    {
                        "title": "OAuth2 Logins (by Provider)",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(oauth_login_total[5m])"
                        }]
                    },
                    {
                        "title": "Token Generation Rate",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(auth_token_generated_total[1m])"
                        }]
                    }
                ]
            }
        }

    @staticmethod
    def build_database_dashboard() -> Dict:
        """Database performance dashboard"""
        return {
            "dashboard": {
                "title": "ORFEAS AI - Database Performance",
                "description": "Database connection pool, query performance, and health",
                "tags": ["orfeas", "database"],
                "panels": [
                    {
                        "title": "Active Connections",
                        "type": "graph",
                        "targets": [{
                            "expr": "db_connections_active"
                        }]
                    },
                    {
                        "title": "Query Latency (p95)",
                        "type": "graph",
                        "targets": [{
                            "expr": "histogram_quantile(0.95, db_query_duration_seconds)"
                        }]
                    },
                    {
                        "title": "Queries/sec",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(db_queries_total[1m])"
                        }]
                    },
                    {
                        "title": "Query Error Rate",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(db_queries_total{status=\"error\"}[1m]) / rate(db_queries_total[1m])"
                        }]
                    },
                    {
                        "title": "SELECT Queries",
                        "type": "stat",
                        "targets": [{
                            "expr": "increase(db_queries_total{query_type=\"SELECT\"}[5m])"
                        }]
                    },
                    {
                        "title": "INSERT Queries",
                        "type": "stat",
                        "targets": [{
                            "expr": "increase(db_queries_total{query_type=\"INSERT\"}[5m])"
                        }]
                    }
                ]
            }
        }

    @staticmethod
    def build_cache_dashboard() -> Dict:
        """Cache performance dashboard"""
        return {
            "dashboard": {
                "title": "ORFEAS AI - Cache Performance",
                "description": "Redis and memory cache hit rates and performance",
                "tags": ["orfeas", "cache"],
                "panels": [
                    {
                        "title": "Cache Hit Rate",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m]))"
                        }]
                    },
                    {
                        "title": "Cache Hits/sec",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(cache_hits_total[1m])"
                        }]
                    },
                    {
                        "title": "Cache Misses/sec",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(cache_misses_total[1m])"
                        }]
                    },
                    {
                        "title": "Redis Cache Size",
                        "type": "stat",
                        "targets": [{
                            "expr": "cache_size_bytes{cache_type=\"redis\"} / 1024 / 1024"
                        }]
                    },
                    {
                        "title": "Memory Cache Size",
                        "type": "stat",
                        "targets": [{
                            "expr": "cache_size_bytes{cache_type=\"memory\"} / 1024 / 1024"
                        }]
                    }
                ]
            }
        }

    @staticmethod
    def build_generation_dashboard() -> Dict:
        """3D Model generation metrics dashboard"""
        return {
            "dashboard": {
                "title": "ORFEAS AI - 3D Generation",
                "description": "3D model generation performance and queue metrics",
                "tags": ["orfeas", "generation"],
                "panels": [
                    {
                        "title": "Generations/min",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(generation_total[1m])"
                        }]
                    },
                    {
                        "title": "Generation Success Rate",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(generation_total{status=\"success\"}[5m]) / rate(generation_total[5m])"
                        }]
                    },
                    {
                        "title": "Generation Time (p95)",
                        "type": "graph",
                        "targets": [{
                            "expr": "histogram_quantile(0.95, generation_duration_seconds)"
                        }]
                    },
                    {
                        "title": "Queue Depth",
                        "type": "stat",
                        "targets": [{
                            "expr": "generation_queue_depth"
                        }]
                    },
                    {
                        "title": "Concurrent Jobs",
                        "type": "stat",
                        "targets": [{
                            "expr": "generation_concurrent_jobs"
                        }]
                    },
                    {
                        "title": "Failed Generations (5min)",
                        "type": "stat",
                        "targets": [{
                            "expr": "increase(generation_total{status=\"failed\"}[5m])"
                        }]
                    }
                ]
            }
        }

    @staticmethod
    def build_gpu_dashboard() -> Dict:
        """GPU resource utilization dashboard"""
        return {
            "dashboard": {
                "title": "ORFEAS AI - GPU Resources",
                "description": "GPU memory, utilization, and temperature monitoring",
                "tags": ["orfeas", "gpu"],
                "panels": [
                    {
                        "title": "GPU Memory Usage",
                        "type": "graph",
                        "targets": [{
                            "expr": "gpu_memory_used_mb"
                        }]
                    },
                    {
                        "title": "GPU Utilization (%)",
                        "type": "graph",
                        "targets": [{
                            "expr": "gpu_utilization_percent"
                        }]
                    },
                    {
                        "title": "GPU Temperature (C)",
                        "type": "graph",
                        "targets": [{
                            "expr": "gpu_temperature_celsius"
                        }]
                    },
                    {
                        "title": "Memory Usage (%)",
                        "type": "gauge",
                        "targets": [{
                            "expr": "(gpu_memory_used_mb / gpu_memory_total_mb) * 100"
                        }]
                    }
                ]
            }
        }


class AlertRuleBuilder:
    """Build Prometheus alert rules"""

    @staticmethod
    def build_alert_rules() -> Dict:
        """Build all alert rules"""
        return {
            "groups": [
                {
                    "name": "orfeas_alerts",
                    "rules": [
                        {
                            "alert": "HighErrorRate",
                            "expr": "rate(errors_total[5m]) > 0.05",
                            "for": "5m",
                            "labels": {"severity": "warning"},
                            "annotations": {
                                "summary": "High error rate detected",
                                "description": "Error rate is {{ $value | humanizePercentage }} over 5 minutes"
                            }
                        },
                        {
                            "alert": "HighResponseTime",
                            "expr": "histogram_quantile(0.95, http_request_duration_seconds) > 1.0",
                            "for": "5m",
                            "labels": {"severity": "warning"},
                            "annotations": {
                                "summary": "High response time",
                                "description": "P95 response time is {{ $value }}s"
                            }
                        },
                        {
                            "alert": "DatabaseConnectionPoolExhausted",
                            "expr": "db_connections_active / db_connection_pool_size > 0.9",
                            "for": "2m",
                            "labels": {"severity": "critical"},
                            "annotations": {
                                "summary": "Database connection pool nearly exhausted",
                                "description": "{{ $value | humanizePercentage }} of connections in use"
                            }
                        },
                        {
                            "alert": "HighCPUUsage",
                            "expr": "cpu_usage_percent > 80",
                            "for": "5m",
                            "labels": {"severity": "warning"},
                            "annotations": {
                                "summary": "High CPU usage",
                                "description": "CPU usage is {{ $value }}%"
                            }
                        },
                        {
                            "alert": "HighMemoryUsage",
                            "expr": "(memory_usage_bytes / memory_available_bytes) > 0.85",
                            "for": "5m",
                            "labels": {"severity": "warning"},
                            "annotations": {
                                "summary": "High memory usage",
                                "description": "Memory usage is {{ $value | humanizePercentage }}"
                            }
                        },
                        {
                            "alert": "LowCacheHitRate",
                            "expr": "rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m])) < 0.7",
                            "for": "10m",
                            "labels": {"severity": "info"},
                            "annotations": {
                                "summary": "Low cache hit rate",
                                "description": "Cache hit rate is {{ $value | humanizePercentage }}"
                            }
                        },
                        {
                            "alert": "GenerationFailureRate",
                            "expr": "rate(generation_total{status=\"failed\"}[5m]) / rate(generation_total[5m]) > 0.1",
                            "for": "5m",
                            "labels": {"severity": "warning"},
                            "annotations": {
                                "summary": "High 3D generation failure rate",
                                "description": "Failure rate is {{ $value | humanizePercentage }}"
                            }
                        },
                        {
                            "alert": "LoginFailureRate",
                            "expr": "rate(auth_failed_login_attempts[5m]) > 5",
                            "for": "2m",
                            "labels": {"severity": "warning"},
                            "annotations": {
                                "summary": "High login failure rate",
                                "description": "{{ $value }} failed logins per second"
                            }
                        },
                        {
                            "alert": "GPUMemoryExhausted",
                            "expr": "(gpu_memory_used_mb / gpu_memory_total_mb) > 0.95",
                            "for": "1m",
                            "labels": {"severity": "critical"},
                            "annotations": {
                                "summary": "GPU memory almost exhausted",
                                "description": "GPU memory usage is {{ $value | humanizePercentage }}"
                            }
                        },
                        {
                            "alert": "HighGPUTemperature",
                            "expr": "gpu_temperature_celsius > 85",
                            "for": "5m",
                            "labels": {"severity": "warning"},
                            "annotations": {
                                "summary": "High GPU temperature",
                                "description": "GPU temperature is {{ $value }}°C"
                            }
                        }
                    ]
                }
            ]
        }


class GrafanaProvisioning:
    """Generate Grafana provisioning files"""

    @staticmethod
    def generate_datasource_config() -> Dict:
        """Generate Prometheus datasource configuration"""
        return {
            "apiVersion": 1,
            "providers": [
                {
                    "name": "Prometheus",
                    "type": "prometheus",
                    "url": "http://prometheus:9090",
                    "access": "proxy",
                    "isDefault": True,
                    "editable": True
                }
            ]
        }

    @staticmethod
    def generate_dashboard_provisioning() -> Dict:
        """Generate dashboard provisioning configuration"""
        return {
            "apiVersion": 1,
            "providers": [
                {
                    "name": "ORFEAS Dashboards",
                    "type": "file",
                    "options": {
                        "path": "/etc/grafana/provisioning/dashboards"
                    }
                }
            ]
        }

"""
Advanced Alerting System - Phase 4 Tier 2
Configurable alerts for performance, resource, and application metrics
Severity-based routing with subscriber callbacks for automated response
"""

import logging
from typing import Dict, List, Callable, Optional, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import threading

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


@dataclass
class Alert:
    """Alert definition with configuration"""
    name: str
    metric: str
    threshold: float
    severity: AlertSeverity
    message: str
    comparison: str = ">"  # >, <, >=, <=, ==, !=
    duration_seconds: int = 0  # Alert only if condition persists for this duration
    cooldown_seconds: int = 300  # Don't re-trigger for this duration
    enabled: bool = True

    # State
    triggered: bool = False
    status: AlertStatus = AlertStatus.RESOLVED
    last_triggered: Optional[datetime] = None
    last_cleared: Optional[datetime] = None
    trigger_count: int = 0
    cooldown_until: Optional[datetime] = None


class AlertingSystem:
    """
    Configurable alerting system for comprehensive monitoring
    Supports alert registration, evaluation, and multi-channel notification
    """

    def __init__(self, enable_logging: bool = True):
        """
        Initialize alerting system

        Args:
            enable_logging: Whether to log all alert events
        """
        self.alerts: List[Alert] = []
        self.subscribers: Dict[AlertSeverity, Set[Callable]] = {
            AlertSeverity.INFO: set(),
            AlertSeverity.WARNING: set(),
            AlertSeverity.CRITICAL: set()
        }
        self.all_subscribers: Set[Callable] = set()  # Receive all alerts
        self.alert_history: List[Dict] = []
        self.max_history = 1000
        self.enable_logging = enable_logging
        self._lock = threading.Lock()
        self.stats = {
            'total_alerts_triggered': 0,
            'total_alerts_cleared': 0,
            'info_count': 0,
            'warning_count': 0,
            'critical_count': 0
        }

    def register_alert(self, alert: Alert) -> None:
        """
        Register an alert

        Args:
            alert: Alert configuration to register
        """
        with self._lock:
            self.alerts.append(alert)

        if self.enable_logging:
            logger.info(
                f"[ALERTS] Registered alert: {alert.name} "
                f"(metric={alert.metric}, threshold={alert.threshold}, "
                f"severity={alert.severity.value})"
            )

    def deregister_alert(self, alert_name: str) -> bool:
        """Deregister an alert by name"""
        with self._lock:
            for i, alert in enumerate(self.alerts):
                if alert.name == alert_name:
                    self.alerts.pop(i)
                    if self.enable_logging:
                        logger.info(f"[ALERTS] Deregistered alert: {alert_name}")
                    return True
        return False

    def check_alerts(self, metrics: Dict) -> None:
        """
        Check all registered alerts against current metrics

        Args:
            metrics: Current metric values
        """
        with self._lock:
            for alert in self.alerts:
                if not alert.enabled:
                    continue

                if alert.metric not in metrics:
                    continue

                value = metrics[alert.metric]

                # Check comparison
                should_trigger = self._evaluate_condition(value, alert.threshold, alert.comparison)

                if should_trigger:
                    if not alert.triggered:
                        self._trigger_alert(alert, value, metrics)
                    alert.triggered = True
                else:
                    if alert.triggered:
                        self._clear_alert(alert, metrics)
                    alert.triggered = False

    def _evaluate_condition(self, value: float, threshold: float, comparison: str) -> bool:
        """Evaluate alert condition"""
        if comparison == ">":
            return value > threshold
        elif comparison == "<":
            return value < threshold
        elif comparison == ">=":
            return value >= threshold
        elif comparison == "<=":
            return value <= threshold
        elif comparison == "==":
            return value == threshold
        elif comparison == "!=":
            return value != threshold
        return False

    def _trigger_alert(self, alert: Alert, value: float, metrics: Dict) -> None:
        """
        Trigger an alert

        Args:
            alert: Alert to trigger
            value: Current metric value
            metrics: All current metrics
        """
        now = datetime.now()

        # Check cooldown
        if alert.cooldown_until and now < alert.cooldown_until:
            if self.enable_logging:
                logger.debug(
                    f"[ALERTS] {alert.name} in cooldown until "
                    f"{alert.cooldown_until.isoformat()}"
                )
            return

        alert.status = AlertStatus.ACTIVE
        alert.last_triggered = now
        alert.trigger_count += 1
        alert.cooldown_until = now + timedelta(seconds=alert.cooldown_seconds)

        # Construct alert message
        message = f"{alert.message} (Current: {value}, Threshold: {alert.threshold})"

        # Create alert event
        alert_event = {
            'timestamp': now.isoformat(),
            'alert_name': alert.name,
            'severity': alert.severity.value,
            'message': message,
            'metric': alert.metric,
            'value': value,
            'threshold': alert.threshold,
            'trigger_count': alert.trigger_count
        }

        # Add to history
        with self._lock:
            self.alert_history.append(alert_event)
            if len(self.alert_history) > self.max_history:
                self.alert_history = self.alert_history[-self.max_history:]

            # Update stats
            self.stats['total_alerts_triggered'] += 1
            if alert.severity == AlertSeverity.INFO:
                self.stats['info_count'] += 1
            elif alert.severity == AlertSeverity.WARNING:
                self.stats['warning_count'] += 1
            elif alert.severity == AlertSeverity.CRITICAL:
                self.stats['critical_count'] += 1

        # Notify subscribers
        self._notify_subscribers(alert_event)

        if self.enable_logging:
            logger.warning(f"[ALERT] TRIGGERED: {alert.name}: {message}")

    def _clear_alert(self, alert: Alert, metrics: Dict) -> None:
        """
        Clear a triggered alert

        Args:
            alert: Alert to clear
            metrics: Current metrics
        """
        now = datetime.now()
        alert.status = AlertStatus.RESOLVED
        alert.last_cleared = now

        # Create clear event
        clear_event = {
            'timestamp': now.isoformat(),
            'alert_name': alert.name,
            'severity': alert.severity.value,
            'event_type': 'cleared',
            'duration_triggered_seconds': (
                (now - alert.last_triggered).total_seconds()
                if alert.last_triggered else 0
            )
        }

        with self._lock:
            self.alert_history.append(clear_event)
            self.stats['total_alerts_cleared'] += 1

        if self.enable_logging:
            logger.info(f"[ALERT] CLEARED: {alert.name}")

    def _notify_subscribers(self, alert_event: Dict) -> None:
        """
        Notify alert subscribers

        Args:
            alert_event: Alert event to notify about
        """
        severity = AlertSeverity(alert_event['severity'])

        # Notify severity-specific subscribers
        with self._lock:
            for callback in self.subscribers.get(severity, set()).copy():
                try:
                    callback(alert_event)
                except Exception as e:
                    logger.error(f"[ALERTS] Subscriber callback failed: {e}")

            # Notify all-severity subscribers
            for callback in self.all_subscribers.copy():
                try:
                    callback(alert_event)
                except Exception as e:
                    logger.error(f"[ALERTS] All-severity callback failed: {e}")

    def subscribe(self, severity: Optional[AlertSeverity], callback: Callable) -> None:
        """
        Subscribe to alerts of specific severity

        Args:
            severity: Alert severity to subscribe to (None = all severities)
            callback: Callable to invoke on alert
        """
        with self._lock:
            if severity is None:
                self.all_subscribers.add(callback)
            else:
                self.subscribers[severity].add(callback)

        if self.enable_logging:
            severity_name = severity.value if severity else "all"
            logger.info(f"[ALERTS] Subscriber registered for {severity_name} severity")

    def unsubscribe(self, severity: Optional[AlertSeverity], callback: Callable) -> None:
        """
        Unsubscribe from alerts

        Args:
            severity: Alert severity (None = all severities)
            callback: Callback to unsubscribe
        """
        with self._lock:
            if severity is None:
                self.all_subscribers.discard(callback)
            else:
                self.subscribers[severity].discard(callback)

    def acknowledge_alert(self, alert_name: str) -> bool:
        """Acknowledge a triggered alert"""
        with self._lock:
            for alert in self.alerts:
                if alert.name == alert_name and alert.triggered:
                    alert.status = AlertStatus.ACKNOWLEDGED
                    if self.enable_logging:
                        logger.info(f"[ALERTS] Acknowledged: {alert_name}")
                    return True
        return False

    def get_active_alerts(self) -> List[Dict]:
        """Get list of currently active alerts"""
        with self._lock:
            return [
                {
                    'name': alert.name,
                    'severity': alert.severity.value,
                    'status': alert.status.value,
                    'metric': alert.metric,
                    'threshold': alert.threshold,
                    'message': alert.message,
                    'last_triggered': alert.last_triggered.isoformat() if alert.last_triggered else None,
                    'trigger_count': alert.trigger_count
                }
                for alert in self.alerts
                if alert.triggered
            ]

    def get_alert_history(self, limit: int = 100, severity: Optional[AlertSeverity] = None) -> List[Dict]:
        """Get alert history"""
        with self._lock:
            history = self.alert_history[-limit:]
            if severity:
                history = [h for h in history if h.get('severity') == severity.value]
            return history

    def get_stats(self) -> Dict:
        """Get alerting system statistics"""
        with self._lock:
            active_count = sum(1 for alert in self.alerts if alert.triggered)
            total_registered = len(self.alerts)

            return {
                'registered_alerts': total_registered,
                'active_alerts': active_count,
                'total_alerts_triggered': self.stats['total_alerts_triggered'],
                'total_alerts_cleared': self.stats['total_alerts_cleared'],
                'severity_breakdown': {
                    'info': self.stats['info_count'],
                    'warning': self.stats['warning_count'],
                    'critical': self.stats['critical_count']
                },
                'subscribers': {
                    'info': len(self.subscribers[AlertSeverity.INFO]),
                    'warning': len(self.subscribers[AlertSeverity.WARNING]),
                    'critical': len(self.subscribers[AlertSeverity.CRITICAL]),
                    'all_severity': len(self.all_subscribers)
                },
                'history_size': len(self.alert_history)
            }


# Factory function for default alerts
def create_default_alerts() -> List[Alert]:
    """Create standard production alerts"""
    return [
        # GPU Alerts
        Alert(
            name="GPU Memory Critical",
            metric="gpu_memory_percent",
            threshold=95,
            severity=AlertSeverity.CRITICAL,
            message="🔴 GPU memory critically high - immediate cleanup required",
            comparison=">=",
            cooldown_seconds=60
        ),
        Alert(
            name="GPU Memory High",
            metric="gpu_memory_percent",
            threshold=85,
            severity=AlertSeverity.WARNING,
            message="🟠 GPU memory warning - consider optimization",
            comparison=">=",
            cooldown_seconds=300
        ),
        # CPU Alerts
        Alert(
            name="CPU Overload",
            metric="cpu_percent",
            threshold=90,
            severity=AlertSeverity.WARNING,
            message="🟠 CPU utilization high",
            comparison=">=",
            cooldown_seconds=300
        ),
        Alert(
            name="CPU Critical",
            metric="cpu_percent",
            threshold=95,
            severity=AlertSeverity.CRITICAL,
            message="🔴 CPU critical - system under extreme load",
            comparison=">=",
            cooldown_seconds=60
        ),
        # Cache Alerts
        Alert(
            name="Cache Performance Degraded",
            metric="cache_miss_rate_percent",
            threshold=50,
            severity=AlertSeverity.WARNING,
            message="🟠 Cache performance degrading - hit rate low",
            comparison=">",
            cooldown_seconds=600
        ),
        # Response Time Alerts
        Alert(
            name="Response Time Elevated",
            metric="response_time_ms",
            threshold=1000,
            severity=AlertSeverity.WARNING,
            message="🟠 Response times elevated - investigation recommended",
            comparison=">",
            cooldown_seconds=300
        ),
        Alert(
            name="Response Time Critical",
            metric="response_time_ms",
            threshold=5000,
            severity=AlertSeverity.CRITICAL,
            message="🔴 Response times critical - immediate investigation required",
            comparison=">",
            cooldown_seconds=60
        ),
        # Error Rate Alerts
        Alert(
            name="Error Rate High",
            metric="error_rate_percent",
            threshold=5,
            severity=AlertSeverity.WARNING,
            message="🟠 Error rate elevated",
            comparison=">",
            cooldown_seconds=300
        ),
        Alert(
            name="Error Rate Critical",
            metric="error_rate_percent",
            threshold=10,
            severity=AlertSeverity.CRITICAL,
            message="🔴 Error rate critical - system stability at risk",
            comparison=">",
            cooldown_seconds=60
        ),
        # Memory Fragmentation Alerts
        Alert(
            name="Memory Fragmentation High",
            metric="memory_fragmentation",
            threshold=0.5,
            severity=AlertSeverity.WARNING,
            message="🟠 Memory fragmentation high - consider cleanup",
            comparison=">",
            cooldown_seconds=600
        ),
    ]


# Singleton instance
_alerting_system: Optional[AlertingSystem] = None


def get_alerting_system() -> AlertingSystem:
    """Get or create alerting system singleton"""
    global _alerting_system
    if _alerting_system is None:
        _alerting_system = AlertingSystem()

        # Register default alerts
        for alert in create_default_alerts():
            _alerting_system.register_alert(alert)

        logger.info("[ALERTS] Alerting system initialized with default alerts")

    return _alerting_system


def reset_alerting_system() -> None:
    """Reset alerting system (for testing)"""
    global _alerting_system
    _alerting_system = None

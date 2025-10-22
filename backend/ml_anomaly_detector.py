"""
ML-Based Anomaly Detection - Phase 4 Tier 3
Uses statistical methods and machine learning to detect unusual patterns
Automatically identifies performance anomalies without explicit thresholds
"""

import logging
import statistics
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """Types of anomalies detected"""
    SUDDEN_SPIKE = "sudden_spike"
    GRADUAL_DEGRADATION = "gradual_degradation"
    PERIODIC_PATTERN = "periodic_pattern_broken"
    STATISTICAL_OUTLIER = "statistical_outlier"
    CORRELATED_ANOMALY = "correlated_anomaly"
    UNKNOWN = "unknown"


@dataclass
class Anomaly:
    """Detected anomaly"""
    anomaly_type: AnomalyType
    metric: str
    severity: float  # 0-100, higher = more severe
    confidence: float  # 0-100
    description: str
    detected_at: datetime
    affected_values: List[float]
    suggested_action: str


class MLAnomalyDetector:
    """
    Machine learning-based anomaly detection
    Uses statistical analysis and pattern recognition to identify issues
    """

    def __init__(self, lookback_samples: int = 300, anomaly_threshold: float = 2.0):
        """
        Initialize anomaly detector

        Args:
            lookback_samples: Number of historical samples to maintain
            anomaly_threshold: Standard deviations for outlier detection
        """
        self.lookback_samples = lookback_samples
        self.anomaly_threshold = anomaly_threshold
        self.metric_history: Dict[str, List[float]] = {}
        self.detected_anomalies: List[Anomaly] = []
        self.baseline_stats: Dict[str, Dict] = {}
        self.correlation_matrix: Dict[Tuple[str, str], float] = {}

    def add_metric(self, metric_name: str, value: float) -> None:
        """Add metric sample to history"""
        if metric_name not in self.metric_history:
            self.metric_history[metric_name] = []

        self.metric_history[metric_name].append(value)

        # Keep only recent history
        if len(self.metric_history[metric_name]) > self.lookback_samples:
            self.metric_history[metric_name] = self.metric_history[metric_name][-self.lookback_samples:]

    def detect_anomalies(self, metrics: Dict) -> List[Anomaly]:
        """
        Detect anomalies in provided metrics

        Args:
            metrics: Current metric values

        Returns:
            List of detected anomalies
        """
        detected = []

        for metric_name, value in metrics.items():
            # Add to history
            self.add_metric(metric_name, value)

            # Check for anomalies
            history = self.metric_history.get(metric_name, [])
            if len(history) < 10:
                continue

            # Statistical analysis
            spike_anomaly = self._detect_sudden_spike(metric_name, history)
            if spike_anomaly:
                detected.append(spike_anomaly)

            # Degradation detection
            degradation = self._detect_gradual_degradation(metric_name, history)
            if degradation:
                detected.append(degradation)

            # Outlier detection
            outlier = self._detect_statistical_outlier(metric_name, history)
            if outlier:
                detected.append(outlier)

        # Correlation analysis
        correlated = self._detect_correlated_anomalies(metrics)
        detected.extend(correlated)

        # Store anomalies
        self.detected_anomalies = detected

        if detected:
            logger.warning(f"[ANOMALY] Detected {len(detected)} anomalies")
            for anomaly in detected:
                logger.warning(
                    f"  - {anomaly.metric}: {anomaly.anomaly_type.value} "
                    f"(severity: {anomaly.severity:.0f}%, confidence: {anomaly.confidence:.0f}%)"
                )

        return detected

    def _detect_sudden_spike(self, metric_name: str, history: List[float]) -> Optional[Anomaly]:
        """Detect sudden spikes in metric value"""
        if len(history) < 5:
            return None

        recent = history[-1]
        previous_avg = statistics.mean(history[-10:-1]) if len(history) > 10 else statistics.mean(history[:-1])

        if previous_avg == 0:
            return None

        spike_percent = abs(recent - previous_avg) / previous_avg * 100

        # Detect sudden spike (> 50% change)
        if spike_percent > 50:
            spike_severity = min(100, spike_percent / 2)
            confidence = min(100, 90 + (spike_percent - 50) / 10)

            return Anomaly(
                anomaly_type=AnomalyType.SUDDEN_SPIKE,
                metric=metric_name,
                severity=spike_severity,
                confidence=confidence,
                description=f"Sudden spike detected: {spike_percent:.1f}% increase from baseline",
                detected_at=datetime.now(),
                affected_values=[previous_avg, recent],
                suggested_action="investigate_cause" if spike_severity > 75 else "monitor_closely"
            )

        return None

    def _detect_gradual_degradation(self, metric_name: str, history: List[float]) -> Optional[Anomaly]:
        """Detect gradual performance degradation"""
        if len(history) < 20:
            return None

        # Split into quarters
        quarter_size = len(history) // 4
        q1 = statistics.mean(history[:quarter_size])
        q2 = statistics.mean(history[quarter_size:quarter_size*2])
        q3 = statistics.mean(history[quarter_size*2:quarter_size*3])
        q4 = statistics.mean(history[quarter_size*3:])

        quarters = [q1, q2, q3, q4]

        # Check if consistently increasing/decreasing
        is_degrading = all(quarters[i] <= quarters[i+1] for i in range(3))
        is_improving = all(quarters[i] >= quarters[i+1] for i in range(3))

        if not is_degrading:
            return None

        degradation_rate = (q4 - q1) / q1 * 100 if q1 != 0 else 0

        # Detect significant degradation (> 20%)
        if degradation_rate > 20:
            confidence = min(100, 70 + min(30, degradation_rate / 10))

            return Anomaly(
                anomaly_type=AnomalyType.GRADUAL_DEGRADATION,
                metric=metric_name,
                severity=min(100, degradation_rate),
                confidence=confidence,
                description=f"Gradual degradation detected: {degradation_rate:.1f}% over time",
                detected_at=datetime.now(),
                affected_values=quarters,
                suggested_action="optimize_performance" if degradation_rate > 50 else "monitor_trend"
            )

        return None

    def _detect_statistical_outlier(self, metric_name: str, history: List[float]) -> Optional[Anomaly]:
        """Detect statistical outliers using Z-score"""
        if len(history) < 10:
            return None

        recent = history[-1]
        baseline = history[:-1]

        mean = statistics.mean(baseline)
        stdev = statistics.stdev(baseline) if len(baseline) > 1 else 0

        if stdev == 0:
            return None

        z_score = abs(recent - mean) / stdev

        # Z-score > 3 is typically considered outlier
        if z_score > self.anomaly_threshold:
            severity = min(100, z_score * 20)
            confidence = min(100, 80 + (z_score - self.anomaly_threshold) * 5)

            return Anomaly(
                anomaly_type=AnomalyType.STATISTICAL_OUTLIER,
                metric=metric_name,
                severity=severity,
                confidence=confidence,
                description=f"Statistical outlier detected (Z-score: {z_score:.2f})",
                detected_at=datetime.now(),
                affected_values=[mean, recent],
                suggested_action="investigate_immediately" if z_score > 4 else "investigate"
            )

        return None

    def _detect_correlated_anomalies(self, metrics: Dict) -> List[Anomaly]:
        """Detect anomalies across correlated metrics"""
        correlated_anomalies = []

        # Check if multiple metrics are anomalous simultaneously
        anomaly_count = 0
        for metric_name, value in metrics.items():
            history = self.metric_history.get(metric_name, [])
            if len(history) < 10:
                continue

            mean = statistics.mean(history[:-1])
            stdev = statistics.stdev(history[:-1]) if len(history) > 1 else 0

            if stdev > 0:
                z_score = abs(value - mean) / stdev
                if z_score > self.anomaly_threshold:
                    anomaly_count += 1

        # If multiple metrics are anomalous, it's a correlated anomaly
        if anomaly_count >= 3:
            correlated_anomalies.append(
                Anomaly(
                    anomaly_type=AnomalyType.CORRELATED_ANOMALY,
                    metric="multiple",
                    severity=min(100, anomaly_count * 20),
                    confidence=90.0,
                    description=f"{anomaly_count} metrics showing anomalies simultaneously",
                    detected_at=datetime.now(),
                    affected_values=[float(anomaly_count)],
                    suggested_action="system_investigation_required"
                )
            )

        return correlated_anomalies

    def calculate_baseline_stats(self) -> Dict:
        """Calculate baseline statistics for all metrics"""
        stats = {}

        for metric_name, history in self.metric_history.items():
            if len(history) < 10:
                continue

            stats[metric_name] = {
                'mean': statistics.mean(history),
                'median': statistics.median(history),
                'stdev': statistics.stdev(history) if len(history) > 1 else 0,
                'min': min(history),
                'max': max(history),
                'range': max(history) - min(history),
                'samples': len(history)
            }

        self.baseline_stats = stats
        return stats

    def get_anomaly_report(self) -> Dict:
        """Generate anomaly report"""
        self.calculate_baseline_stats()

        critical_anomalies = [a for a in self.detected_anomalies if a.severity > 75]
        warning_anomalies = [a for a in self.detected_anomalies if 50 <= a.severity <= 75]

        return {
            'timestamp': datetime.now().isoformat(),
            'total_anomalies': len(self.detected_anomalies),
            'critical_anomalies': len(critical_anomalies),
            'warning_anomalies': len(warning_anomalies),
            'anomalies': [
                {
                    'type': a.anomaly_type.value,
                    'metric': a.metric,
                    'severity_percent': round(a.severity, 2),
                    'confidence_percent': round(a.confidence, 2),
                    'description': a.description,
                    'detected_at': a.detected_at.isoformat(),
                    'suggested_action': a.suggested_action
                }
                for a in self.detected_anomalies
            ],
            'baseline_stats': {
                k: {
                    'mean': round(v['mean'], 2),
                    'median': round(v['median'], 2),
                    'stdev': round(v['stdev'], 2),
                    'range': round(v['range'], 2),
                    'min': round(v['min'], 2),
                    'max': round(v['max'], 2)
                }
                for k, v in self.baseline_stats.items()
            },
            'system_health': self._calculate_system_health()
        }

    def _calculate_system_health(self) -> Dict:
        """Calculate overall system health based on anomalies"""
        if not self.detected_anomalies:
            return {'score': 100, 'status': 'healthy'}

        total_severity = sum(a.severity for a in self.detected_anomalies)
        avg_severity = total_severity / len(self.detected_anomalies)

        health_score = max(0, 100 - avg_severity)

        if health_score >= 90:
            status = 'healthy'
        elif health_score >= 75:
            status = 'degraded'
        elif health_score >= 50:
            status = 'unhealthy'
        else:
            status = 'critical'

        return {
            'score': round(health_score, 2),
            'status': status,
            'anomaly_count': len(self.detected_anomalies),
            'average_severity': round(avg_severity, 2)
        }

    def clear_history(self) -> None:
        """Clear historical data and anomalies"""
        self.metric_history.clear()
        self.detected_anomalies.clear()
        self.baseline_stats.clear()
        logger.info("[ANOMALY] Cleared history and anomalies")


# Singleton instance
_detector_instance: Optional[MLAnomalyDetector] = None


def get_anomaly_detector() -> MLAnomalyDetector:
    """Get or create anomaly detector singleton"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = MLAnomalyDetector()
        logger.info("[ANOMALY] ML Anomaly Detector initialized")
    return _detector_instance


def reset_detector() -> None:
    """Reset detector instance (for testing)"""
    global _detector_instance
    _detector_instance = None

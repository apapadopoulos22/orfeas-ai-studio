"""
Predictive Performance Optimizer - Phase 4 Tier 2
Uses historical metrics to predict and prevent performance issues before they occur
Machine learning-enhanced trend analysis and forecasting
"""

import logging
import statistics
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TrendAnalysis:
    """Trend analysis result"""
    metric: str
    trend: str  # 'improving', 'degrading', 'stable'
    trend_percent: float
    confidence: float  # 0-100
    direction: float  # positive or negative
    velocity: float  # rate of change


@dataclass
class Prediction:
    """Performance prediction"""
    prediction_type: str  # 'memory_pressure', 'cache_hit_rate', 'response_time'
    prediction: str
    confidence: float  # 0-100
    time_to_event_minutes: Optional[float]
    recommended_action: str


class PredictivePerformanceOptimizer:
    """
    Predicts performance issues before they occur
    Uses historical data analysis, trend detection, and simple forecasting
    """

    def __init__(self, lookback_hours: int = 24, min_samples: int = 10):
        """
        Initialize predictive optimizer

        Args:
            lookback_hours: Hours of historical data to consider
            min_samples: Minimum samples needed for predictions
        """
        self.lookback_hours = lookback_hours
        self.min_samples = min_samples
        self.performance_history: List[Dict] = []
        self.predictions: List[Prediction] = []
        self.prediction_accuracy: Dict[str, float] = {}

    def add_metric_sample(self, metrics: Dict) -> None:
        """Add new metric sample to history"""
        self.performance_history.append({
            'timestamp': datetime.now(),
            'metrics': metrics
        })

        # Keep only recent history
        cutoff_time = datetime.now() - timedelta(hours=self.lookback_hours)
        self.performance_history = [
            h for h in self.performance_history
            if h['timestamp'] > cutoff_time
        ]

    def analyze_trends(self, metric_key: str, metrics_history: List[Dict]) -> Optional[TrendAnalysis]:
        """
        Analyze historical metrics for trends

        Args:
            metric_key: Key of metric to analyze
            metrics_history: List of metric dictionaries with this metric

        Returns:
            TrendAnalysis object or None if insufficient data
        """
        if len(metrics_history) < self.min_samples:
            return None

        # Extract values
        values = [m.get(metric_key, 0) for m in metrics_history]
        if not values or len(set(values)) < 2:  # No variance
            return TrendAnalysis(
                metric=metric_key,
                trend='stable',
                trend_percent=0.0,
                confidence=50.0,
                direction=0.0,
                velocity=0.0
            )

        # Split into recent and older
        split_point = len(values) // 2
        recent = values[split_point:]
        older = values[:split_point]

        recent_avg = statistics.mean(recent)
        older_avg = statistics.mean(older) if older else recent_avg

        # Calculate trend percent
        if older_avg > 0:
            trend_percent = ((recent_avg - older_avg) / older_avg) * 100
        else:
            trend_percent = 0.0

        # Determine trend direction
        if trend_percent > 10:
            trend = 'degrading'
            direction = -1.0
        elif trend_percent < -10:
            trend = 'improving'
            direction = 1.0
        else:
            trend = 'stable'
            direction = 0.0

        # Calculate confidence based on variance consistency
        recent_stdev = statistics.stdev(recent) if len(recent) > 1 else 0
        older_stdev = statistics.stdev(older) if len(older) > 1 else 0

        # More consistent = higher confidence
        consistency = 1.0 - (
            (abs(recent_stdev - older_stdev) / max(recent_stdev, older_stdev, 0.01))
            if max(recent_stdev, older_stdev) > 0 else 0
        )
        confidence = min(100, max(50, consistency * 100))

        # Velocity (rate of change)
        velocity = trend_percent / max(1, len(recent))

        analysis = TrendAnalysis(
            metric=metric_key,
            trend=trend,
            trend_percent=round(trend_percent, 2),
            confidence=round(confidence, 2),
            direction=direction,
            velocity=round(velocity, 4)
        )

        logger.debug(
            f"[PREDICTOR] Trend analysis - {metric_key}: {trend} "
            f"({trend_percent:.1f}%), confidence {confidence:.0f}%"
        )

        return analysis

    def predict_memory_pressure(self, memory_history: List[float],
                               critical_threshold: float = 90.0) -> Prediction:
        """
        Predict when memory will become problematic
        Uses linear extrapolation of recent trend
        """
        if len(memory_history) < self.min_samples:
            return Prediction(
                prediction_type='memory_pressure',
                prediction='insufficient_data',
                confidence=0.0,
                time_to_event_minutes=None,
                recommended_action='collect_more_data'
            )

        recent = memory_history[-self.min_samples:]
        growth_per_sample = (recent[-1] - recent[0]) / len(recent)

        current_level = recent[-1]
        remaining_headroom = critical_threshold - current_level

        # Calculate time to critical
        if growth_per_sample > 0:
            samples_to_critical = remaining_headroom / growth_per_sample
            minutes_to_critical = (samples_to_critical / 60) if samples_to_critical > 0 else float('inf')

            if minutes_to_critical < 5:
                prediction = 'critical_memory_in_minutes'
                action = 'immediate_cleanup_required'
                confidence = 95.0
            elif minutes_to_critical < 30:
                prediction = 'high_memory_expected_soon'
                action = 'preemptive_cleanup'
                confidence = 90.0
            elif minutes_to_critical < 120:
                prediction = 'memory_pressure_anticipated'
                action = 'monitor_closely'
                confidence = 80.0
            else:
                prediction = 'stable_memory'
                action = 'no_action'
                confidence = 70.0

            time_to_event = minutes_to_critical if minutes_to_critical != float('inf') else None

        else:
            prediction = 'memory_stable'
            action = 'no_action'
            confidence = 90.0
            time_to_event = None

        return Prediction(
            prediction_type='memory_pressure',
            prediction=prediction,
            confidence=min(100, confidence),
            time_to_event_minutes=time_to_event,
            recommended_action=action
        )

    def predict_cache_hit_rate(self, cache_history: List[Dict]) -> Prediction:
        """
        Predict cache performance based on historical hit rates
        """
        if len(cache_history) < self.min_samples:
            return Prediction(
                prediction_type='cache_hit_rate',
                prediction='insufficient_data',
                confidence=0.0,
                time_to_event_minutes=None,
                recommended_action='collect_more_data'
            )

        recent_hit_rates = [c.get('hit_rate', 0) for c in cache_history[-self.min_samples:]]
        avg_hit_rate = statistics.mean(recent_hit_rates)
        recent_trend = recent_hit_rates[-1] - recent_hit_rates[0]

        if avg_hit_rate > 0.85:
            prediction = 'excellent_cache_performance'
            confidence = 95.0
        elif avg_hit_rate > 0.75:
            prediction = 'good_cache_performance'
            confidence = 90.0
        elif avg_hit_rate > 0.60:
            prediction = 'acceptable_cache_performance'
            confidence = 85.0
        else:
            prediction = 'poor_cache_performance'
            confidence = 80.0

        # Recommend action based on trend
        if recent_trend < -0.1:  # Declining
            action = 'increase_cache_size'
        elif recent_trend > 0.1:  # Improving
            action = 'maintain_current_settings'
        else:
            action = 'monitor_performance'

        return Prediction(
            prediction_type='cache_hit_rate',
            prediction=prediction,
            confidence=confidence,
            time_to_event_minutes=None,
            recommended_action=action
        )

    def predict_response_time(self, response_time_history: List[float],
                             warning_threshold: float = 1000.0) -> Prediction:
        """
        Predict response time trends and identify degradation
        """
        if len(response_time_history) < self.min_samples:
            return Prediction(
                prediction_type='response_time',
                prediction='insufficient_data',
                confidence=0.0,
                time_to_event_minutes=None,
                recommended_action='collect_more_data'
            )

        recent = response_time_history[-self.min_samples:]
        older = response_time_history[-(self.min_samples*2):-self.min_samples] if len(response_time_history) >= self.min_samples * 2 else recent

        recent_avg = statistics.mean(recent)
        older_avg = statistics.mean(older) if older and older != recent else recent_avg

        degradation_percent = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0

        current_level = recent[-1]

        if current_level > warning_threshold * 1.5:
            prediction = 'response_time_critical'
            action = 'immediate_investigation'
            confidence = 95.0
        elif current_level > warning_threshold:
            prediction = 'response_time_elevated'
            action = 'increase_resources'
            confidence = 90.0
        elif degradation_percent > 20:
            prediction = 'response_time_degrading'
            action = 'optimize_queries'
            confidence = 85.0
        else:
            prediction = 'response_time_healthy'
            action = 'maintain_current_config'
            confidence = 80.0

        return Prediction(
            prediction_type='response_time',
            prediction=prediction,
            confidence=confidence,
            time_to_event_minutes=None,
            recommended_action=action
        )

    def generate_prediction_report(self, metrics: Dict) -> Dict:
        """Generate comprehensive prediction report"""
        self.add_metric_sample(metrics)

        predictions = []

        # Extract metric histories
        memory_values = [
            h['metrics'].get('gpu_memory', 0)
            for h in self.performance_history[-60:]
        ]
        cache_history = [
            h['metrics'].get('cache_stats', {})
            for h in self.performance_history[-60:]
        ]
        response_times = [
            h['metrics'].get('latency_ms', 0)
            for h in self.performance_history[-60:]
        ]

        # Generate predictions
        if memory_values:
            mem_pred = self.predict_memory_pressure(memory_values)
            predictions.append(mem_pred)

        if cache_history:
            cache_pred = self.predict_cache_hit_rate(cache_history)
            predictions.append(cache_pred)

        if response_times:
            response_pred = self.predict_response_time(response_times)
            predictions.append(response_pred)

        self.predictions = predictions

        # Identify critical issues
        critical_predictions = [
            p for p in predictions
            if 'critical' in p.prediction.lower() or 'immediate' in p.recommended_action.lower()
        ]

        return {
            'timestamp': datetime.now().isoformat(),
            'sample_count': len(self.performance_history),
            'predictions': [
                {
                    'type': p.prediction_type,
                    'prediction': p.prediction,
                    'confidence_percent': p.confidence,
                    'time_to_event_minutes': p.time_to_event_minutes,
                    'recommended_action': p.recommended_action
                }
                for p in predictions
            ],
            'critical_issues': len(critical_predictions),
            'overall_system_health': self._calculate_system_health(predictions),
            'top_recommendation': self._get_top_recommendation(predictions)
        }

    def _calculate_system_health(self, predictions: List[Prediction]) -> Dict:
        """Calculate overall system health score"""
        if not predictions:
            return {'score': 100, 'status': 'unknown'}

        # Weight predictions by severity
        weighted_score = 0
        weights = 0

        for pred in predictions:
            if 'critical' in pred.prediction.lower():
                weight = 3
                score_impact = 20  # Critical issues reduce score by 20
            elif 'poor' in pred.prediction.lower() or 'high' in pred.prediction.lower():
                weight = 2
                score_impact = 10
            else:
                weight = 1
                score_impact = 5

            weighted_score += (100 - score_impact) * weight
            weights += weight

        health_score = weighted_score / weights if weights > 0 else 100
        health_score = min(100, max(0, health_score))

        if health_score >= 90:
            status = 'excellent'
        elif health_score >= 75:
            status = 'good'
        elif health_score >= 50:
            status = 'fair'
        else:
            status = 'poor'

        return {
            'score': round(health_score, 2),
            'status': status
        }

    def _get_top_recommendation(self, predictions: List[Prediction]) -> str:
        """Get the most important recommendation"""
        priority_actions = [
            'immediate_investigation',
            'immediate_cleanup_required',
            'increase_resources',
            'preemptive_cleanup',
            'optimize_queries',
            'increase_cache_size'
        ]

        for action in priority_actions:
            for pred in predictions:
                if pred.recommended_action == action:
                    return f"{action}: {pred.prediction}"

        return "Monitor system performance closely"


# Singleton instance
_predictor_instance: Optional[PredictivePerformanceOptimizer] = None


def get_predictive_optimizer() -> PredictivePerformanceOptimizer:
    """Get or create singleton instance"""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = PredictivePerformanceOptimizer()
        logger.info("[PREDICTOR] Predictive optimizer initialized")
    return _predictor_instance


def reset_predictor() -> None:
    """Reset predictor instance (for testing)"""
    global _predictor_instance
    _predictor_instance = None

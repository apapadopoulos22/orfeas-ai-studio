"""
A/B Testing Framework for ML Models
Module: ab_testing.py

Purpose: Implement A/B testing for comparing model versions in production.

Features:
  - Traffic splitting between model versions
  - Statistical significance testing
  - Performance metrics collection
  - Conversion tracking
  - Automated winner selection

Author: ORFEAS AI Studio - Phase 2 Task 1
Date: October 28, 2025
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
from pathlib import Path
import random

# Statistical testing
from scipy import stats

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TestStatus(Enum):
    """Status of an A/B test."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class TestMetrics:
    """Metrics collected during A/B test."""

    total_requests: int = 0
    successful_predictions: int = 0
    failed_predictions: int = 0
    average_confidence: float = 0.0
    average_latency_ms: float = 0.0
    accuracy: float = 0.0
    error_rate: float = 0.0
    user_conversions: int = 0

    def update(self, **kwargs):
        """Update metrics."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'total_requests': self.total_requests,
            'successful_predictions': self.successful_predictions,
            'failed_predictions': self.failed_predictions,
            'average_confidence': round(self.average_confidence, 4),
            'average_latency_ms': round(self.average_latency_ms, 2),
            'accuracy': round(self.accuracy, 4),
            'error_rate': round(self.error_rate, 4),
            'user_conversions': self.user_conversions,
        }


@dataclass
class TestVariant:
    """A single variant in an A/B test."""

    variant_id: str
    model_version: str
    traffic_percentage: float  # 0-100
    metrics: TestMetrics = field(default_factory=TestMetrics)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'variant_id': self.variant_id,
            'model_version': self.model_version,
            'traffic_percentage': self.traffic_percentage,
            'metrics': self.metrics.to_dict(),
            'created_at': self.created_at,
        }


@dataclass
class ABTest:
    """Represents an A/B test experiment."""

    test_id: str
    test_name: str
    variants: Dict[str, TestVariant] = field(default_factory=dict)
    status: str = TestStatus.ACTIVE.value
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    winner: Optional[str] = None  # variant_id of winner
    significance_level: float = 0.05  # p-value threshold
    min_sample_size: int = 1000  # Minimum samples before significance test

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'test_id': self.test_id,
            'test_name': self.test_name,
            'status': self.status,
            'variants': {v_id: v.to_dict() for v_id, v in self.variants.items()},
            'created_at': self.created_at,
            'completed_at': self.completed_at,
            'winner': self.winner,
            'significance_level': self.significance_level,
            'min_sample_size': self.min_sample_size,
        }


class ABTestingFramework:
    """Framework for managing A/B tests."""

    def __init__(self, base_dir: str = "./ab_tests"):
        """Initialize A/B testing framework."""
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.tests: Dict[str, ABTest] = {}
        self.test_history_file = self.base_dir / "test_history.json"

        self._load_history()
        logger.info(f"✅ A/B Testing Framework initialized: {base_dir}")

    def _load_history(self) -> None:
        """Load test history from disk."""
        if self.test_history_file.exists():
            try:
                with open(self.test_history_file, 'r') as f:
                    data = json.load(f)
                    for test_data in data.get('tests', []):
                        test = ABTest(
                            test_id=test_data['test_id'],
                            test_name=test_data['test_name'],
                            status=test_data.get('status', TestStatus.ACTIVE.value),
                            created_at=test_data['created_at'],
                            completed_at=test_data.get('completed_at'),
                            winner=test_data.get('winner'),
                            significance_level=test_data.get(
                                'significance_level', 0.05
                            ),
                            min_sample_size=test_data.get('min_sample_size', 1000),
                        )
                        self.tests[test.test_id] = test
                logger.info(f"✅ Loaded {len(self.tests)} tests from history")
            except Exception as e:
                logger.error(f"❌ Failed to load history: {e}")

    def _save_history(self) -> None:
        """Save test history to disk."""
        data = {
            'tests': [t.to_dict() for t in self.tests.values()],
            'last_updated': datetime.now().isoformat(),
        }

        with open(self.test_history_file, 'w') as f:
            json.dump(data, f, indent=2)

    def create_test(
        self,
        test_name: str,
        model_versions: Dict[str, float],  # {version_id: traffic_percentage}
        min_sample_size: int = 1000,
        significance_level: float = 0.05,
    ) -> str:
        """
        Create a new A/B test.

        Args:
            test_name: Name of the test
            model_versions: Dict mapping version IDs to traffic percentages
            min_sample_size: Minimum samples before significance testing
            significance_level: P-value threshold (alpha)

        Returns:
            Test ID
        """
        # Validate traffic percentages sum to 100
        total_traffic = sum(model_versions.values())
        if not (99.5 <= total_traffic <= 100.5):  # Allow small rounding errors
            raise ValueError(
                f"Traffic percentages must sum to 100, got {total_traffic}"
            )

        # Generate test ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_id = f"test_{timestamp}_{random.randint(1000, 9999)}"

        # Create test
        test = ABTest(
            test_id=test_id,
            test_name=test_name,
            min_sample_size=min_sample_size,
            significance_level=significance_level,
        )

        # Add variants
        for i, (version_id, traffic_pct) in enumerate(model_versions.items()):
            variant_id = f"variant_{i}"
            variant = TestVariant(
                variant_id=variant_id,
                model_version=version_id,
                traffic_percentage=traffic_pct,
            )
            test.variants[variant_id] = variant

        self.tests[test_id] = test
        self._save_history()

        logger.info(f"✅ Created test: {test_id} ({test_name})")
        logger.info(
            f"  Variants: {', '.join([f'{v.model_version} ({v.traffic_percentage}%)' for v in test.variants.values()])}"
        )

        return test_id

    def select_variant(self, test_id: str) -> Optional[str]:
        """
        Select a variant for a user based on traffic split.

        Args:
            test_id: Test ID

        Returns:
            Variant ID to use for this user
        """
        if test_id not in self.tests:
            logger.error(f"❌ Test not found: {test_id}")
            return None

        test = self.tests[test_id]
        if test.status != TestStatus.ACTIVE.value:
            logger.warning(f"⚠️ Test not active: {test_id}")
            return None

        # Generate random number 0-100
        rand = random.uniform(0, 100)
        cumulative = 0

        for variant in test.variants.values():
            cumulative += variant.traffic_percentage
            if rand <= cumulative:
                return variant.variant_id

        # Fallback to last variant
        return list(test.variants.keys())[-1]

    def record_prediction(
        self,
        test_id: str,
        variant_id: str,
        confidence: float,
        latency_ms: float,
        was_correct: bool,
    ) -> None:
        """
        Record a prediction for metrics tracking.

        Args:
            test_id: Test ID
            variant_id: Variant ID used
            confidence: Model confidence score
            latency_ms: Prediction latency
            was_correct: Whether prediction was correct
        """
        if test_id not in self.tests or variant_id not in self.tests[test_id].variants:
            logger.error(
                f"❌ Invalid test/variant: {test_id}/{variant_id}"
            )
            return

        metrics = self.tests[test_id].variants[variant_id].metrics
        metrics.total_requests += 1

        if was_correct:
            metrics.successful_predictions += 1
        else:
            metrics.failed_predictions += 1

        # Update averages (simplified exponential moving average)
        alpha = 0.1  # Learning rate
        metrics.average_confidence = (
            alpha * confidence + (1 - alpha) * metrics.average_confidence
        )
        metrics.average_latency_ms = (
            alpha * latency_ms + (1 - alpha) * metrics.average_latency_ms
        )

        if metrics.total_requests > 0:
            metrics.accuracy = (
                metrics.successful_predictions / metrics.total_requests
            )
            metrics.error_rate = (
                metrics.failed_predictions / metrics.total_requests
            )

    def record_conversion(self, test_id: str, variant_id: str) -> None:
        """Record a user conversion."""
        if test_id not in self.tests or variant_id not in self.tests[test_id].variants:
            return

        self.tests[test_id].variants[variant_id].metrics.user_conversions += 1

    def get_test_status(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a test."""
        if test_id not in self.tests:
            return None

        test = self.tests[test_id]
        return test.to_dict()

    def check_significance(self, test_id: str) -> Dict[str, Any]:
        """
        Check statistical significance between variants.

        Returns chi-square test results comparing variant accuracies.
        """
        if test_id not in self.tests:
            return {'error': 'Test not found'}

        test = self.tests[test_id]
        variants = list(test.variants.values())

        if len(variants) < 2:
            return {'error': 'Need at least 2 variants'}

        # Check sample sizes
        min_samples = min(v.metrics.total_requests for v in variants)
        if min_samples < test.min_sample_size:
            return {
                'ready': False,
                'min_samples': test.min_sample_size,
                'current_min': min_samples,
                'message': f"Need {test.min_sample_size - min_samples} more samples",
            }

        # Perform chi-square test
        observed = []
        for variant in variants:
            observed.append([
                variant.metrics.successful_predictions,
                variant.metrics.failed_predictions,
            ])

        try:
            chi2, p_value, dof, expected = stats.chi2_contingency(observed)

            result = {
                'ready': True,
                'chi_square': round(chi2, 4),
                'p_value': round(p_value, 6),
                'dof': dof,
                'significance_level': test.significance_level,
                'is_significant': p_value < test.significance_level,
                'variants': {
                    v.variant_id: {
                        'accuracy': round(v.metrics.accuracy, 4),
                        'samples': v.metrics.total_requests,
                    }
                    for v in variants
                },
            }

            return result
        except Exception as e:
            logger.error(f"❌ Significance test failed: {e}")
            return {'error': str(e)}

    def declare_winner(self, test_id: str) -> Optional[str]:
        """
        Declare winner based on accuracy.

        Returns:
            Variant ID of winner
        """
        if test_id not in self.tests:
            return None

        test = self.tests[test_id]

        # Check significance
        sig = self.check_significance(test_id)
        if not sig.get('ready', False) or not sig.get('is_significant', False):
            logger.warning(f"⚠️ Not statistically significant yet: {test_id}")
            return None

        # Find variant with highest accuracy
        winner_variant = max(
            test.variants.values(),
            key=lambda v: v.metrics.accuracy,
        )

        test.winner = winner_variant.variant_id
        test.status = TestStatus.COMPLETED.value
        test.completed_at = datetime.now().isoformat()

        self._save_history()

        logger.info(
            f"✅ Winner declared: {winner_variant.variant_id} "
            f"(accuracy: {winner_variant.metrics.accuracy:.4f})"
        )

        return winner_variant.variant_id

    def get_all_tests(
        self,
        status: Optional[TestStatus] = None,
    ) -> List[Dict[str, Any]]:
        """Get all tests, optionally filtered by status."""
        tests = list(self.tests.values())

        if status:
            tests = [t for t in tests if t.status == status.value]

        return [t.to_dict() for t in tests]

    def get_summary(self) -> Dict[str, Any]:
        """Get A/B testing summary."""
        active_tests = [t for t in self.tests.values() if t.status == TestStatus.ACTIVE.value]
        completed_tests = [t for t in self.tests.values() if t.status == TestStatus.COMPLETED.value]

        return {
            'total_tests': len(self.tests),
            'active_tests': len(active_tests),
            'completed_tests': len(completed_tests),
            'active_test_ids': [t.test_id for t in active_tests],
            'recent_winner': (
                completed_tests[-1].winner
                if completed_tests else None
            ),
        }


# Singleton instance
_ab_framework: Optional[ABTestingFramework] = None


def get_ab_testing_framework(
    base_dir: str = "./ab_tests"
) -> ABTestingFramework:
    """Get or create A/B testing framework singleton."""
    global _ab_framework
    if _ab_framework is None:
        _ab_framework = ABTestingFramework(base_dir)
    return _ab_framework


if __name__ == "__main__":
    # Example usage and testing
    logger.info("=" * 70)
    logger.info("A/B TESTING FRAMEWORK - DEMO")
    logger.info("=" * 70)

    # Create framework
    logger.info("\n🧪 Creating A/B testing framework...")
    framework = get_ab_testing_framework("./test_ab")

    # Create test
    logger.info("\n🆕 Creating test...")
    test_id = framework.create_test(
        test_name="Model Accuracy Comparison",
        model_versions={
            "iris_classifier_v1": 50.0,  # 50% traffic
            "iris_classifier_v2": 50.0,  # 50% traffic
        },
        min_sample_size=100,
    )

    # Simulate traffic
    logger.info("\n📊 Simulating traffic...")
    variant_accuracies = {
        'variant_0': 0.92,  # 92% accuracy
        'variant_1': 0.95,  # 95% accuracy
    }

    for _ in range(150):
        variant_id = framework.select_variant(test_id)
        accuracy = variant_accuracies[variant_id]
        was_correct = random.random() < accuracy

        framework.record_prediction(
            test_id=test_id,
            variant_id=variant_id,
            confidence=0.87,
            latency_ms=42.0,
            was_correct=was_correct,
        )

    # Check significance
    logger.info("\n🔍 Checking statistical significance...")
    sig_result = framework.check_significance(test_id)
    logger.info(f"  Ready: {sig_result.get('ready', False)}")
    if sig_result.get('ready'):
        logger.info(f"  Chi-square: {sig_result.get('chi_square')}")
        logger.info(f"  P-value: {sig_result.get('p_value')}")
        logger.info(f"  Significant: {sig_result.get('is_significant')}")

    # Declare winner
    logger.info("\n🏆 Declaring winner...")
    winner = framework.declare_winner(test_id)
    if winner:
        logger.info(f"  Winner: {winner}")

    # Test status
    logger.info("\n📋 Test status:")
    status = framework.get_test_status(test_id)
    logger.info(f"  Test ID: {status['test_id']}")
    logger.info(f"  Status: {status['status']}")
    logger.info(f"  Winner: {status.get('winner')}")

    # Summary
    logger.info("\n📈 A/B Testing Summary:")
    summary = framework.get_summary()
    for key, value in summary.items():
        logger.info(f"  {key}: {value}")

    logger.info("\n✅ A/B Testing Framework Demo Complete!")
    logger.info("=" * 70)

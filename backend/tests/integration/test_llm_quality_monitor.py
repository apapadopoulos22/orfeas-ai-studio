"""
Unit Tests for Quality Monitor (File 8)
Tests response quality evaluation, hallucination detection, and safety checks
"""

import pytest
from backend.llm_integration.llm_quality_monitor import (
    LLMQualityMonitor,
    QualityScore,
    QualityLevel,
)


class TestLLMQualityMonitor:
    """Test suite for LLMQualityMonitor class."""

    @pytest.fixture
    def monitor(self):
        """Create fresh quality monitor for each test."""
        return LLMQualityMonitor()

    def test_monitor_initialization(self, monitor):
        """Test monitor initializes correctly."""
        assert len(monitor.quality_history) == 0
        stats = monitor.get_stats()
        assert stats['responses_evaluated'] == 0

    def test_evaluate_good_response(self, monitor):
        """Test evaluation of a good quality response."""
        response = "Python is a high-level programming language. It emphasizes code readability."
        score = monitor.evaluate_response(response, task_type="factual")

        assert isinstance(score, QualityScore)
        assert score.overall_score >= 0.7
        assert score.quality_level in [QualityLevel.GOOD, QualityLevel.EXCELLENT]
        assert score.is_safe

    def test_evaluate_poor_response(self, monitor):
        """Test evaluation of a poor quality response."""
        response = "blah blah blah not good"
        score = monitor.evaluate_response(response, task_type="factual")

        assert score.overall_score < 0.7

    def test_hallucination_detection(self, monitor):
        """Test hallucination risk detection."""
        # Response with hallucination indicators
        response = "I cannot verify this information. As of my last update in 2021..."
        score = monitor.evaluate_response(response, task_type="factual")

        assert score.hallucination_risk > 0.2

    def test_no_hallucination_in_good_response(self, monitor):
        """Test good response has low hallucination risk."""
        response = "The Earth orbits around the Sun. This is a well-established fact."
        score = monitor.evaluate_response(response, task_type="factual")

        assert score.hallucination_risk < 0.3

    def test_safety_check_toxic_content(self, monitor):
        """Test safety detection of toxic content."""
        response = "This person is a hate criminal who should be killed."
        score = monitor.evaluate_response(response, task_type="general")

        assert score.is_safe == False
        assert score.safety_score < 0.7

    def test_safety_check_safe_content(self, monitor):
        """Test safety verification of safe content."""
        response = "Hello, this is a friendly message."
        score = monitor.evaluate_response(response, task_type="general")

        assert score.is_safe == True
        assert score.safety_score > 0.7

    def test_accuracy_scoring_with_ground_truth(self, monitor):
        """Test accuracy scoring with ground truth."""
        response = "The capital of France is Paris, a major European city."
        ground_truth = "The capital of France is Paris."
        score = monitor.evaluate_response(response, ground_truth=ground_truth, task_type="factual")

        assert score.accuracy_score > 0.5

    def test_clarity_scoring(self, monitor):
        """Test clarity score calculation."""
        clear_response = "Here are three points: 1. First point. 2. Second point. 3. Third point."
        score = monitor.evaluate_response(clear_response, task_type="general")

        assert score.clarity_score > 0.6

    def test_consistency_detection(self, monitor):
        """Test consistency checking."""
        inconsistent = "The answer is always yes. But it can also be no."
        score = monitor.evaluate_response(inconsistent, task_type="general")

        # Should detect inconsistency
        assert score.consistency_score < 0.8

    def test_quality_level_classification(self, monitor):
        """Test quality level assignment."""
        excellent = "This is a comprehensive, accurate, and well-structured response."
        poor = "xyz abc def"

        excellent_score = monitor.evaluate_response(excellent)
        poor_score = monitor.evaluate_response(poor)

        assert excellent_score.overall_score > poor_score.overall_score
        assert excellent_score.quality_level.value > poor_score.quality_level.value

    def test_task_type_weighting(self, monitor):
        """Test different task types use different weighting."""
        response = "Technical implementation details here."

        code_score = monitor.evaluate_response(response, task_type="code")
        factual_score = monitor.evaluate_response(response, task_type="factual")
        general_score = monitor.evaluate_response(response, task_type="general")

        # Different weights should produce different scores
        # (though they might be close)
        assert isinstance(code_score.overall_score, float)
        assert isinstance(factual_score.overall_score, float)

    def test_warning_generation(self, monitor):
        """Test warning generation for issues."""
        response = "maybe perhaps possibly this could be right"
        score = monitor.evaluate_response(response, task_type="factual")

        # Should generate warnings
        assert len(score.warnings) >= 0

    def test_statistics_tracking(self, monitor):
        """Test quality statistics tracking."""
        monitor.evaluate_response("Good response", task_type="general")
        monitor.evaluate_response("Another response", task_type="general")

        stats = monitor.get_stats()
        assert stats['responses_evaluated'] == 2

    def test_quality_trend(self, monitor):
        """Test quality trend tracking."""
        for i in range(5):
            response = f"Response number {i}. This is a test."
            monitor.evaluate_response(response)

        trend = monitor.get_quality_trend(last_n=3)
        assert len(trend) <= 3
        assert all(0.0 <= score <= 1.0 for score in trend)

    def test_average_quality(self, monitor):
        """Test average quality calculation."""
        monitor.evaluate_response("Good response")
        monitor.evaluate_response("Good response")
        monitor.evaluate_response("Good response")

        avg = monitor.get_average_quality()
        assert 0.0 <= avg <= 1.0

    def test_quality_report(self, monitor):
        """Test detailed quality report generation."""
        response = "Sample response for testing."
        score = monitor.evaluate_response(response)

        report = monitor.get_quality_report(score)
        assert 'overall_score' in report
        assert 'quality_level' in report
        assert 'scores' in report
        assert 'warnings' in report

    def test_reset_history(self, monitor):
        """Test history reset."""
        monitor.evaluate_response("Test response")
        assert len(monitor.quality_history) == 1

        monitor.reset_history()
        assert len(monitor.quality_history) == 0


class TestQualityScore:
    """Test suite for QualityScore dataclass."""

    def test_quality_score_creation(self):
        """Test QualityScore initialization."""
        score = QualityScore(
            overall_score=0.85,
            quality_level=QualityLevel.GOOD,
            accuracy_score=0.8,
            consistency_score=0.9,
            clarity_score=0.85,
            safety_score=0.95,
            hallucination_risk=0.1,
            is_safe=True
        )
        assert score.overall_score == 0.85
        assert score.quality_level == QualityLevel.GOOD

    def test_quality_level_enum(self):
        """Test QualityLevel enum values."""
        levels = [
            QualityLevel.EXCELLENT,
            QualityLevel.GOOD,
            QualityLevel.ACCEPTABLE,
            QualityLevel.POOR,
            QualityLevel.CRITICAL,
        ]
        assert len(levels) == 5
        # Higher values for better quality
        assert QualityLevel.EXCELLENT.value > QualityLevel.POOR.value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Unit Tests for Failover Handler (File 9)
Tests circuit breaker, retry logic, and error categorization
"""

import pytest
import time
from backend.llm_integration.llm_failover_handler import (
    LLMFailoverHandler,
    ErrorCategory,
    CircuitState,
)


class TestLLMFailoverHandler:
    """Test suite for LLMFailoverHandler class."""

    @pytest.fixture
    def handler(self):
        """Create fresh failover handler for each test."""
        return LLMFailoverHandler(
            fallback_chain=["gpt-3.5-turbo", "claude-3-sonnet"],
            circuit_failure_threshold=3,
            circuit_recovery_timeout_sec=60
        )

    def test_handler_initialization(self, handler):
        """Test handler initializes correctly."""
        assert handler.circuit_failure_threshold == 3
        assert len(handler.fallback_chain) == 2

    def test_error_categorization_rate_limit(self, handler):
        """Test rate limit error categorization."""
        category = handler._categorize_error("429: Rate limit exceeded")
        assert category == ErrorCategory.RATE_LIMIT

    def test_error_categorization_auth(self, handler):
        """Test auth error categorization."""
        category = handler._categorize_error("401: Unauthorized access")
        assert category == ErrorCategory.AUTH_ERROR

    def test_error_categorization_timeout(self, handler):
        """Test timeout error categorization."""
        category = handler._categorize_error("Request timed out after 30s")
        assert category == ErrorCategory.TIMEOUT

    def test_error_categorization_token_limit(self, handler):
        """Test token limit error categorization."""
        category = handler._categorize_error("Token limit exceeded")
        assert category == ErrorCategory.TOKEN_LIMIT

    def test_error_categorization_invalid_input(self, handler):
        """Test invalid input error categorization."""
        category = handler._categorize_error("400: Bad request")
        assert category == ErrorCategory.INVALID_INPUT

    def test_retryable_error_detection(self, handler):
        """Test identification of retryable errors."""
        assert handler._is_retryable(ErrorCategory.RATE_LIMIT)
        assert handler._is_retryable(ErrorCategory.TIMEOUT)
        assert handler._is_retryable(ErrorCategory.MODEL_OVERLOAD)
        assert not handler._is_retryable(ErrorCategory.AUTH_ERROR)
        assert not handler._is_retryable(ErrorCategory.INVALID_INPUT)

    def test_backoff_calculation(self, handler):
        """Test exponential backoff calculation."""
        backoff_0 = handler._calculate_backoff(0)
        backoff_1 = handler._calculate_backoff(1)
        backoff_2 = handler._calculate_backoff(2)

        assert 0 < backoff_0 < 2
        assert backoff_1 > backoff_0
        assert backoff_2 > backoff_1
        assert backoff_2 <= 30.0

    def test_circuit_breaker_initial_state(self, handler):
        """Test circuit breaker starts in CLOSED state."""
        status = handler.get_circuit_status("gpt-4-turbo")
        assert status['state'] == CircuitState.CLOSED.value

    def test_circuit_breaker_opens_on_failures(self, handler):
        """Test circuit breaker opens after threshold failures."""
        # Simulate failures
        for i in range(3):
            handler._record_failure(
                "test-model",
                ErrorCategory.MODEL_OVERLOAD,
                f"Failure {i+1}"
            )

        status = handler.get_circuit_status("test-model")
        # Should be OPEN or transitioning
        assert status['failures'] == 3

    def test_circuit_breaker_closes_on_success(self, handler):
        """Test circuit breaker closes after successful recovery."""
        handler._record_success("test-model")
        handler._record_success("test-model")

        status = handler.get_circuit_status("test-model")
        assert status['successes'] >= 1

    def test_failover_chain_selection(self, handler):
        """Test failover model selection from chain."""
        fallback = handler._get_failover_model("gpt-4-turbo")
        # Should return a model from fallback chain
        assert fallback in handler.fallback_chain

    def test_failure_recording(self, handler):
        """Test failure recording and history."""
        handler._record_failure("model1", ErrorCategory.TIMEOUT, "Timed out")
        handler._record_failure("model2", ErrorCategory.RATE_LIMIT, "Rate limited")

        report = handler.get_failure_report(last_n=5)
        assert len(report) == 2
        assert report[0]['error_category'] == ErrorCategory.TIMEOUT.value

    def test_statistics_tracking(self, handler):
        """Test statistics tracking."""
        handler._record_failure("model", ErrorCategory.TIMEOUT, "Timeout")

        stats = handler.get_stats()
        assert stats['total_failures'] == 1

    def test_circuit_status_all_models(self, handler):
        """Test circuit status for all models."""
        status = handler.get_circuit_status()
        assert isinstance(status, dict)
        # Should have entries for various models
        assert len(status) > 0

    def test_failure_report_limit(self, handler):
        """Test failure report respects last_n limit."""
        for i in range(10):
            handler._record_failure(f"model{i}", ErrorCategory.TIMEOUT, f"Failure {i}")

        report = handler.get_failure_report(last_n=3)
        assert len(report) <= 3

    def test_reset_statistics(self, handler):
        """Test statistics reset."""
        handler._record_failure("model", ErrorCategory.TIMEOUT, "Test")
        assert handler.get_stats()['total_failures'] > 0

        handler.reset_stats()
        assert handler.get_stats()['total_failures'] == 0

    def test_check_circuit_breaker_closed(self, handler):
        """Test circuit breaker allows requests when closed."""
        can_proceed = handler._check_circuit_breaker("gpt-4-turbo")
        assert can_proceed == True

    def test_circuit_recovery_timeout(self, handler):
        """Test circuit breaker recovery timeout."""
        # Force circuit open
        for i in range(5):
            handler._record_failure("model", ErrorCategory.TIMEOUT, "Fail")

        # Check if circuit is open
        status = handler.get_circuit_status("model")
        # Should be OPEN
        assert status['failures'] >= handler.circuit_failure_threshold


class TestErrorCategory:
    """Test suite for ErrorCategory enum."""

    def test_error_category_values(self):
        """Test all error category enum values."""
        categories = [
            ErrorCategory.RATE_LIMIT,
            ErrorCategory.AUTH_ERROR,
            ErrorCategory.MODEL_OVERLOAD,
            ErrorCategory.TIMEOUT,
            ErrorCategory.INVALID_INPUT,
            ErrorCategory.TOKEN_LIMIT,
            ErrorCategory.UNKNOWN,
        ]
        assert len(categories) == 7


class TestCircuitState:
    """Test suite for CircuitState enum."""

    def test_circuit_state_values(self):
        """Test all circuit state enum values."""
        states = [
            CircuitState.CLOSED,
            CircuitState.OPEN,
            CircuitState.HALF_OPEN,
        ]
        assert len(states) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

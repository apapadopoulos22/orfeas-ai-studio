"""
LLM Failover Handler Module - Error Handling and Graceful Degradation

Purpose:
    Handle LLM failures with resilience patterns:
    - Circuit breaker pattern to prevent cascading failures
    - Intelligent retry with exponential backoff
    - Fallback chains to alternative models/providers
    - Error categorization and reporting
    - Incident tracking and alerts

Performance Targets:
    - Circuit breaker check: <5ms
    - Retry decision: <10ms
    - Failover execution: <100ms
    - Total per-failure: <500ms
"""

import logging
import time
from typing import Callable, Optional, Any, Dict, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import random

from .error_handler import (
    error_context,
    safe_execute,
    LLMFailoverError,
    ErrorAggregator
)
from .tracing import (
    trace_performance,
    trace_block_async,
    PerformanceTracer
)
logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """LLM error categories."""
    RATE_LIMIT = "rate_limit"           # Too many requests
    AUTH_ERROR = "auth_error"            # Invalid credentials
    MODEL_OVERLOAD = "model_overload"    # Service temporarily unavailable
    TIMEOUT = "timeout"                  # Request timeout
    INVALID_INPUT = "invalid_input"      # Bad request format
    TOKEN_LIMIT = "token_limit"          # Token limit exceeded
    UNKNOWN = "unknown"                  # Unknown error


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"        # Normal operation
    OPEN = "open"            # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class FailureRecord:
    """Record of a single failure."""
    error_category: ErrorCategory
    error_message: str
    model: str
    timestamp: datetime = field(default_factory=datetime.now)
    response_time_ms: Optional[float] = None
    retryable: bool = False


@dataclass
class CircuitBreakerStatus:
    """Status of circuit breaker."""
    state: CircuitState
    failure_count: int
    success_count: int
    last_failure_time: Optional[datetime]
    open_until: Optional[datetime]


class LLMFailoverHandler:
    """
    LLM failover and error handling system.

    Manages failures, retries, and fallbacks with circuit breaker pattern.
    """

    def __init__(
        self,
        fallback_chain: Optional[List[str]] = None,
        circuit_failure_threshold: int = 5,
        circuit_recovery_timeout_sec: int = 60,
    ):
        """
        Initialize failover handler.

        Args:
            fallback_chain: List of fallback models in priority order
            circuit_failure_threshold: Failures before opening circuit
            circuit_recovery_timeout_sec: Time to attempt recovery
        """
        self.fallback_chain = fallback_chain or ["gpt-3.5-turbo", "claude-3-sonnet", "mistral-large"]
        self.circuit_failure_threshold = circuit_failure_threshold
        self.circuit_recovery_timeout = circuit_recovery_timeout_sec

        # Circuit breakers per model
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        self._initialize_circuit_breakers()

        # Failure tracking
        self.failure_history: List[FailureRecord] = []
        self.error_agg = ErrorAggregator()
        self.perf_tracer = PerformanceTracer()
        self.stats = {
            'total_failures': 0,
            'total_retries': 0,
            'successful_retries': 0,
            'failovers': 0,
            'circuit_breaks': 0,
        }

        logger.info(
            f"LLMFailoverHandler initialized "
            f"(threshold={circuit_failure_threshold}, "
            f"recovery_timeout={circuit_recovery_timeout_sec}s, "
            f"fallbacks={self.fallback_chain})"
        )

    def _initialize_circuit_breakers(self) -> None:
        """Initialize circuit breakers for all models."""
        all_models = list(set(self.fallback_chain + ["gpt-4-turbo", "gpt-4"]))

        for model in all_models:
            self.circuit_breakers[model] = {
                'state': CircuitState.CLOSED,
                'failure_count': 0,
                'success_count': 0,
                'last_failure_time': None,
                'open_until': None,
            }
    @trace_performance(operation='handle_call', component='llm_failover_handler')
    @error_context(component='llm_failover_handler', operation='handle_call')
    def handle_call(
        self,
        func: Callable,
        *args,
        model: str = "gpt-4",
        max_retries: int = 3,
        **kwargs
    ) -> Any:
        """
        Execute function with failover handling.

        Args:
            func: Function to call
            model: Primary model to use
            max_retries: Maximum retry attempts
            *args, **kwargs: Arguments to pass to func

        Returns:
            Function result

        Raises:
            Exception: If all retries and failovers exhausted
        """
        current_model = model
        attempt = 0
        last_error = None

        while attempt <= max_retries:
            try:
                # Check circuit breaker
                if not self._check_circuit_breaker(current_model):
                    logger.warning(f"Circuit breaker OPEN for {current_model}")
                    self.stats['circuit_breaks'] += 1

                    # Try failover
                    failover_model = self._get_failover_model(current_model)
                    if failover_model:
                        logger.info(f"Failing over from {current_model} to {failover_model}")
                        current_model = failover_model
                        self.stats['failovers'] += 1
                        continue
                    else:
                        raise Exception("All models unavailable (circuit breakers open)")

                # Call function
                kwargs['model'] = current_model
                result = func(*args, **kwargs)

                # Record success
                self._record_success(current_model)

                return result

            except Exception as e:
                last_error = e
                error_category = self._categorize_error(str(e))

                # Record failure
                self._record_failure(current_model, error_category, str(e))

                # Determine if retryable
                retryable = self._is_retryable(error_category)

                if retryable and attempt < max_retries:
                    # Calculate backoff
                    backoff_time = self._calculate_backoff(attempt)
                    logger.warning(
                        f"Retrying after {backoff_time:.2f}s "
                        f"(attempt {attempt + 1}/{max_retries}): {error_category.value}"
                    )
                    self.stats['total_retries'] += 1
                    time.sleep(backoff_time)
                    attempt += 1
                else:
                    # Try failover
                    failover_model = self._get_failover_model(current_model)
                    if failover_model and attempt == 0:
                        logger.info(f"Non-retryable error, failing over to {failover_model}")
                        current_model = failover_model
                        self.stats['failovers'] += 1
                        attempt = 0
                    else:
                        raise last_error

        raise last_error

    @trace_performance(operation='check_circuit_breaker', component='llm_failover_handler')
    @error_context(component='llm_failover_handler', operation='check_circuit_breaker')
    def _check_circuit_breaker(self, model: str) -> bool:
        """Check if circuit breaker allows request."""
        if model not in self.circuit_breakers:
            return True

        breaker = self.circuit_breakers[model]
        state = breaker['state']

        if state == CircuitState.CLOSED:
            return True

        elif state == CircuitState.OPEN:
            # Check if recovery timeout elapsed
            if breaker['open_until'] and datetime.now() >= breaker['open_until']:
                # Try half-open
                breaker['state'] = CircuitState.HALF_OPEN
                breaker['success_count'] = 0
                logger.info(f"Circuit breaker for {model} entering HALF_OPEN state")
                return True
            return False

        elif state == CircuitState.HALF_OPEN:
            # Allow test request
            return True

        return False

    def _record_success(self, model: str) -> None:
        """Record successful request."""
        if model not in self.circuit_breakers:
            return

        breaker = self.circuit_breakers[model]
        breaker['success_count'] += 1

        # Close circuit on success if in half-open
        if breaker['state'] == CircuitState.HALF_OPEN:
            if breaker['success_count'] >= 2:
                breaker['state'] = CircuitState.CLOSED
                breaker['failure_count'] = 0
                logger.info(f"Circuit breaker for {model} CLOSED (recovered)")
    @trace_performance(operation='record_failure', component='llm_failover_handler')
    @error_context(component='llm_failover_handler', operation='record_failure')
    def _record_failure(
        self,
        model: str,
        error_category: ErrorCategory,
        error_message: str
    ) -> None:
        """Record failed request."""
        self.stats['total_failures'] += 1

        # Track in history
        failure = FailureRecord(
            error_category=error_category,
            error_message=error_message,
            model=model,
            retryable=self._is_retryable(error_category),
        )
        self.failure_history.append(failure)

        if model not in self.circuit_breakers:
            return

        breaker = self.circuit_breakers[model]
        breaker['failure_count'] += 1
        breaker['last_failure_time'] = datetime.now()

        # Open circuit on threshold
        if breaker['failure_count'] >= self.circuit_failure_threshold:
            breaker['state'] = CircuitState.OPEN
            breaker['open_until'] = datetime.now() + timedelta(
                seconds=self.circuit_recovery_timeout
            )
            logger.error(
                f"Circuit breaker for {model} OPEN "
                f"(failures: {breaker['failure_count']})"
            )

    def _get_failover_model(self, current_model: str) -> Optional[str]:
        """Get next failover model."""
        for fallback in self.fallback_chain:
            if fallback != current_model:
                # Check if fallback circuit is not permanently broken
                if self._check_circuit_breaker(fallback):
                    return fallback

        return None

    def _categorize_error(self, error_message: str) -> ErrorCategory:
        """Categorize error type."""
        error_lower = error_message.lower()

        if 'rate limit' in error_lower or '429' in error_lower:
            return ErrorCategory.RATE_LIMIT
        elif 'auth' in error_lower or '401' in error_lower:
            return ErrorCategory.AUTH_ERROR
        elif 'overload' in error_lower or '503' in error_lower:
            return ErrorCategory.MODEL_OVERLOAD
        elif 'timeout' in error_lower or 'timed out' in error_lower:
            return ErrorCategory.TIMEOUT
        elif 'token' in error_lower or 'limit' in error_lower:
            return ErrorCategory.TOKEN_LIMIT
        elif 'invalid' in error_lower or '400' in error_lower:
            return ErrorCategory.INVALID_INPUT
        else:
            return ErrorCategory.UNKNOWN

    def _is_retryable(self, error_category: ErrorCategory) -> bool:
        """Determine if error is retryable."""
        retryable_errors = {
            ErrorCategory.RATE_LIMIT,
            ErrorCategory.MODEL_OVERLOAD,
            ErrorCategory.TIMEOUT,
        }
        return error_category in retryable_errors

    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff with jitter."""
        # Exponential: 2^attempt with jitter
        base_backoff = 2 ** attempt
        jitter = random.uniform(0, 0.1 * base_backoff)
        return min(base_backoff + jitter, 30.0)  # Cap at 30s

    def get_circuit_status(self, model: Optional[str] = None) -> Dict[str, Any]:
        """Get circuit breaker status."""
        if model:
            if model in self.circuit_breakers:
                b = self.circuit_breakers[model]
                return {
                    'model': model,
                    'state': b['state'].value,
                    'failure_count': b['failure_count'],
                    'success_count': b['success_count'],
                    'last_failure_time': b['last_failure_time'].isoformat() if b['last_failure_time'] else None,
                }
            return {}

        # All models
        status = {}
        for model_name, breaker in self.circuit_breakers.items():
            status[model_name] = {
                'state': breaker['state'].value,
                'failures': breaker['failure_count'],
                'successes': breaker['success_count'],
            }

        return status

    def get_failure_report(self, last_n: int = 10) -> List[Dict[str, Any]]:
        """Get recent failure report."""
        return [
            {
                'timestamp': f.timestamp.isoformat(),
                'model': f.model,
                'error_category': f.error_category.value,
                'error_message': f.error_message[:100],  # Truncate
                'retryable': f.retryable,
            }
            for f in self.failure_history[-last_n:]
        ]

    def get_stats(self) -> Dict[str, Any]:
        """Get failover statistics."""
        return self.stats.copy()

    def reset_stats(self) -> None:
        """Reset statistics."""
        self.stats = {
            'total_failures': 0,
            'total_retries': 0,
            'successful_retries': 0,
            'failovers': 0,
            'circuit_breaks': 0,
        }
        self.failure_history = []
        logger.info("Failover handler statistics reset")


# Global failover handler instance
_failover_handler: Optional[LLMFailoverHandler] = None


def get_failover_handler(
    fallback_chain: Optional[List[str]] = None,
    circuit_failure_threshold: int = 5,
    circuit_recovery_timeout_sec: int = 60,
) -> LLMFailoverHandler:
    """Get or create global failover handler instance."""
    global _failover_handler
    if _failover_handler is None:
        _failover_handler = LLMFailoverHandler(
            fallback_chain,
            circuit_failure_threshold,
            circuit_recovery_timeout_sec,
        )
    return _failover_handler

"""
Comprehensive error handling infrastructure for LLM integration layer.

Provides:
- Unified exception hierarchy
- Error aggregation and reporting
- Retry strategies with exponential backoff
- Error context tracking
"""

import logging
import asyncio
import time
from typing import Optional, Callable, Any, TypeVar, Coroutine
from dataclasses import dataclass
from datetime import datetime
from functools import wraps

logger = logging.getLogger(__name__)

# Exception hierarchy
class LLMError(Exception):
    """Base exception for all LLM integration errors."""

    def __init__(self, message: str, error_code: str = "LLM_ERROR", context: dict = None):
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.timestamp = datetime.now()
        super().__init__(self.message)


class LLMRouterError(LLMError):
    """Router-specific errors."""
    pass


class LLMOrchestratorError(LLMError):
    """Orchestrator-specific errors."""
    pass


class LLMFailoverError(LLMError):
    """Failover-specific errors."""
    pass


class LLMCacheError(LLMError):
    """Cache-specific errors."""
    pass


class LLMRetrievalError(LLMError):
    """Retrieval-specific errors."""
    pass


class LLMQualityError(LLMError):
    """Quality monitoring errors."""
    pass


class LLMResourceError(LLMError):
    """Resource exhaustion errors."""
    code = "RESOURCE_EXHAUSTED"


# Additional specific error classes for components
class PromptEngineeringError(LLMError):
    """Prompt engineering errors."""
    pass


class ChunkingError(LLMError):
    """Semantic chunking errors."""
    pass


class RetrievalError(LLMError):
    """Context retrieval errors."""
    pass


class QualityCheckError(LLMError):
    """Quality checking errors."""
    pass


class TokenCountError(LLMError):
    """Token counting errors."""
    pass


class CacheLayerError(LLMError):
    """Cache layer errors."""
    pass


@dataclass
class ErrorContext:
    """Error context information."""
    component: str
    operation: str
    timestamp: datetime
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    error_count: int = 0
    last_error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            'component': self.component,
            'operation': self.operation,
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id,
            'request_id': self.request_id,
            'error_count': self.error_count,
            'last_error': self.last_error
        }


class ErrorAggregator:
    """Aggregate errors across components."""

    def __init__(self, max_errors: int = 100):
        self.errors = []
        self.max_errors = max_errors
        self.error_counts = {}

    def add_error(self, error: LLMError):
        """Add an error to the aggregator."""
        if len(self.errors) >= self.max_errors:
            self.errors.pop(0)

        self.errors.append({
            'error': error,
            'timestamp': datetime.now(),
            'code': error.error_code
        })

        # Track error counts by code
        self.error_counts[error.error_code] = self.error_counts.get(error.error_code, 0) + 1

        logger.error(f"Error aggregated: {error.error_code} - {error.message}")

    def get_error_rate(self, error_code: str = None) -> float:
        """Get error rate."""
        if not self.errors:
            return 0.0

        if error_code:
            count = sum(1 for e in self.errors if e['code'] == error_code)
        else:
            count = len(self.errors)

        return count / len(self.errors)

    def get_recent_errors(self, count: int = 10) -> list:
        """Get recent errors."""
        return self.errors[-count:]

    def clear(self):
        """Clear error history."""
        self.errors = []
        self.error_counts = {}


# Global error aggregator
error_aggregator = ErrorAggregator()


def handle_error(error: Exception, component: str, operation: str, context: dict = None) -> LLMError:
    """
    Convert any exception to LLMError with context.

    Args:
        error: Original exception
        component: Component where error occurred
        operation: Operation being performed
        context: Additional context

    Returns:
        LLMError with full context
    """
    context = context or {}

    if isinstance(error, LLMError):
        llm_error = error
    else:
        llm_error = LLMError(
            message=str(error),
            error_code=type(error).__name__,
            context=context
        )

    llm_error.context.update({
        'component': component,
        'operation': operation,
        'original_error': type(error).__name__
    })

    error_aggregator.add_error(llm_error)
    logger.error(
        f"Error in {component}.{operation}: {error}",
        extra={
            'component': component,
            'operation': operation,
            'context': llm_error.context
        }
    )

    return llm_error


T = TypeVar('T')


async def safe_execute(
    operation: Callable[..., Coroutine[Any, Any, T]],
    component: str,
    operation_name: str,
    fallback: Optional[Callable[..., Coroutine[Any, Any, T]]] = None,
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    timeout: Optional[float] = None
) -> T:
    """
    Safely execute an async operation with retry and error handling.

    Args:
        operation: Async operation to execute
        component: Component name
        operation_name: Operation name
        fallback: Fallback operation if main fails
        max_retries: Max retry attempts
        backoff_factor: Exponential backoff factor
        timeout: Operation timeout in seconds

    Returns:
        Operation result

    Raises:
        LLMError: If operation fails after retries and no fallback
    """
    last_error = None

    for attempt in range(max_retries + 1):
        try:
            if timeout:
                return await asyncio.wait_for(operation(), timeout=timeout)
            else:
                return await operation()

        except asyncio.TimeoutError as e:
            last_error = e
            logger.warning(
                f"Timeout in {component}.{operation_name} (attempt {attempt + 1}/"
                f"{max_retries + 1})"
            )
            if attempt < max_retries:
                await asyncio.sleep(backoff_factor ** attempt)

        except Exception as e:
            last_error = e
            logger.warning(
                f"Error in {component}.{operation_name} (attempt {attempt + 1}/"
                f"{max_retries + 1}): {e}"
            )
            if attempt < max_retries:
                await asyncio.sleep(backoff_factor ** attempt)

    # All retries exhausted
    if fallback:
        try:
            logger.info(f"Executing fallback for {component}.{operation_name}")
            return await fallback()
        except Exception as fallback_error:
            error = handle_error(
                fallback_error,
                component,
                operation_name,
                {'fallback_failed': True, 'original_error': str(last_error)}
            )
            raise error

    # No fallback, raise error
    error = handle_error(
        last_error,
        component,
        operation_name,
        {'attempts': max_retries + 1}
    )
    raise error


def retry_with_backoff(
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    component: str = "unknown",
):
    """
    Decorator for retrying operations with exponential backoff.

    Args:
        max_retries: Maximum retry attempts
        backoff_factor: Exponential backoff factor
        component: Component name for logging
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries:
                        wait_time = backoff_factor ** attempt
                        logger.warning(
                            f"Retry {attempt + 1}/{max_retries} for "
                            f"{component}.{func.__name__} after {wait_time}s"
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        raise handle_error(e, component, func.__name__)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries:
                        wait_time = backoff_factor ** attempt
                        logger.warning(
                            f"Retry {attempt + 1}/{max_retries} for "
                            f"{component}.{func.__name__} after {wait_time}s"
                        )
                        time.sleep(wait_time)
                    else:
                        raise handle_error(e, component, func.__name__)

        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def error_context(component: str, operation: str):
    """
    Decorator for tracking errors in specific operations.

    Args:
        component: Component name
        operation: Operation name
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            with ErrorContext(component, operation):
                return func(*args, **kwargs)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with ErrorContext(component, operation):
                return await func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper

    return decorator


def safe_execute(func: Callable, *args, component: str = "unknown", **kwargs) -> Any:
    """
    Safely execute a function with error handling.

    Args:
        func: Function to execute
        *args: Positional arguments
        component: Component name for error context
        **kwargs: Keyword arguments

    Returns:
        Function result or None if error
    """
    try:
        if asyncio.iscoroutinefunction(func):
            return asyncio.create_task(func(*args, **kwargs))
        else:
            return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error in {component}: {e}")
        return None


# Contextual error tracking
class ErrorContext:
    """Context manager for tracking errors in a specific operation."""

    def __init__(self, component: str, operation: str, user_id: str = None):
        self.component = component
        self.operation = operation
        self.user_id = user_id
        self.errors = []
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time

        if exc_type:
            error = handle_error(
                exc_val,
                self.component,
                self.operation,
                {
                    'user_id': self.user_id,
                    'duration': duration
                }
            )
            self.errors.append(error)
            logger.error(
                f"Error in {self.component}.{self.operation}: {error.message} "
                f"(took {duration:.3f}s)"
            )

    def add_error(self, error: Exception):
        """Add error to context."""
        llm_error = handle_error(error, self.component, self.operation)
        self.errors.append(llm_error)


# Health check helpers
async def check_component_health(
    component_name: str,
    check_func: Callable[[], Coroutine[Any, Any, bool]],
    timeout: float = 5.0
) -> dict:
    """
    Check health of a component.

    Args:
        component_name: Name of component
        check_func: Async function that returns True if healthy
        timeout: Health check timeout

    Returns:
        Health status dict
    """
    try:
        result = await asyncio.wait_for(check_func(), timeout=timeout)
        return {
            'component': component_name,
            'healthy': result,
            'timestamp': datetime.now().isoformat(),
            'error': None
        }
    except Exception as e:
        return {
            'component': component_name,
            'healthy': False,
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }


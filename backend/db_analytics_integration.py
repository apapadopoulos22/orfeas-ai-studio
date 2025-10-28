"""
[ORFEAS PHASE 2 TASK 4] Database Analytics Integration
Tracks database operations and performance metrics for Task 3 analytics system.

Purpose:
  Record database operations as analytics events
  Track query performance metrics
  Monitor connection pool health
  Integrate with Task 3 real-time analytics dashboard

Events Tracked:
  - Database queries (execution time, rows affected)
  - Connection pool metrics (active, available, overflow)
  - Transaction commits/rollbacks
  - Slow queries (>100ms)
  - Connection errors
  - Bulk operations (inserts, updates)
"""

import logging
import time
from typing import Any, Dict, Optional, Callable
from functools import wraps
from datetime import datetime

from db_layer import get_db_manager
from db_models import AnalyticsEvent

logger = logging.getLogger(__name__)


class DatabaseAnalyticsTracker:
    """Track database operations and send to analytics system."""

    # Reference to analytics event manager (injected at startup)
    event_manager: Optional[Any] = None

    @classmethod
    def set_event_manager(cls, event_manager: Any) -> None:
        """Set the analytics event manager for reporting events."""
        cls.event_manager = event_manager
        logger.info("[DB ANALYTICS] Event manager configured")

    @classmethod
    def track_query(cls, operation: str, table: str, duration_ms: float,
                   rows_affected: int = 0, is_slow: bool = False) -> None:
        """Track database query execution.

        Args:
            operation: Query type (SELECT, INSERT, UPDATE, DELETE)
            table: Table name
            duration_ms: Query execution time
            rows_affected: Number of rows affected
            is_slow: Whether query exceeded slow threshold
        """
        try:
            if cls.event_manager is None:
                return

            event_data = {
                'operation': operation,
                'table': table,
                'duration_ms': duration_ms,
                'rows_affected': rows_affected,
                'is_slow': is_slow,
                'timestamp': datetime.now().isoformat(),
            }

            event_name = f"database.{operation.lower()}.{table.lower()}"

            cls.event_manager.track_event(
                event_type="database_operation",
                event_name=event_name,
                value=duration_ms,
                metadata=event_data,
            )

            if is_slow:
                logger.warning(f"[DB ANALYTICS] Slow query: {operation} {table} ({duration_ms:.2f}ms)")

        except Exception as e:
            logger.error(f"[DB ANALYTICS] Failed to track query: {e}")

    @classmethod
    def track_pool_status(cls) -> None:
        """Track connection pool status."""
        try:
            if cls.event_manager is None:
                return

            manager = get_db_manager()
            pool_status = manager.get_pool_status()
            stats = manager.get_stats()

            event_data = {
                'pool_size': pool_status.get('pool_size', 0),
                'checked_out': pool_status.get('checked_out', 0),
                'overflow': pool_status.get('overflow', 0),
                'active_connections': stats.active_connections,
                'error_count': stats.error_count,
                'health_status': stats.health_status,
                'timestamp': datetime.now().isoformat(),
            }

            cls.event_manager.track_event(
                event_type="database_pool",
                event_name="database.pool.status",
                value=pool_status.get('checked_out', 0),
                metadata=event_data,
            )

        except Exception as e:
            logger.error(f"[DB ANALYTICS] Failed to track pool status: {e}")

    @classmethod
    def track_transaction(cls, operation: str, status: str, duration_ms: float) -> None:
        """Track transaction start/commit/rollback.

        Args:
            operation: COMMIT or ROLLBACK
            status: SUCCESS or FAILED
            duration_ms: Transaction duration
        """
        try:
            if cls.event_manager is None:
                return

            event_data = {
                'operation': operation,
                'status': status,
                'duration_ms': duration_ms,
                'timestamp': datetime.now().isoformat(),
            }

            cls.event_manager.track_event(
                event_type="database_transaction",
                event_name=f"database.transaction.{operation.lower()}",
                value=duration_ms,
                metadata=event_data,
            )

        except Exception as e:
            logger.error(f"[DB ANALYTICS] Failed to track transaction: {e}")

    @classmethod
    def track_error(cls, error_type: str, error_message: str, operation: str) -> None:
        """Track database errors.

        Args:
            error_type: Type of error (OperationalError, DatabaseError, etc.)
            error_message: Error message
            operation: Operation that failed
        """
        try:
            if cls.event_manager is None:
                return

            event_data = {
                'error_type': error_type,
                'error_message': error_message,
                'operation': operation,
                'timestamp': datetime.now().isoformat(),
            }

            cls.event_manager.track_event(
                event_type="database_error",
                event_name=f"database.error.{error_type.lower()}",
                metadata=event_data,
            )

            logger.error(f"[DB ANALYTICS] Database error tracked: {error_type} in {operation}")

        except Exception as e:
            logger.error(f"[DB ANALYTICS] Failed to track error: {e}")


def track_db_operation(operation: str, table: str, slow_threshold_ms: float = 100.0):
    """Decorator for tracking database operations.

    Usage:
        @track_db_operation("SELECT", "jobs", slow_threshold_ms=50)
        def get_job(job_id):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            rows_affected = 0

            try:
                result = func(*args, **kwargs)

                # Try to determine rows affected
                if isinstance(result, list):
                    rows_affected = len(result)
                elif result is not None:
                    rows_affected = 1

                return result

            finally:
                duration_ms = (time.time() - start_time) * 1000
                is_slow = duration_ms > slow_threshold_ms

                DatabaseAnalyticsTracker.track_query(
                    operation=operation,
                    table=table,
                    duration_ms=duration_ms,
                    rows_affected=rows_affected,
                    is_slow=is_slow,
                )

        return wrapper
    return decorator


def track_db_transaction(operation: str = "COMMIT"):
    """Decorator for tracking database transactions.

    Usage:
        @track_db_transaction("COMMIT")
        def save_job(job):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()

            try:
                result = func(*args, **kwargs)

                duration_ms = (time.time() - start_time) * 1000
                DatabaseAnalyticsTracker.track_transaction(
                    operation=operation,
                    status="SUCCESS",
                    duration_ms=duration_ms,
                )

                return result

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                DatabaseAnalyticsTracker.track_transaction(
                    operation="ROLLBACK",
                    status="FAILED",
                    duration_ms=duration_ms,
                )

                DatabaseAnalyticsTracker.track_error(
                    error_type=type(e).__name__,
                    error_message=str(e),
                    operation=func.__name__,
                )

                raise

        return wrapper
    return decorator


# Analytics dashboard metrics
def get_db_metrics() -> Dict[str, Any]:
    """Get comprehensive database metrics for analytics dashboard.

    Returns:
        Dictionary with pool status, query stats, and health info.
    """
    try:
        manager = get_db_manager()
        pool_status = manager.get_pool_status()
        stats = manager.get_stats()
        db_stats = manager.get_stats()

        return {
            'pool': {
                'size': pool_status.get('pool_size', 0),
                'checked_out': pool_status.get('checked_out', 0),
                'overflow': pool_status.get('overflow', 0),
                'status': pool_status.get('status', 'unknown'),
            },
            'performance': {
                'total_queries': db_stats.total_connections,
                'active_connections': db_stats.active_connections,
                'error_count': db_stats.error_count,
                'health_status': db_stats.health_status,
            },
            'health': {
                'last_check': db_stats.last_check.isoformat() if db_stats.last_check else None,
                'status': 'healthy' if manager.health_check() else 'unhealthy',
                'last_error': db_stats.last_error,
            },
        }

    except Exception as e:
        logger.error(f"[DB ANALYTICS] Failed to get metrics: {e}")
        return {
            'error': str(e),
            'status': 'failed',
        }

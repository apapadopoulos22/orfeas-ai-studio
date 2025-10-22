"""
Distributed Tracing System - Phase 4 Tier 3
End-to-end request tracing for debugging and performance analysis
Minimal overhead with detailed request flow visualization
"""

import logging
import time
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
import json

logger = logging.getLogger(__name__)


class SpanStatus(Enum):
    """Span execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class Span:
    """Single operation span in a trace"""
    span_id: str
    trace_id: str
    parent_span_id: Optional[str]
    operation_name: str
    service: str
    status: SpanStatus = SpanStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    duration_ms: float = 0.0
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict] = field(default_factory=list)
    error: Optional[str] = None

    def duration(self) -> float:
        """Calculate span duration"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0.0

    def to_dict(self) -> Dict:
        """Convert span to dictionary"""
        return {
            'span_id': self.span_id,
            'trace_id': self.trace_id,
            'parent_span_id': self.parent_span_id,
            'operation_name': self.operation_name,
            'service': self.service,
            'status': self.status.value,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration_ms': self.duration_ms,
            'tags': self.tags,
            'logs': self.logs,
            'error': self.error
        }


@dataclass
class Trace:
    """Complete trace containing multiple spans"""
    trace_id: str
    root_span_id: str
    start_time: float
    end_time: Optional[float] = None
    status: SpanStatus = SpanStatus.RUNNING
    spans: Dict[str, Span] = field(default_factory=dict)
    services: set = field(default_factory=set)
    error_count: int = 0

    def duration(self) -> float:
        """Calculate trace duration"""
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0.0

    def to_dict(self) -> Dict:
        """Convert trace to dictionary"""
        return {
            'trace_id': self.trace_id,
            'root_span_id': self.root_span_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration_ms': self.duration(),
            'status': self.status.value,
            'services': list(self.services),
            'span_count': len(self.spans),
            'error_count': self.error_count,
            'spans': [span.to_dict() for span in self.spans.values()]
        }


class DistributedTracingSystem:
    """
    Distributed tracing for end-to-end request tracking
    Minimal overhead with detailed request flow visualization
    """

    def __init__(self, service_name: str = "orfeas", max_traces: int = 1000):
        """
        Initialize tracing system

        Args:
            service_name: Name of this service
            max_traces: Maximum traces to keep in memory
        """
        self.service_name = service_name
        self.max_traces = max_traces

        # Active traces (in-flight)
        self.active_traces: Dict[str, Trace] = {}

        # Completed traces (history)
        self.completed_traces: List[Trace] = []

        # Current trace context (thread-local)
        self._trace_context = threading.local()

        self._lock = threading.Lock()
        self.stats = {
            'traces_created': 0,
            'traces_completed': 0,
            'total_spans': 0,
            'total_errors': 0,
            'slow_requests': 0
        }

    def start_trace(self, root_operation: str, tags: Dict = None) -> str:
        """
        Start a new trace

        Args:
            root_operation: Name of root operation
            tags: Optional tags for the root span

        Returns:
            Trace ID
        """
        trace_id = str(uuid.uuid4())
        span_id = str(uuid.uuid4())
        current_time = time.time()

        root_span = Span(
            span_id=span_id,
            trace_id=trace_id,
            parent_span_id=None,
            operation_name=root_operation,
            service=self.service_name,
            status=SpanStatus.RUNNING,
            start_time=current_time,
            tags=tags or {}
        )

        trace = Trace(
            trace_id=trace_id,
            root_span_id=span_id,
            start_time=current_time,
            spans={span_id: root_span},
            services={self.service_name}
        )

        with self._lock:
            self.active_traces[trace_id] = trace
            self.stats['traces_created'] += 1

        # Set context
        self._trace_context.trace_id = trace_id
        self._trace_context.current_span_id = span_id

        logger.debug(f"[TRACE] Started trace {trace_id}: {root_operation}")

        return trace_id

    def start_span(self, operation_name: str, service: Optional[str] = None,
                   tags: Dict = None) -> str:
        """
        Start a new span within current trace

        Args:
            operation_name: Name of operation
            service: Service name (defaults to current service)
            tags: Optional tags

        Returns:
            Span ID
        """
        trace_id = getattr(self._trace_context, 'trace_id', None)
        parent_span_id = getattr(self._trace_context, 'current_span_id', None)

        if not trace_id:
            logger.warning("[TRACE] No active trace context")
            return ""

        span_id = str(uuid.uuid4())
        current_time = time.time()
        service = service or self.service_name

        span = Span(
            span_id=span_id,
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            service=service,
            status=SpanStatus.RUNNING,
            start_time=current_time,
            tags=tags or {}
        )

        with self._lock:
            if trace_id in self.active_traces:
                self.active_traces[trace_id].spans[span_id] = span
                self.active_traces[trace_id].services.add(service)
                self.stats['total_spans'] += 1

        # Update context
        old_span_id = getattr(self._trace_context, 'current_span_id', None)
        self._trace_context.current_span_id = span_id
        self._trace_context.previous_span_id = old_span_id

        logger.debug(f"[TRACE] Started span {span_id}: {operation_name}")

        return span_id

    def add_log(self, message: str, fields: Dict = None) -> None:
        """Add log entry to current span"""
        trace_id = getattr(self._trace_context, 'trace_id', None)
        span_id = getattr(self._trace_context, 'current_span_id', None)

        if not trace_id or not span_id:
            return

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'fields': fields or {}
        }

        with self._lock:
            if trace_id in self.active_traces:
                if span_id in self.active_traces[trace_id].spans:
                    self.active_traces[trace_id].spans[span_id].logs.append(log_entry)

    def add_tag(self, key: str, value: Any) -> None:
        """Add tag to current span"""
        trace_id = getattr(self._trace_context, 'trace_id', None)
        span_id = getattr(self._trace_context, 'current_span_id', None)

        if not trace_id or not span_id:
            return

        with self._lock:
            if trace_id in self.active_traces:
                if span_id in self.active_traces[trace_id].spans:
                    self.active_traces[trace_id].spans[span_id].tags[key] = value

    def end_span(self, status: SpanStatus = SpanStatus.COMPLETED, error: Optional[str] = None) -> None:
        """
        End current span

        Args:
            status: Final status
            error: Optional error message
        """
        trace_id = getattr(self._trace_context, 'trace_id', None)
        span_id = getattr(self._trace_context, 'current_span_id', None)

        if not trace_id or not span_id:
            return

        current_time = time.time()

        with self._lock:
            if trace_id in self.active_traces:
                trace = self.active_traces[trace_id]
                if span_id in trace.spans:
                    span = trace.spans[span_id]
                    span.end_time = current_time
                    span.duration_ms = span.duration()
                    span.status = status
                    span.error = error

                    if status == SpanStatus.ERROR:
                        trace.error_count += 1
                        self.stats['total_errors'] += 1

        # Restore context
        previous_span_id = getattr(self._trace_context, 'previous_span_id', None)
        if previous_span_id:
            self._trace_context.current_span_id = previous_span_id

        logger.debug(f"[TRACE] Ended span {span_id} ({status.value})")

    def end_trace(self) -> Optional[Trace]:
        """
        End current trace

        Returns:
            Completed trace
        """
        trace_id = getattr(self._trace_context, 'trace_id', None)

        if not trace_id:
            return None

        current_time = time.time()

        with self._lock:
            if trace_id in self.active_traces:
                trace = self.active_traces.pop(trace_id)
                trace.end_time = current_time
                trace.status = SpanStatus.COMPLETED

                # Check if slow
                if trace.duration() > 5000:  # > 5 seconds
                    self.stats['slow_requests'] += 1

                # Add to history
                self.completed_traces.append(trace)
                if len(self.completed_traces) > self.max_traces:
                    self.completed_traces = self.completed_traces[-self.max_traces:]

                self.stats['traces_completed'] += 1

                logger.debug(
                    f"[TRACE] Completed trace {trace_id} "
                    f"({trace.duration():.2f}ms, {len(trace.spans)} spans)"
                )

                return trace

        return None

    def get_trace(self, trace_id: str) -> Optional[Trace]:
        """Get trace by ID"""
        with self._lock:
            # Check active traces
            if trace_id in self.active_traces:
                return self.active_traces[trace_id]

            # Check completed traces
            for trace in self.completed_traces:
                if trace.trace_id == trace_id:
                    return trace

        return None

    def get_active_traces(self) -> List[Dict]:
        """Get all active traces"""
        with self._lock:
            return [t.to_dict() for t in self.active_traces.values()]

    def get_completed_traces(self, limit: int = 100) -> List[Dict]:
        """Get recent completed traces"""
        with self._lock:
            return [t.to_dict() for t in self.completed_traces[-limit:]]

    def get_slow_traces(self, min_duration_ms: float = 1000, limit: int = 50) -> List[Dict]:
        """Get slow traces (above threshold)"""
        with self._lock:
            slow = [
                t for t in self.completed_traces
                if t.duration() >= min_duration_ms
            ]
            return [t.to_dict() for t in slow[-limit:]]

    def get_trace_statistics(self) -> Dict:
        """Get tracing statistics"""
        with self._lock:
            completed = self.completed_traces

            if not completed:
                return {
                    'traces_created': self.stats['traces_created'],
                    'traces_completed': self.stats['traces_completed'],
                    'active_traces': len(self.active_traces),
                    'no_data': 'Insufficient completed traces'
                }

            durations = [t.duration() for t in completed]

            return {
                'traces_created': self.stats['traces_created'],
                'traces_completed': self.stats['traces_completed'],
                'active_traces': len(self.active_traces),
                'total_spans': self.stats['total_spans'],
                'total_errors': self.stats['total_errors'],
                'slow_requests': self.stats['slow_requests'],
                'avg_duration_ms': sum(durations) / len(durations),
                'max_duration_ms': max(durations),
                'min_duration_ms': min(durations),
                'avg_spans_per_trace': self.stats['total_spans'] / max(1, self.stats['traces_completed']),
                'error_rate_percent': (
                    self.stats['total_errors'] / max(1, self.stats['total_spans']) * 100
                ) if self.stats['total_spans'] > 0 else 0
            }

    def export_trace_json(self, trace_id: str) -> str:
        """Export trace as JSON"""
        trace = self.get_trace(trace_id)
        if trace:
            return json.dumps(trace.to_dict(), indent=2, default=str)
        return "{}"

    def clear_history(self) -> Dict:
        """Clear completed trace history"""
        with self._lock:
            count = len(self.completed_traces)
            self.completed_traces.clear()

        logger.info(f"[TRACE] Cleared {count} completed traces")
        return {'traces_cleared': count}


# Singleton instance
_tracing_system: Optional[DistributedTracingSystem] = None


def get_tracing_system(service_name: str = "orfeas") -> DistributedTracingSystem:
    """Get or create tracing system singleton"""
    global _tracing_system
    if _tracing_system is None:
        _tracing_system = DistributedTracingSystem(service_name=service_name)
        logger.info(f"[TRACE] Distributed Tracing System initialized for {service_name}")
    return _tracing_system


def reset_tracing_system() -> None:
    """Reset tracing system (for testing)"""
    global _tracing_system
    _tracing_system = None


# Context manager for automatic span management
class TraceSpan:
    """Context manager for automatic span lifecycle management"""

    def __init__(self, operation_name: str, service: Optional[str] = None, tags: Dict = None):
        self.operation_name = operation_name
        self.service = service
        self.tags = tags
        self.span_id: Optional[str] = None
        self.tracer = get_tracing_system()

    def __enter__(self) -> 'TraceSpan':
        self.span_id = self.tracer.start_span(self.operation_name, self.service, self.tags)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.tracer.end_span(SpanStatus.ERROR, str(exc_val))
        else:
            self.tracer.end_span(SpanStatus.COMPLETED)

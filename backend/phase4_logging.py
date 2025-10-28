#!/usr/bin/env python3
"""
Phase 4.7: Logging Aggregation
================================

Centralized logging system with file, console, and structured output.
Supports: Log rotation, filtering, formatting, structured JSON logging.

Status: Production-Ready
Version: 1.0.0
Author: BOB AI v10.0
"""

import logging
import json
import os
import sys
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path


class StructuredFormatter(logging.Formatter):
    """Structured JSON logging formatter."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_obj = {
            'timestamp': datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread': record.thread,
            'thread_name': record.threadName
        }

        # Add exception info if present
        if record.exc_info:
            log_obj['exception'] = self.formatException(record.exc_info)

        # Add custom fields if present
        if hasattr(record, 'custom_fields'):
            log_obj.update(record.custom_fields)

        return json.dumps(log_obj)


class SimpleFormatter(logging.Formatter):
    """Simple text logging formatter."""

    FORMAT = '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as text."""
        formatter = logging.Formatter(self.FORMAT, self.DATE_FORMAT)
        return formatter.format(record)


class LoggingManager:
    """
    Centralized logging management.

    Features:
    - Multiple handlers (console, file, rotating file)
    - Structured JSON logging support
    - Log level configuration
    - Log rotation by size or time
    - Performance metrics logging
    """

    _instance = None
    _configured = False

    def __init__(self, name: str = 'bob_ai'):
        """
        Initialize logging manager.

        Args:
            name: Logger name
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.handlers = {}

    @classmethod
    def get_instance(cls, name: str = 'bob_ai') -> 'LoggingManager':
        """Get or create singleton."""
        if cls._instance is None:
            cls._instance = LoggingManager(name)
        return cls._instance

    def setup_console_handler(self, level: str = 'INFO',
                            use_json: bool = False) -> None:
        """
        Set up console (stdout) handler.

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            use_json: Use JSON formatter if True
        """
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, level))

        formatter = (StructuredFormatter() if use_json
                    else SimpleFormatter())
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)
        self.handlers['console'] = handler

        logging.info(f"[LOGGING] Console handler configured (level={level}, json={use_json})")

    def setup_file_handler(self, log_file: str, level: str = 'INFO',
                          use_json: bool = False, max_bytes: int = 10485760,
                          backup_count: int = 5) -> None:
        """
        Set up rotating file handler.

        Args:
            log_file: Path to log file
            level: Log level
            use_json: Use JSON formatter if True
            max_bytes: Max file size before rotation (default: 10MB)
            backup_count: Number of backup files to keep (default: 5)
        """
        # Create log directory if needed
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        handler.setLevel(getattr(logging, level))

        formatter = (StructuredFormatter() if use_json
                    else SimpleFormatter())
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)
        self.handlers['file'] = handler

        logging.info(f"[LOGGING] File handler configured (file={log_file}, max_bytes={max_bytes})")

    def set_level(self, level: str = 'INFO') -> None:
        """Set logging level."""
        self.logger.setLevel(getattr(logging, level))
        for handler in self.handlers.values():
            handler.setLevel(getattr(logging, level))

    def log_with_context(self, level: str, message: str,
                        context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log with additional context fields.

        Args:
            level: Log level
            message: Log message
            context: Additional fields to include in JSON log
        """
        if context is None:
            context = {}

        # Create logger record with custom fields
        record = self.logger.makeRecord(
            self.logger.name,
            getattr(logging, level),
            fn='',
            lno=0,
            msg=message,
            args=(),
            exc_info=None
        )
        record.custom_fields = context

        for handler in self.handlers.values():
            handler.emit(record)

    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        if kwargs:
            self.log_with_context('INFO', message, kwargs)
        else:
            self.logger.info(message)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        if kwargs:
            self.log_with_context('WARNING', message, kwargs)
        else:
            self.logger.warning(message)

    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        if kwargs:
            self.log_with_context('ERROR', message, kwargs)
        else:
            self.logger.error(message)

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        if kwargs:
            self.log_with_context('DEBUG', message, kwargs)
        else:
            self.logger.debug(message)

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        if kwargs:
            self.log_with_context('CRITICAL', message, kwargs)
        else:
            self.logger.critical(message)

    # ========================================================================
    # PERFORMANCE LOGGING
    # ========================================================================

    def log_request(self, method: str, path: str, status_code: int,
                   duration_ms: float, user_id: Optional[str] = None) -> None:
        """
        Log HTTP request with performance metrics.

        Args:
            method: HTTP method
            path: Request path
            status_code: Response status code
            duration_ms: Request duration in milliseconds
            user_id: User ID (optional)
        """
        context = {
            'type': 'http_request',
            'method': method,
            'path': path,
            'status_code': status_code,
            'duration_ms': round(duration_ms, 2)
        }
        if user_id:
            context['user_id'] = user_id

        level = 'WARNING' if status_code >= 400 else 'INFO'
        self.log_with_context(level, f"{method} {path} {status_code} ({duration_ms:.2f}ms)", context)

    def log_cache_operation(self, operation: str, key: str,
                           hit: bool, duration_ms: float) -> None:
        """
        Log cache operation.

        Args:
            operation: Operation type (get, set, delete)
            key: Cache key
            hit: True if cache hit
            duration_ms: Operation duration
        """
        context = {
            'type': 'cache_operation',
            'operation': operation,
            'key': key[:50] + '...' if len(key) > 50 else key,  # Truncate long keys
            'hit': hit,
            'duration_ms': round(duration_ms, 2)
        }
        self.log_with_context('DEBUG', f"Cache {operation}: {key} ({'hit' if hit else 'miss'}) {duration_ms:.2f}ms", context)

    def log_auth_attempt(self, key_id: str, success: bool,
                        reason: Optional[str] = None) -> None:
        """
        Log authentication attempt.

        Args:
            key_id: API key ID
            success: True if authentication succeeded
            reason: Failure reason if applicable
        """
        context = {
            'type': 'auth_attempt',
            'key_id': key_id[:10] + '...' if len(key_id) > 10 else key_id,
            'success': success
        }
        if reason:
            context['reason'] = reason

        level = 'INFO' if success else 'WARNING'
        status = 'successful' if success else 'failed'
        msg = f"Authentication {status} for {key_id}"
        self.log_with_context(level, msg, context)

    def log_security_event(self, event_type: str, details: str,
                          ip_address: Optional[str] = None) -> None:
        """
        Log security event.

        Args:
            event_type: Type of event (sql_injection, xss, etc.)
            details: Event details
            ip_address: Source IP address (optional)
        """
        context = {
            'type': 'security_event',
            'event_type': event_type,
            'details': details
        }
        if ip_address:
            context['ip_address'] = ip_address

        self.log_with_context('CRITICAL', f"SECURITY EVENT: {event_type} - {details}", context)

    # ========================================================================
    # LOG RETRIEVAL
    # ========================================================================

    def get_log_file_path(self) -> Optional[str]:
        """Get path to main log file (if using file handler)."""
        if 'file' in self.handlers:
            return self.handlers['file'].baseFilename
        return None

    def read_recent_logs(self, num_lines: int = 100) -> str:
        """
        Read recent log lines from file.

        Args:
            num_lines: Number of lines to read

        Returns:
            Recent log lines as string
        """
        log_file = self.get_log_file_path()
        if not log_file or not os.path.exists(log_file):
            return "No log file found"

        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                return ''.join(lines[-num_lines:])
        except Exception as e:
            return f"Error reading logs: {e}"

    def get_log_stats(self) -> Dict[str, Any]:
        """Get statistics about log file."""
        log_file = self.get_log_file_path()
        if not log_file or not os.path.exists(log_file):
            return {'status': 'no_log_file'}

        try:
            stat = os.stat(log_file)
            return {
                'status': 'ok',
                'file_path': log_file,
                'size_bytes': stat.st_size,
                'size_mb': round(stat.st_size / 1024 / 1024, 2),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}


def get_logging_manager(name: str = 'bob_ai') -> LoggingManager:
    """Get or create logging manager singleton."""
    return LoggingManager.get_instance(name)


def configure_logging(console_level: str = 'INFO',
                     file_level: str = 'DEBUG',
                     log_file: Optional[str] = None,
                     use_json: bool = False) -> LoggingManager:
    """
    Quick configuration helper.

    Args:
        console_level: Console log level
        file_level: File log level
        log_file: Path to log file (optional)
        use_json: Use JSON formatting

    Returns:
        Configured LoggingManager instance

    Example:
        logging_manager = configure_logging(
            console_level='INFO',
            file_level='DEBUG',
            log_file='logs/app.log'
        )
    """
    manager = get_logging_manager()

    # Configure console handler
    manager.setup_console_handler(console_level, use_json)

    # Configure file handler if specified
    if log_file:
        manager.setup_file_handler(log_file, file_level, use_json)

    return manager

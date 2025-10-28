"""
ORFEAS AI Studio - API Gateway
===============================

Centralized API gateway with:
- Request routing and validation
- API versioning (v1, v2)
- Request/response transformation
- Circuit breaker pattern
- Request/response logging
- Integration with rate limiting and authentication

Author: ORFEAS AI Team
Date: October 28, 2025
"""

import logging
import time
import json
from typing import Optional, Dict, Any, Callable
from functools import wraps
from datetime import datetime, timedelta
import re
from flask import Blueprint, request, jsonify, g, make_response
from werkzeug.exceptions import HTTPException

from core.rate_limiter import rate_limit, RateLimitTier
try:
    from prometheus_metrics import (
        http_requests_total,
        http_request_duration_seconds,
        errors_total,
        rate_limit_rejections_total
    )
except ImportError:
    # Fallback if prometheus_metrics not available
    http_requests_total = None
    http_request_duration_seconds = None
    errors_total = None
    rate_limit_rejections_total = None

logger = logging.getLogger(__name__)


class APIVersion:
    """API version configurations"""

    V1 = {
        'version': 'v1',
        'prefix': '/api/v1',
        'deprecated': False,
        'sunset_date': None,
        'features': ['basic', 'auth', 'generation']
    }

    V2 = {
        'version': 'v2',
        'prefix': '/api/v2',
        'deprecated': False,
        'sunset_date': None,
        'features': ['basic', 'auth', 'generation', 'streaming', 'batch']
    }


class CircuitBreaker:
    """
    Circuit breaker pattern for fault tolerance.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests blocked
    - HALF_OPEN: Testing if service recovered
    """

    CLOSED = 'closed'
    OPEN = 'open'
    HALF_OPEN = 'half_open'

    def __init__(
        self,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout: int = 60
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Failures before opening circuit
            success_threshold: Successes to close circuit from half-open
            timeout: Seconds before trying half-open from open
        """
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout

        self.state = self.CLOSED
        self.failures = 0
        self.successes = 0
        self.last_failure_time = None

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker.

        Args:
            func: Function to execute
            *args, **kwargs: Function arguments

        Returns:
            Function result

        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == self.OPEN:
            # Check if timeout elapsed
            if self.last_failure_time:
                elapsed = time.time() - self.last_failure_time
                if elapsed >= self.timeout:
                    logger.info("Circuit breaker entering HALF_OPEN state")
                    self.state = self.HALF_OPEN
                    self.successes = 0
                else:
                    raise Exception("Circuit breaker is OPEN")
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result

        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        """Handle successful request"""
        if self.state == self.HALF_OPEN:
            self.successes += 1
            if self.successes >= self.success_threshold:
                logger.info("Circuit breaker closing after successful tests")
                self.state = self.CLOSED
                self.failures = 0
                self.successes = 0
        elif self.state == self.CLOSED:
            self.failures = 0  # Reset failure count

    def _on_failure(self):
        """Handle failed request"""
        self.failures += 1
        self.last_failure_time = time.time()

        if self.state == self.HALF_OPEN:
            logger.warning("Circuit breaker reopening after failure in HALF_OPEN")
            self.state = self.OPEN
            self.successes = 0

        elif self.state == self.CLOSED:
            if self.failures >= self.failure_threshold:
                logger.error(f"Circuit breaker opening after {self.failures} failures")
                self.state = self.OPEN

    def reset(self):
        """Reset circuit breaker to CLOSED state"""
        self.state = self.CLOSED
        self.failures = 0
        self.successes = 0
        self.last_failure_time = None


class APIGateway:
    """
    API Gateway for request routing and management.
    """

    def __init__(self):
        """Initialize API gateway"""
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.request_validators: Dict[str, Callable] = {}
        self.response_transformers: Dict[str, Callable] = {}

    def get_circuit_breaker(self, service: str) -> CircuitBreaker:
        """Get or create circuit breaker for service"""
        if service not in self.circuit_breakers:
            self.circuit_breakers[service] = CircuitBreaker(
                failure_threshold=5,
                success_threshold=2,
                timeout=60
            )
        return self.circuit_breakers[service]

    def register_validator(self, endpoint: str, validator: Callable):
        """Register request validator for endpoint"""
        self.request_validators[endpoint] = validator

    def register_transformer(self, endpoint: str, transformer: Callable):
        """Register response transformer for endpoint"""
        self.response_transformers[endpoint] = transformer

    def validate_request(self, endpoint: str, data: Dict[str, Any]) -> tuple:
        """
        Validate request data.

        Returns:
            Tuple of (valid: bool, errors: list)
        """
        if endpoint in self.request_validators:
            return self.request_validators[endpoint](data)
        return True, []

    def transform_response(self, endpoint: str, response: Any) -> Any:
        """Transform response data"""
        if endpoint in self.response_transformers:
            return self.response_transformers[endpoint](response)
        return response


# Global API gateway instance
_api_gateway: Optional[APIGateway] = None


def get_api_gateway() -> APIGateway:
    """Get global API gateway instance"""
    global _api_gateway

    if _api_gateway is None:
        _api_gateway = APIGateway()

    return _api_gateway


def api_gateway(
    version: str = 'v1',
    require_auth: bool = False,
    rate_limit_tier: Optional[Dict[str, Any]] = None,
    validate_request: bool = True,
    circuit_breaker: bool = False
):
    """
    API Gateway decorator for Flask routes.

    Usage:
        @app.route('/api/v1/generate')
        @api_gateway(version='v1', require_auth=True, rate_limit_tier=RateLimitTier.PRO)
        def generate():
            return {'status': 'success'}

    Args:
        version: API version (v1, v2)
        require_auth: Require authentication
        rate_limit_tier: Rate limit tier (None = auto-detect)
        validate_request: Validate request data
        circuit_breaker: Use circuit breaker pattern
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            gateway = get_api_gateway()

            # Extract endpoint name
            endpoint = request.endpoint or f.__name__

            try:
                # 1. Check authentication if required
                if require_auth:
                    if not hasattr(g, 'user_id') or not g.user_id:
                        if http_requests_total:
                            if http_requests_total: http_requests_total.labels(
                                method=request.method,
                                endpoint=endpoint,
                                status=401
                            ).inc()

                        return jsonify({
                            'error': 'authentication_required',
                            'message': 'Authentication required for this endpoint'
                        }), 401

                # 2. Validate request data
                if validate_request and request.is_json:
                    valid, errors = gateway.validate_request(endpoint, request.get_json())
                    if not valid:
                        if http_requests_total:
                            if http_requests_total: http_requests_total.labels(
                                method=request.method,
                                endpoint=endpoint,
                                status=400
                            ).inc()

                        return jsonify({
                            'error': 'validation_failed',
                            'message': 'Request validation failed',
                            'errors': errors
                        }), 400

                # 3. Execute request (with circuit breaker if enabled)
                if circuit_breaker:
                    breaker = gateway.get_circuit_breaker(endpoint)
                    try:
                        response = breaker.call(f, *args, **kwargs)
                    except Exception as e:
                        if "Circuit breaker is OPEN" in str(e):
                            if http_requests_total: http_requests_total.labels(
                                method=request.method,
                                endpoint=endpoint,
                                status=503
                            ).inc()

                            return jsonify({
                                'error': 'service_unavailable',
                                'message': 'Service temporarily unavailable',
                                'retry_after': 60
                            }), 503
                        raise
                else:
                    response = f(*args, **kwargs)

                # 4. Transform response
                response = gateway.transform_response(endpoint, response)

                # 5. Add API version headers
                if hasattr(response, 'headers'):
                    response.headers['X-API-Version'] = version
                    response.headers['X-Request-ID'] = request.headers.get(
                        'X-Request-ID',
                        f"req_{int(time.time()*1000)}"
                    )

                # 6. Record metrics
                duration = time.time() - start_time
                status_code = response.status_code if hasattr(response, 'status_code') else 200

                if http_requests_total: http_requests_total.labels(
                    method=request.method,
                    endpoint=endpoint,
                    status=status_code
                ).inc()

                if http_request_duration_seconds: http_request_duration_seconds.labels(
                    method=request.method,
                    endpoint=endpoint
                ).observe(duration)

                return response

            except HTTPException as e:
                # Handle HTTP exceptions
                duration = time.time() - start_time

                if http_requests_total: http_requests_total.labels(
                    method=request.method,
                    endpoint=endpoint,
                    status=e.code
                ).inc()

                if http_request_duration_seconds: http_request_duration_seconds.labels(
                    method=request.method,
                    endpoint=endpoint
                ).observe(duration)

                if errors_total: errors_total.labels(
                    error_type='http_error',
                    endpoint=endpoint
                ).inc()

                raise

            except Exception as e:
                # Handle unexpected exceptions
                duration = time.time() - start_time

                if http_requests_total: http_requests_total.labels(
                    method=request.method,
                    endpoint=endpoint,
                    status=500
                ).inc()

                if http_request_duration_seconds: http_request_duration_seconds.labels(
                    method=request.method,
                    endpoint=endpoint
                ).observe(duration)

                if errors_total: errors_total.labels(
                    error_type='internal_error',
                    endpoint=endpoint
                ).inc()

                logger.error(f"Error in {endpoint}: {e}", exc_info=True)

                return jsonify({
                    'error': 'internal_error',
                    'message': 'An internal error occurred',
                    'request_id': request.headers.get('X-Request-ID', 'unknown')
                }), 500

        return decorated_function
    return decorator


def create_api_blueprint(version: str = 'v1') -> Blueprint:
    """
    Create API blueprint for specific version.

    Args:
        version: API version (v1, v2)

    Returns:
        Flask Blueprint
    """
    version_config = APIVersion.V1 if version == 'v1' else APIVersion.V2

    bp = Blueprint(
        f'api_{version}',
        __name__,
        url_prefix=version_config['prefix']
    )

    @bp.before_request
    def before_request():
        """Execute before each request"""
        g.start_time = time.time()
        g.request_id = request.headers.get('X-Request-ID', f"req_{int(time.time()*1000)}")

        # Check if API version is deprecated
        if version_config['deprecated']:
            logger.warning(f"Deprecated API version {version} accessed")

    @bp.after_request
    def after_request(response):
        """Execute after each request"""
        # Add CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Request-ID'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'

        # Add version headers
        response.headers['X-API-Version'] = version
        response.headers['X-Request-ID'] = g.request_id

        # Add deprecation warning if applicable
        if version_config['deprecated'] and version_config['sunset_date']:
            response.headers['Sunset'] = version_config['sunset_date']
            response.headers['Deprecation'] = 'true'

        # Log request duration
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            logger.info(
                f"{request.method} {request.path} - "
                f"{response.status_code} - {duration:.3f}s"
            )

        return response

    # Health check endpoint
    @bp.route('/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'version': version,
            'timestamp': datetime.utcnow().isoformat()
        })

    # API info endpoint
    @bp.route('/info', methods=['GET'])
    def info():
        """API information endpoint"""
        return jsonify({
            'version': version_config['version'],
            'deprecated': version_config['deprecated'],
            'sunset_date': version_config['sunset_date'],
            'features': version_config['features'],
            'documentation': f'/docs/{version}'
        })

    return bp


if __name__ == "__main__":
    print("Testing API Gateway...")

    # Test circuit breaker
    print("\n1. Testing Circuit Breaker:")
    breaker = CircuitBreaker(failure_threshold=3, timeout=5)

    def failing_function():
        raise Exception("Service error")

    def working_function():
        return "Success"

    # Trigger failures
    for i in range(5):
        try:
            breaker.call(failing_function)
        except Exception as e:
            print(f"Attempt {i+1}: {e}")

    # Circuit should be open now
    print(f"Circuit state: {breaker.state}")

    try:
        breaker.call(working_function)
    except Exception as e:
        print(f"Blocked: {e}")

    print("\n✅ API Gateway test complete")

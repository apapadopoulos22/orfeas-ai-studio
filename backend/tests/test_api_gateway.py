"""
ORFEAS AI Studio - API Gateway & Rate Limiting Tests
=====================================================

Comprehensive test suite for:
- Rate limiting with sliding window algorithm
- API gateway routing and validation
- Circuit breaker pattern
- Multiple rate limit tiers
- Concurrent request limiting

Author: ORFEAS AI Team
Date: October 28, 2025
"""

import pytest
import time
import redis
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, g, request

from core.rate_limiter import (
    SlidingWindowRateLimiter,
    RateLimitManager,
    RateLimitTier,
    rate_limit,
    check_concurrent_requests,
    release_concurrent_request
)
from core.api_gateway import (
    APIGateway,
    CircuitBreaker,
    api_gateway,
    create_api_blueprint
)


@pytest.fixture
def redis_mock():
    """Mock Redis client"""
    mock = MagicMock(spec=redis.Redis)
    mock.zremrangebyscore.return_value = None
    mock.zcard.return_value = 0
    mock.zadd.return_value = None
    mock.expire.return_value = None
    mock.zrange.return_value = [(b'test', 0.0)]
    return mock


@pytest.fixture
def rate_limiter(redis_mock):
    """Create rate limiter with mock Redis"""
    return SlidingWindowRateLimiter(redis_mock)


@pytest.fixture
def rate_limit_manager(redis_mock):
    """Create rate limit manager with mock Redis"""
    return RateLimitManager(redis_mock)


@pytest.fixture
def flask_app():
    """Create Flask app for testing"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app


class TestSlidingWindowRateLimiter:
    """Test sliding window rate limiter"""

    def test_check_rate_limit_allowed(self, rate_limiter, redis_mock):
        """Test rate limit allows request within limit"""
        # Mock Redis to return 5 current requests
        redis_mock.zcard.return_value = 5

        allowed, info = rate_limiter.check_rate_limit(
            identifier="test:user:123",
            limit=10,
            window_seconds=60
        )

        assert allowed is True
        assert info['limit'] == 10
        assert info['remaining'] >= 0
        assert 'reset' in info

    def test_check_rate_limit_blocked(self, rate_limiter, redis_mock):
        """Test rate limit blocks request over limit"""
        # Mock Redis to return 10 current requests (at limit)
        redis_mock.zcard.return_value = 10

        allowed, info = rate_limiter.check_rate_limit(
            identifier="test:user:123",
            limit=10,
            window_seconds=60
        )

        assert allowed is False
        assert info['remaining'] == 0

    def test_burst_allowance(self, rate_limiter, redis_mock):
        """Test burst allowance allows extra requests"""
        # Mock Redis to return 10 requests (at base limit)
        redis_mock.zcard.return_value = 10

        # Should still allow with burst allowance
        allowed, info = rate_limiter.check_rate_limit(
            identifier="test:user:123",
            limit=10,
            window_seconds=60,
            burst_allowance=5
        )

        assert allowed is True  # Allowed due to burst
        assert info['burst_allowance'] == 5

    def test_check_multiple_windows(self, rate_limiter, redis_mock):
        """Test checking across multiple time windows"""
        manager = RateLimitManager(redis_mock)

        # Mock all windows to pass
        redis_mock.zcard.return_value = 5

        allowed, info = manager.limiter.check_multiple_windows(
            identifier="test:user:123",
            tier=RateLimitTier.FREE
        )

        assert allowed is True
        assert 'tier' in info
        assert info['tier'] == 'free'

    def test_redis_error_handling(self, redis_mock):
        """Test graceful handling of Redis errors"""
        redis_mock.zremrangebyscore.side_effect = redis.RedisError("Connection failed")

        limiter = SlidingWindowRateLimiter(redis_mock)
        allowed, info = limiter.check_rate_limit(
            identifier="test:user:123",
            limit=10,
            window_seconds=60
        )

        # Should fail open (allow request) when Redis is down
        assert allowed is True
        assert 'error' in info


class TestRateLimitManager:
    """Test rate limit manager"""

    def test_get_user_tier_anonymous(self, rate_limit_manager):
        """Test getting tier for anonymous user"""
        tier = rate_limit_manager.get_user_tier(user_id=None)

        assert tier == RateLimitTier.FREE
        assert tier['requests_per_minute'] == 10

    def test_get_user_tier_cached(self, rate_limit_manager, redis_mock):
        """Test getting tier from cache"""
        redis_mock.get.return_value = b'pro'

        tier = rate_limit_manager.get_user_tier(user_id="user123")

        assert tier == RateLimitTier.PRO
        assert tier['requests_per_minute'] == 60

    def test_set_user_tier(self, rate_limit_manager, redis_mock):
        """Test setting user tier"""
        rate_limit_manager.set_user_tier("user123", "enterprise", ttl=3600)

        redis_mock.setex.assert_called_once()
        args = redis_mock.setex.call_args[0]
        assert 'user_tier:user123' in args[0]
        assert args[1] == 3600
        assert args[2] == 'enterprise'

    def test_check_rate_limit_integration(self, rate_limit_manager, redis_mock):
        """Test full rate limit check"""
        redis_mock.zcard.return_value = 5

        allowed, info = rate_limit_manager.check_rate_limit(
            user_id="user123",
            endpoint="/api/v1/generate"
        )

        assert allowed is True
        assert 'tier' in info


class TestRateLimitDecorator:
    """Test rate limit decorator"""

    def test_rate_limit_decorator_allowed(self, flask_app, redis_mock):
        """Test rate limit decorator allows request"""
        with patch('core.rate_limiter.get_redis_client', return_value=redis_mock):
            redis_mock.zcard.return_value = 5

            @flask_app.route('/test')
            @rate_limit(tier=RateLimitTier.FREE)
            def test_route():
                return {'status': 'success'}

            with flask_app.test_client() as client:
                response = client.get('/test')

                assert response.status_code == 200
                assert 'X-RateLimit-Limit' in response.headers
                assert 'X-RateLimit-Remaining' in response.headers

    def test_rate_limit_decorator_blocked(self, flask_app, redis_mock):
        """Test rate limit decorator blocks request"""
        with patch('core.rate_limiter.get_redis_client', return_value=redis_mock):
            redis_mock.zcard.return_value = 10  # At limit

            @flask_app.route('/test')
            @rate_limit(tier=RateLimitTier.FREE)
            def test_route():
                return {'status': 'success'}

            with flask_app.test_client() as client:
                response = client.get('/test')

                assert response.status_code == 429
                assert response.json['error'] == 'rate_limit_exceeded'
                assert 'Retry-After' in response.headers


class TestConcurrentRequests:
    """Test concurrent request limiting"""

    def test_check_concurrent_requests_allowed(self, redis_mock):
        """Test concurrent requests within limit"""
        with patch('core.rate_limiter.get_redis_client', return_value=redis_mock):
            redis_mock.incr.return_value = 3

            allowed = check_concurrent_requests(user_id="user123", max_concurrent=5)

            assert allowed is True
            redis_mock.incr.assert_called_once()

    def test_check_concurrent_requests_blocked(self, redis_mock):
        """Test concurrent requests over limit"""
        with patch('core.rate_limiter.get_redis_client', return_value=redis_mock):
            redis_mock.incr.return_value = 6  # Over limit

            # Reset the global manager so it uses our mock
            import core.rate_limiter
            core.rate_limiter._rate_limit_manager = None

            allowed = check_concurrent_requests(user_id="user123", max_concurrent=5)

            assert allowed is False
            # When over limit, we decr after incr
            assert redis_mock.decr.call_count >= 1

    def test_release_concurrent_request(self, redis_mock):
        """Test releasing concurrent request slot"""
        with patch('core.rate_limiter.get_redis_client', return_value=redis_mock):
            # Reset the global manager so it uses our mock
            import core.rate_limiter
            core.rate_limiter._rate_limit_manager = None

            release_concurrent_request(user_id="user123")

            redis_mock.decr.assert_called_once()
class TestCircuitBreaker:
    """Test circuit breaker pattern"""

    def test_circuit_breaker_closed_state(self):
        """Test circuit breaker in closed state"""
        breaker = CircuitBreaker(failure_threshold=3)

        def working_func():
            return "success"

        result = breaker.call(working_func)

        assert result == "success"
        assert breaker.state == CircuitBreaker.CLOSED

    def test_circuit_breaker_opens_on_failures(self):
        """Test circuit breaker opens after failures"""
        breaker = CircuitBreaker(failure_threshold=3)

        def failing_func():
            raise Exception("Error")

        # Trigger failures
        for i in range(3):
            try:
                breaker.call(failing_func)
            except Exception:
                pass

        assert breaker.state == CircuitBreaker.OPEN

    def test_circuit_breaker_blocks_when_open(self):
        """Test circuit breaker blocks requests when open"""
        breaker = CircuitBreaker(failure_threshold=1)

        def failing_func():
            raise Exception("Error")

        # Trigger failure to open circuit
        try:
            breaker.call(failing_func)
        except Exception:
            pass

        # Circuit should be open now
        assert breaker.state == CircuitBreaker.OPEN

        # Should block further requests
        with pytest.raises(Exception, match="Circuit breaker is OPEN"):
            breaker.call(lambda: "success")

    def test_circuit_breaker_half_open_transition(self):
        """Test circuit breaker transitions to half-open"""
        breaker = CircuitBreaker(failure_threshold=1, timeout=1)

        def failing_func():
            raise Exception("Error")

        # Open circuit
        try:
            breaker.call(failing_func)
        except Exception:
            pass

        assert breaker.state == CircuitBreaker.OPEN

        # Wait for timeout
        time.sleep(1.1)

        # Should transition to half-open
        def working_func():
            return "success"

        result = breaker.call(working_func)
        assert breaker.state == CircuitBreaker.HALF_OPEN

    def test_circuit_breaker_closes_from_half_open(self):
        """Test circuit breaker closes from half-open after successes"""
        breaker = CircuitBreaker(failure_threshold=1, success_threshold=2, timeout=0)

        # Manually set to half-open
        breaker.state = CircuitBreaker.HALF_OPEN

        def working_func():
            return "success"

        # Call twice (success threshold)
        breaker.call(working_func)
        breaker.call(working_func)

        assert breaker.state == CircuitBreaker.CLOSED


class TestAPIGateway:
    """Test API gateway"""

    def test_api_gateway_initialization(self):
        """Test API gateway initialization"""
        gateway = APIGateway()

        assert isinstance(gateway.circuit_breakers, dict)
        assert isinstance(gateway.request_validators, dict)
        assert isinstance(gateway.response_transformers, dict)

    def test_get_circuit_breaker(self):
        """Test getting circuit breaker for service"""
        gateway = APIGateway()

        breaker1 = gateway.get_circuit_breaker("service1")
        breaker2 = gateway.get_circuit_breaker("service1")

        assert breaker1 is breaker2  # Same instance
        assert isinstance(breaker1, CircuitBreaker)

    def test_register_validator(self):
        """Test registering request validator"""
        gateway = APIGateway()

        def validator(data):
            return True, []

        gateway.register_validator("/test", validator)

        assert "/test" in gateway.request_validators

    def test_validate_request(self):
        """Test request validation"""
        gateway = APIGateway()

        def validator(data):
            if 'required_field' not in data:
                return False, ['required_field is missing']
            return True, []

        gateway.register_validator("/test", validator)

        # Test with missing field
        valid, errors = gateway.validate_request("/test", {})
        assert valid is False
        assert len(errors) > 0

        # Test with field present
        valid, errors = gateway.validate_request("/test", {'required_field': 'value'})
        assert valid is True
        assert len(errors) == 0


class TestAPIBlueprint:
    """Test API blueprint creation"""

    def test_create_api_blueprint_v1(self):
        """Test creating v1 API blueprint"""
        bp = create_api_blueprint(version='v1')

        assert bp.name == 'api_v1'
        assert bp.url_prefix == '/api/v1'

    def test_create_api_blueprint_v2(self):
        """Test creating v2 API blueprint"""
        bp = create_api_blueprint(version='v2')

        assert bp.name == 'api_v2'
        assert bp.url_prefix == '/api/v2'

    def test_api_blueprint_health_endpoint(self, flask_app):
        """Test health check endpoint"""
        bp = create_api_blueprint(version='v1')
        flask_app.register_blueprint(bp)

        with flask_app.test_client() as client:
            response = client.get('/api/v1/health')

            assert response.status_code == 200
            assert response.json['status'] == 'healthy'
            assert response.json['version'] == 'v1'

    def test_api_blueprint_info_endpoint(self, flask_app):
        """Test API info endpoint"""
        bp = create_api_blueprint(version='v1')
        flask_app.register_blueprint(bp)

        with flask_app.test_client() as client:
            response = client.get('/api/v1/info')

            assert response.status_code == 200
            assert response.json['version'] == 'v1'
            assert 'features' in response.json


class TestAPIGatewayDecorator:
    """Test API gateway decorator"""

    def test_api_gateway_decorator_success(self, flask_app):
        """Test API gateway decorator with successful request"""
        @flask_app.route('/test')
        @api_gateway(version='v1')
        def test_route():
            return {'status': 'success'}

        with flask_app.test_client() as client:
            response = client.get('/test')

            assert response.status_code == 200
            assert 'X-API-Version' in response.headers
            assert response.headers['X-API-Version'] == 'v1'

    def test_api_gateway_decorator_auth_required(self, flask_app):
        """Test API gateway decorator with authentication required"""
        @flask_app.route('/test')
        @api_gateway(version='v1', require_auth=True)
        def test_route():
            return {'status': 'success'}

        with flask_app.test_client() as client:
            response = client.get('/test')

            assert response.status_code == 401
            assert response.json['error'] == 'authentication_required'

    def test_api_gateway_decorator_with_auth(self, flask_app):
        """Test API gateway decorator with authenticated user"""
        @flask_app.route('/test')
        @api_gateway(version='v1', require_auth=True)
        def test_route():
            return {'status': 'success'}

        with flask_app.test_request_context('/test'):
            g.user_id = 'user123'

            with flask_app.test_client() as client:
                # Manually set g.user_id in request context
                with client.application.app_context():
                    g.user_id = 'user123'
                    response = test_route()

                    assert response['status'] == 'success'


class TestRateLimitTiers:
    """Test rate limit tier configurations"""

    def test_free_tier_limits(self):
        """Test FREE tier configuration"""
        tier = RateLimitTier.FREE

        assert tier['name'] == 'free'
        assert tier['requests_per_minute'] == 10
        assert tier['requests_per_hour'] == 100
        assert tier['requests_per_day'] == 1000

    def test_pro_tier_limits(self):
        """Test PRO tier configuration"""
        tier = RateLimitTier.PRO

        assert tier['name'] == 'pro'
        assert tier['requests_per_minute'] == 60
        assert tier['requests_per_hour'] == 1000
        assert tier['requests_per_day'] == 10000

    def test_enterprise_tier_limits(self):
        """Test ENTERPRISE tier configuration"""
        tier = RateLimitTier.ENTERPRISE

        assert tier['name'] == 'enterprise'
        assert tier['requests_per_minute'] == 300
        assert tier['requests_per_hour'] == 10000
        assert tier['requests_per_day'] == 100000

    def test_admin_tier_limits(self):
        """Test ADMIN tier configuration"""
        tier = RateLimitTier.ADMIN

        assert tier['name'] == 'admin'
        assert tier['requests_per_minute'] == 1000
        assert tier['concurrent_requests'] == 100


if __name__ == "__main__":
    pytest.main([__file__, '-v'])

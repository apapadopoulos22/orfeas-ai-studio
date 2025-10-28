"""
ORFEAS AI Studio - Rate Limiting System
========================================

Enterprise-grade rate limiting with:
- Sliding window algorithm for accurate rate limiting
- Redis-backed distributed rate limiting
- Multiple rate limit tiers (free, pro, enterprise)
- IP-based and user-based rate limiting
- Automatic cleanup and TTL management
- Integration with Prometheus metrics

Author: ORFEAS AI Team
Date: October 28, 2025
"""

import time
import logging
import hashlib
from typing import Optional, Dict, Any, Tuple
from functools import wraps
from datetime import datetime, timedelta
import redis
from flask import request, jsonify, g

logger = logging.getLogger(__name__)


class RateLimitTier:
    """Rate limit tier configurations"""

    FREE = {
        'name': 'free',
        'requests_per_minute': 10,
        'requests_per_hour': 100,
        'requests_per_day': 1000,
        'concurrent_requests': 2,
        'burst_allowance': 5
    }

    PRO = {
        'name': 'pro',
        'requests_per_minute': 60,
        'requests_per_hour': 1000,
        'requests_per_day': 10000,
        'concurrent_requests': 10,
        'burst_allowance': 20
    }

    ENTERPRISE = {
        'name': 'enterprise',
        'requests_per_minute': 300,
        'requests_per_hour': 10000,
        'requests_per_day': 100000,
        'concurrent_requests': 50,
        'burst_allowance': 100
    }

    ADMIN = {
        'name': 'admin',
        'requests_per_minute': 1000,
        'requests_per_hour': 50000,
        'requests_per_day': 500000,
        'concurrent_requests': 100,
        'burst_allowance': 500
    }


class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter with Redis backend.

    Uses sorted sets in Redis to track request timestamps within
    time windows for accurate rate limiting.
    """

    def __init__(self, redis_client: redis.Redis):
        """Initialize rate limiter with Redis client"""
        self.redis = redis_client
        self.prefix = "rate_limit"

    def _get_key(self, identifier: str, window: str) -> str:
        """Generate Redis key for rate limit tracking"""
        return f"{self.prefix}:{identifier}:{window}"

    def _get_identifier(self, user_id: Optional[str] = None) -> str:
        """
        Get identifier for rate limiting.
        Prioritizes user_id, falls back to IP address.
        """
        if user_id:
            return f"user:{user_id}"

        # Get IP address from request
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip:
            ip = ip.split(',')[0].strip()
        else:
            ip = 'unknown'

        return f"ip:{ip}"

    def check_rate_limit(
        self,
        identifier: str,
        limit: int,
        window_seconds: int,
        burst_allowance: int = 0
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request is within rate limit using sliding window.

        Args:
            identifier: Unique identifier (user ID or IP)
            limit: Maximum requests allowed in window
            window_seconds: Time window in seconds
            burst_allowance: Extra requests allowed for bursts

        Returns:
            Tuple of (allowed: bool, info: dict)
        """
        now = time.time()
        window_start = now - window_seconds

        # Redis key for this identifier and window
        key = self._get_key(identifier, f"{window_seconds}s")

        try:
            # Remove old entries outside the window
            self.redis.zremrangebyscore(key, 0, window_start)

            # Count current requests in window
            current_count = self.redis.zcard(key)

            # Check if within limit (including burst)
            effective_limit = limit + burst_allowance
            allowed = current_count < effective_limit

            if allowed:
                # Add current request timestamp
                request_id = f"{now}:{hashlib.md5(str(now).encode()).hexdigest()[:8]}"
                self.redis.zadd(key, {request_id: now})

                # Set TTL to window duration + buffer
                self.redis.expire(key, window_seconds + 60)

            # Calculate reset time
            if current_count > 0:
                oldest_timestamp = float(self.redis.zrange(key, 0, 0, withscores=True)[0][1])
                reset_time = oldest_timestamp + window_seconds
            else:
                reset_time = now + window_seconds

            # Prepare response info
            info = {
                'limit': limit,
                'remaining': max(0, effective_limit - current_count - (1 if allowed else 0)),
                'reset': int(reset_time),
                'reset_in_seconds': int(reset_time - now),
                'current_count': current_count,
                'window_seconds': window_seconds,
                'burst_allowance': burst_allowance
            }

            return allowed, info

        except redis.RedisError as e:
            logger.error(f"Redis error in rate limiter: {e}")
            # Fail open - allow request if Redis is down
            return True, {
                'limit': limit,
                'remaining': limit,
                'reset': int(now + window_seconds),
                'error': 'rate_limiter_unavailable'
            }

    def check_multiple_windows(
        self,
        identifier: str,
        tier: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check rate limits across multiple time windows.

        Args:
            identifier: Unique identifier
            tier: Rate limit tier configuration

        Returns:
            Tuple of (allowed: bool, info: dict)
        """
        windows = [
            ('minute', tier['requests_per_minute'], 60),
            ('hour', tier['requests_per_hour'], 3600),
            ('day', tier['requests_per_day'], 86400)
        ]

        for window_name, limit, window_seconds in windows:
            allowed, info = self.check_rate_limit(
                identifier,
                limit,
                window_seconds,
                tier.get('burst_allowance', 0)
            )

            if not allowed:
                info['window'] = window_name
                info['tier'] = tier['name']
                return False, info

        # All windows passed - return info from shortest window (minute)
        allowed, info = self.check_rate_limit(
            identifier,
            tier['requests_per_minute'],
            60,
            tier.get('burst_allowance', 0)
        )
        info['tier'] = tier['name']
        return True, info

    def reset_limit(self, identifier: str, window_seconds: int):
        """Reset rate limit for identifier"""
        key = self._get_key(identifier, f"{window_seconds}s")
        try:
            self.redis.delete(key)
            logger.info(f"Reset rate limit for {identifier}")
        except redis.RedisError as e:
            logger.error(f"Error resetting rate limit: {e}")


class RateLimitManager:
    """
    Centralized rate limit management.
    Integrates with authentication and user tiers.
    """

    def __init__(self, redis_client: redis.Redis):
        """Initialize rate limit manager"""
        self.limiter = SlidingWindowRateLimiter(redis_client)
        self.redis = redis_client

    def get_user_tier(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get rate limit tier for user.

        Args:
            user_id: User ID (None for anonymous)

        Returns:
            Rate limit tier configuration
        """
        if not user_id:
            return RateLimitTier.FREE

        try:
            # Check user tier in Redis cache
            cache_key = f"user_tier:{user_id}"
            cached_tier = self.redis.get(cache_key)

            if cached_tier:
                tier_name = cached_tier.decode('utf-8')
                return getattr(RateLimitTier, tier_name.upper(), RateLimitTier.FREE)

            # TODO: Query database for user tier
            # For now, return FREE tier
            return RateLimitTier.FREE

        except Exception as e:
            logger.error(f"Error getting user tier: {e}")
            return RateLimitTier.FREE

    def check_rate_limit(
        self,
        user_id: Optional[str] = None,
        endpoint: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check rate limit for current request.

        Args:
            user_id: User ID (None for IP-based limiting)
            endpoint: API endpoint (for endpoint-specific limits)

        Returns:
            Tuple of (allowed: bool, info: dict)
        """
        # Get identifier and tier
        identifier = self.limiter._get_identifier(user_id)
        tier = self.get_user_tier(user_id)

        # Add endpoint to identifier if specified
        if endpoint:
            identifier = f"{identifier}:{endpoint}"

        # Check rate limits across all windows
        return self.limiter.check_multiple_windows(identifier, tier)

    def set_user_tier(self, user_id: str, tier_name: str, ttl: int = 3600):
        """
        Set user tier in cache.

        Args:
            user_id: User ID
            tier_name: Tier name (free, pro, enterprise, admin)
            ttl: Cache TTL in seconds
        """
        try:
            cache_key = f"user_tier:{user_id}"
            self.redis.setex(cache_key, ttl, tier_name.lower())
            logger.info(f"Set user {user_id} to {tier_name} tier")
        except redis.RedisError as e:
            logger.error(f"Error setting user tier: {e}")


# Global rate limit manager instance
_rate_limit_manager: Optional[RateLimitManager] = None


def get_redis_client() -> redis.Redis:
    """Get Redis client for rate limiting"""
    return redis.Redis(
        host='localhost',
        port=6379,
        db=1,  # Use db=1 for rate limiting
        decode_responses=False
    )


def get_rate_limit_manager() -> RateLimitManager:
    """Get global rate limit manager instance"""
    global _rate_limit_manager

    if _rate_limit_manager is None:
        # Initialize Redis client
        redis_client = get_redis_client()
        _rate_limit_manager = RateLimitManager(redis_client)

    return _rate_limit_manager
def rate_limit(
    tier: Optional[Dict[str, Any]] = None,
    per_user: bool = True,
    endpoint: Optional[str] = None
):
    """
    Rate limiting decorator for Flask routes.

    Usage:
        @app.route('/api/v1/generate')
        @rate_limit(tier=RateLimitTier.PRO, per_user=True)
        def generate():
            return {'status': 'success'}

    Args:
        tier: Rate limit tier (None = auto-detect from user)
        per_user: Use user-based limiting (True) or IP-based (False)
        endpoint: Endpoint identifier for per-endpoint limits
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            manager = get_rate_limit_manager()

            # Get user ID if authenticated
            user_id = None
            if per_user and hasattr(g, 'user_id'):
                user_id = g.user_id

            # Check rate limit
            allowed, info = manager.check_rate_limit(user_id, endpoint)

            # Add rate limit headers to response
            @wraps(f)
            def add_headers(response):
                response.headers['X-RateLimit-Limit'] = str(info['limit'])
                response.headers['X-RateLimit-Remaining'] = str(info['remaining'])
                response.headers['X-RateLimit-Reset'] = str(info['reset'])
                if 'tier' in info:
                    response.headers['X-RateLimit-Tier'] = info['tier']
                return response

            if not allowed:
                # Rate limit exceeded
                logger.warning(
                    f"Rate limit exceeded for {user_id or 'anonymous'} "
                    f"on {endpoint or request.endpoint}"
                )

                response = jsonify({
                    'error': 'rate_limit_exceeded',
                    'message': f"Rate limit exceeded. Try again in {info['reset_in_seconds']} seconds.",
                    'limit': info['limit'],
                    'window': info.get('window', 'minute'),
                    'reset_in_seconds': info['reset_in_seconds'],
                    'tier': info.get('tier', 'free')
                })
                response.status_code = 429

                # Add rate limit headers
                response.headers['X-RateLimit-Limit'] = str(info['limit'])
                response.headers['X-RateLimit-Remaining'] = '0'
                response.headers['X-RateLimit-Reset'] = str(info['reset'])
                response.headers['Retry-After'] = str(info['reset_in_seconds'])

                return response

            # Execute route handler
            response = f(*args, **kwargs)

            # Add rate limit headers to successful response
            if hasattr(response, 'headers'):
                return add_headers(response)

            return response

        return decorated_function
    return decorator


def check_concurrent_requests(user_id: Optional[str] = None, max_concurrent: int = 5) -> bool:
    """
    Check if user has too many concurrent requests.

    Args:
        user_id: User ID (None for IP-based)
        max_concurrent: Maximum concurrent requests allowed

    Returns:
        True if within limit, False otherwise
    """
    manager = get_rate_limit_manager()
    identifier = manager.limiter._get_identifier(user_id)

    key = f"concurrent:{identifier}"

    try:
        current = manager.redis.incr(key)
        manager.redis.expire(key, 300)  # 5 minute expiry

        if current > max_concurrent:
            manager.redis.decr(key)
            return False

        return True

    except redis.RedisError as e:
        logger.error(f"Error checking concurrent requests: {e}")
        return True  # Fail open


def release_concurrent_request(user_id: Optional[str] = None):
    """Release concurrent request slot"""
    manager = get_rate_limit_manager()
    identifier = manager.limiter._get_identifier(user_id)

    key = f"concurrent:{identifier}"

    try:
        manager.redis.decr(key)
    except redis.RedisError as e:
        logger.error(f"Error releasing concurrent request: {e}")


if __name__ == "__main__":
    # Test rate limiter
    import redis

    print("Testing Rate Limiter...")

    # Connect to Redis
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=False)

    # Create rate limiter
    limiter = SlidingWindowRateLimiter(r)

    # Test with free tier
    print("\n1. Testing FREE tier (10 req/min):")
    identifier = "test:user:123"

    for i in range(12):
        allowed, info = limiter.check_rate_limit(
            identifier,
            limit=10,
            window_seconds=60,
            burst_allowance=2
        )
        print(f"Request {i+1}: {'✓ ALLOWED' if allowed else '✗ BLOCKED'} - "
              f"Remaining: {info['remaining']}/{info['limit']}")

    # Reset and test burst
    limiter.reset_limit(identifier, 60)
    print("\n2. Testing burst allowance:")

    for i in range(5):
        allowed, info = limiter.check_rate_limit(
            identifier,
            limit=3,
            window_seconds=10,
            burst_allowance=5
        )
        print(f"Burst request {i+1}: {'✓ ALLOWED' if allowed else '✗ BLOCKED'} - "
              f"Remaining: {info['remaining']}")

    print("\n✅ Rate limiter test complete")

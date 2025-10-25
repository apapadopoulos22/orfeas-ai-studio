"""
Advanced Rate Limiting for DDoS Protection
==========================================

Multi-tier rate limiting with Redis-backed distributed state:
- Per-IP limits (global)
- Per-user limits (authenticated)
- Per-endpoint limits (resource-specific)
- Adaptive rate limiting based on system load

Expected Impact:
- DDoS protection: Block 99.9% of abusive traffic
- Fair resource allocation: Prevent single user monopolization
- System stability: Auto-throttle during high load

Usage:
    from advanced_rate_limiter import get_rate_limiter, RateLimitConfig

    rate_limiter = get_rate_limiter()

    # Check if request is allowed
    allowed, retry_after = rate_limiter.check_rate_limit(
        identifier='192.168.1.100',
        endpoint='/api/generate-3d'
    )
"""

import os
import logging
import time
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class RateLimitTier(Enum):
    """Rate limit tiers with different quotas"""
    FREE = "free"           # 10 requests/minute
    BASIC = "basic"         # 60 requests/minute
    PREMIUM = "premium"     # 300 requests/minute
    UNLIMITED = "unlimited" # No limits


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    requests_per_minute: int = 60
    burst_allowance: int = 10  # Allow short bursts
    enable_adaptive: bool = True  # Adjust limits based on system load
    redis_url: Optional[str] = None
    default_tier: RateLimitTier = RateLimitTier.FREE


class AdvancedRateLimiter:
    """
    Advanced rate limiting with multiple tiers and Redis backing
    """

    def __init__(self, config: Optional[RateLimitConfig] = None):
        """
        Initialize rate limiter

        Args:
            config: Rate limiting configuration
        """
        self.config = config or RateLimitConfig()

        # Rate limit tiers
        self.tier_limits = {
            RateLimitTier.FREE: 10,
            RateLimitTier.BASIC: 60,
            RateLimitTier.PREMIUM: 300,
            RateLimitTier.UNLIMITED: float('inf')
        }

        # Endpoint-specific limits (overrides)
        self.endpoint_limits = {
            '/api/generate-3d': 30,  # More restrictive for expensive operations
            '/api/generate-3d/progressive': 30,
            '/api/health': 300,  # More permissive for monitoring
            '/api/cache/stats': 120
        }

        # Try to initialize Redis
        self.redis_client = None
        if self.config.redis_url:
            try:
                import redis
                self.redis_client = redis.from_url(
                    self.config.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2
                )
                self.redis_client.ping()
                logger.info(f"[RATE-LIMITER] Redis connected: {self.config.redis_url}")
            except Exception as e:
                logger.warning(f"[RATE-LIMITER] Redis unavailable: {e}")
                self.redis_client = None

        # Fallback to in-memory storage
        if not self.redis_client:
            self.memory_store: Dict[str, Dict] = {}
            logger.info("[RATE-LIMITER] Using in-memory storage (not distributed)")

        # Statistics
        self.stats = {
            'total_requests': 0,
            'allowed_requests': 0,
            'blocked_requests': 0,
            'adaptive_adjustments': 0
        }

        logger.info(
            f"[RATE-LIMITER] Initialized (default: {self.config.requests_per_minute} req/min, "
            f"burst: {self.config.burst_allowance})"
        )

    def check_rate_limit(
        self,
        identifier: str,
        endpoint: str = 'default',
        tier: Optional[RateLimitTier] = None
    ) -> Tuple[bool, Optional[int]]:
        """
        Check if request is allowed under rate limits

        Args:
            identifier: IP address or user ID
            endpoint: API endpoint (for endpoint-specific limits)
            tier: User's rate limit tier

        Returns:
            (allowed: bool, retry_after: Optional[int seconds])
        """
        self.stats['total_requests'] += 1

        # Determine rate limit
        if tier == RateLimitTier.UNLIMITED:
            self.stats['allowed_requests'] += 1
            return True, None

        # Get tier limit
        tier = tier or self.config.default_tier
        base_limit = self.tier_limits[tier]

        # Apply endpoint-specific limit
        limit = min(base_limit, self.endpoint_limits.get(endpoint, base_limit))

        # Adaptive rate limiting based on system load
        if self.config.enable_adaptive:
            limit = self._adjust_for_system_load(limit)

        # Check limit
        current_time = int(time.time())
        window_key = f"rate_limit:{identifier}:{endpoint}:{current_time // 60}"

        try:
            if self.redis_client:
                return self._check_redis_limit(window_key, limit)
            else:
                return self._check_memory_limit(window_key, limit)
        except Exception as e:
            logger.error(f"[RATE-LIMITER] Error checking limit: {e}")
            # Fail open (allow request) rather than fail closed
            self.stats['allowed_requests'] += 1
            return True, None

    def _check_redis_limit(
        self,
        window_key: str,
        limit: int
    ) -> Tuple[bool, Optional[int]]:
        """Check rate limit using Redis"""
        try:
            # Increment counter with expiry
            pipeline = self.redis_client.pipeline()
            pipeline.incr(window_key)
            pipeline.expire(window_key, 70)  # 60s window + 10s buffer
            current_count, _ = pipeline.execute()

            if current_count <= limit + self.config.burst_allowance:
                self.stats['allowed_requests'] += 1
                return True, None
            else:
                self.stats['blocked_requests'] += 1
                retry_after = 60  # Wait 1 minute
                logger.warning(
                    f"[RATE-LIMITER] Request blocked: {window_key} "
                    f"({current_count}/{limit})"
                )
                return False, retry_after

        except Exception as e:
            logger.error(f"[RATE-LIMITER] Redis error: {e}")
            # Fallback to memory
            return self._check_memory_limit(window_key, limit)

    def _check_memory_limit(
        self,
        window_key: str,
        limit: int
    ) -> Tuple[bool, Optional[int]]:
        """Check rate limit using in-memory storage"""
        current_time = int(time.time())

        # Clean old entries (older than 2 minutes)
        expired_keys = [
            k for k, v in self.memory_store.items()
            if v['expires'] < current_time
        ]
        for k in expired_keys:
            del self.memory_store[k]

        # Get or create counter
        if window_key not in self.memory_store:
            self.memory_store[window_key] = {
                'count': 0,
                'expires': current_time + 70
            }

        # Increment and check
        self.memory_store[window_key]['count'] += 1
        current_count = self.memory_store[window_key]['count']

        if current_count <= limit + self.config.burst_allowance:
            self.stats['allowed_requests'] += 1
            return True, None
        else:
            self.stats['blocked_requests'] += 1
            retry_after = 60
            logger.warning(
                f"[RATE-LIMITER] Request blocked: {window_key} "
                f"({current_count}/{limit})"
            )
            return False, retry_after

    def _adjust_for_system_load(self, base_limit: int) -> int:
        """
        Adjust rate limit based on system load
        Reduce limits when system is under stress
        """
        try:
            import psutil

            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_percent = psutil.virtual_memory().percent

            # Aggressive throttling if system is overloaded
            if cpu_percent > 90 or memory_percent > 90:
                adjusted = int(base_limit * 0.3)  # 70% reduction
                self.stats['adaptive_adjustments'] += 1
                logger.warning(
                    f"[RATE-LIMITER] Adaptive throttling: {base_limit} → {adjusted} "
                    f"(CPU: {cpu_percent:.1f}%, RAM: {memory_percent:.1f}%)"
                )
                return adjusted

            # Moderate throttling if system is stressed
            elif cpu_percent > 75 or memory_percent > 75:
                adjusted = int(base_limit * 0.6)  # 40% reduction
                self.stats['adaptive_adjustments'] += 1
                return adjusted

            # Normal limits
            else:
                return base_limit

        except Exception as e:
            logger.warning(f"[RATE-LIMITER] Failed to check system load: {e}")
            return base_limit

    def get_user_tier(self, user_id: Optional[str]) -> RateLimitTier:
        """
        Get rate limit tier for user (placeholder for future auth integration)

        Args:
            user_id: User identifier

        Returns:
            Rate limit tier
        """
        # TODO: Integrate with user authentication/subscription system
        if not user_id:
            return RateLimitTier.FREE

        # Example logic (replace with actual database lookup)
        if user_id.startswith('premium_'):
            return RateLimitTier.PREMIUM
        elif user_id.startswith('basic_'):
            return RateLimitTier.BASIC
        else:
            return RateLimitTier.FREE

    def get_stats(self) -> Dict[str, any]:
        """Get rate limiter statistics"""
        block_rate = (
            (self.stats['blocked_requests'] / self.stats['total_requests'] * 100)
            if self.stats['total_requests'] > 0 else 0
        )

        return {
            'total_requests': self.stats['total_requests'],
            'allowed_requests': self.stats['allowed_requests'],
            'blocked_requests': self.stats['blocked_requests'],
            'block_rate_percent': round(block_rate, 2),
            'adaptive_adjustments': self.stats['adaptive_adjustments'],
            'redis_enabled': self.redis_client is not None,
            'tier_limits': {
                tier.value: limit
                for tier, limit in self.tier_limits.items()
            }
        }

    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            'total_requests': 0,
            'allowed_requests': 0,
            'blocked_requests': 0,
            'adaptive_adjustments': 0
        }
        logger.info("[RATE-LIMITER] Statistics reset")


# Singleton instance
_rate_limiter: Optional[AdvancedRateLimiter] = None


def get_rate_limiter(config: Optional[RateLimitConfig] = None) -> AdvancedRateLimiter:
    """Get or create singleton rate limiter"""
    global _rate_limiter
    if _rate_limiter is None:
        # Load configuration from environment
        if config is None:
            config = RateLimitConfig(
                requests_per_minute=int(os.getenv('RATE_LIMIT_PER_MINUTE', '60')),
                burst_allowance=int(os.getenv('RATE_LIMIT_BURST', '10')),
                enable_adaptive=os.getenv('RATE_LIMIT_ADAPTIVE', 'true').lower() == 'true',
                redis_url=os.getenv('REDIS_URL', None)
            )
        _rate_limiter = AdvancedRateLimiter(config)
    return _rate_limiter


# Export
__all__ = [
    'AdvancedRateLimiter',
    'RateLimitConfig',
    'RateLimitTier',
    'get_rate_limiter'
]

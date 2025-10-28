#!/usr/bin/env python3
"""
BOB AI v10.0 - PHASE 4.6 RATE LIMITER
Request Rate Limiting with Token Bucket Algorithm

Implements token bucket algorithm for rate limiting
Supports per-key rate limits with time windows

Version: 1.0.0
Date: October 28, 2025
Status: PHASE 4.6 IMPLEMENTATION
"""

import logging
import time
from typing import Dict, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class TokenBucket:
    """Token bucket for rate limiting"""

    def __init__(self, capacity: int, refill_rate: float = 1.0):
        """
        Initialize token bucket

        Args:
            capacity: Maximum tokens in bucket
            refill_rate: Tokens added per second (1.0 = 60 per minute)
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_refill = time.time()

    def refill(self):
        """Refill bucket based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill

        # Add tokens based on elapsed time
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)

        self.last_refill = now

    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens from bucket

        Returns:
            True if tokens available, False otherwise
        """
        self.refill()

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True

        return False

    def get_tokens(self) -> float:
        """Get current number of tokens"""
        self.refill()
        return self.tokens

    def reset(self):
        """Reset bucket to full capacity"""
        self.tokens = float(self.capacity)
        self.last_refill = time.time()


class RateLimiter:
    """Rate limiter for API requests"""

    def __init__(self):
        self.buckets: Dict[str, TokenBucket] = {}
        logger.info("Initialized rate limiter")

    def get_bucket(
        self,
        key: str,
        requests_per_minute: int = 100
    ) -> TokenBucket:
        """Get or create token bucket for a key"""
        if key not in self.buckets:
            # Convert requests per minute to tokens per second
            refill_rate = requests_per_minute / 60.0
            self.buckets[key] = TokenBucket(
                capacity=requests_per_minute,
                refill_rate=refill_rate
            )
            logger.debug(f"Created bucket for {key}: {requests_per_minute} req/min")

        return self.buckets[key]

    def is_allowed(
        self,
        key: str,
        requests_per_minute: int = 100,
        tokens: int = 1
    ) -> Tuple[bool, int]:
        """
        Check if request is allowed

        Returns:
            Tuple of (is_allowed, remaining_tokens)
        """
        bucket = self.get_bucket(key, requests_per_minute)

        allowed = bucket.consume(tokens)
        remaining = int(bucket.get_tokens())

        if allowed:
            logger.debug(f"Rate limit OK: {key} ({remaining} tokens remaining)")
        else:
            logger.warning(f"Rate limit exceeded: {key}")

        return allowed, remaining

    def get_status(self, key: str, requests_per_minute: int = 100) -> Dict:
        """Get rate limit status for a key"""
        bucket = self.get_bucket(key, requests_per_minute)
        bucket.refill()

        return {
            'key': key,
            'capacity': bucket.capacity,
            'current_tokens': int(bucket.tokens),
            'remaining_requests': int(bucket.tokens),
            'requests_per_minute': requests_per_minute,
            'refill_rate': bucket.refill_rate
        }

    def reset_key(self, key: str):
        """Reset rate limit for a key"""
        if key in self.buckets:
            self.buckets[key].reset()
            logger.info(f"Reset rate limit for {key}")

    def get_all_stats(self) -> Dict:
        """Get statistics for all rate-limited keys"""
        stats = {}
        for key, bucket in self.buckets.items():
            bucket.refill()
            stats[key] = {
                'tokens': int(bucket.tokens),
                'capacity': bucket.capacity,
                'refill_rate': bucket.refill_rate
            }
        return stats


class RateLimitException(Exception):
    """Exception raised when rate limit is exceeded"""

    def __init__(self, key: str, limit: int, retry_after: int = 60):
        self.key = key
        self.limit = limit
        self.retry_after = retry_after
        super().__init__(
            f"Rate limit exceeded for {key}. Limit: {limit} req/min. Retry after: {retry_after}s"
        )


def get_rate_limiter() -> RateLimiter:
    """Get or create rate limiter singleton"""
    if not hasattr(get_rate_limiter, '_instance'):
        get_rate_limiter._instance = RateLimiter()
    return get_rate_limiter._instance


if __name__ == '__main__':
    # Test rate limiter
    logging.basicConfig(level=logging.INFO)

    limiter = get_rate_limiter()

    # Test rate limiting
    api_key = "test_key_123"
    limit = 10  # 10 requests per minute

    print(f"Testing rate limiter with {limit} requests per minute...")

    # Make 15 requests
    for i in range(15):
        allowed, remaining = limiter.is_allowed(api_key, limit)
        status = "✓" if allowed else "✗"
        print(f"Request {i+1}: {status} (remaining: {remaining})")

        if i == 9:
            print("Waiting 2 seconds for token refill...")
            time.sleep(2)

    # Get status
    print(f"\nStatus: {limiter.get_status(api_key, limit)}")

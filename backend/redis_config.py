# Redis Configuration for ORFEAS AI Studio
# Distributed caching and session management

import os
import redis
from redis.connection import ConnectionPool
from functools import wraps
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

# ============================================
# REDIS CONNECTION CONFIGURATION
# ============================================

class RedisConfig:
    """Redis configuration for distributed caching"""

    # Connection parameters
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

    # Connection pool
    REDIS_POOL_MAX_CONNECTIONS = int(os.getenv('REDIS_POOL_MAX_CONNECTIONS', 50))

    # Timeout settings
    REDIS_SOCKET_CONNECT_TIMEOUT = 5
    REDIS_SOCKET_TIMEOUT = 5
    REDIS_RETRY_ON_TIMEOUT = True

    # Cache TTL defaults
    CACHE_TTL_SHORT = int(os.getenv('CACHE_TTL_SHORT', 300))  # 5 minutes
    CACHE_TTL_MEDIUM = int(os.getenv('CACHE_TTL_MEDIUM', 3600))  # 1 hour
    CACHE_TTL_LONG = int(os.getenv('CACHE_TTL_LONG', 86400))  # 24 hours

    # Key prefixes
    CACHE_PREFIX = os.getenv('CACHE_PREFIX', 'orfeas:')
    SESSION_PREFIX = os.getenv('SESSION_PREFIX', 'session:')
    JOB_PREFIX = os.getenv('JOB_PREFIX', 'job:')
    MODEL_PREFIX = os.getenv('MODEL_PREFIX', 'model:')


class RedisClient:
    """Thread-safe Redis client singleton"""

    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            try:
                self.pool = ConnectionPool(
                    host=RedisConfig.REDIS_HOST,
                    port=RedisConfig.REDIS_PORT,
                    db=RedisConfig.REDIS_DB,
                    password=RedisConfig.REDIS_PASSWORD,
                    max_connections=RedisConfig.REDIS_POOL_MAX_CONNECTIONS,
                    socket_connect_timeout=RedisConfig.REDIS_SOCKET_CONNECT_TIMEOUT,
                    socket_timeout=RedisConfig.REDIS_SOCKET_TIMEOUT,
                    retry_on_timeout=RedisConfig.REDIS_RETRY_ON_TIMEOUT,
                )
                self._client = redis.Redis(connection_pool=self.pool)

                # Test connection
                self._client.ping()
                logger.info(
                    f"✅ Redis client initialized: {RedisConfig.REDIS_HOST}:"
                    f"{RedisConfig.REDIS_PORT}/{RedisConfig.REDIS_DB}"
                )
            except redis.ConnectionError as e:
                logger.error(f"❌ Redis connection failed: {e}")
                self._client = None

    @property
    def client(self):
        """Get Redis client instance"""
        return self._client

    def is_available(self):
        """Check if Redis is available"""
        try:
            if self._client:
                self._client.ping()
                return True
        except Exception:
            pass
        return False


# ============================================
# CACHE DECORATORS
# ============================================

def redis_cache(ttl=RedisConfig.CACHE_TTL_MEDIUM, prefix="cache"):
    """
    Decorator for caching function results in Redis

    Usage:
        @redis_cache(ttl=3600, prefix="user")
        def get_user_data(user_id):
            return {"id": user_id, "name": "John"}
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            redis_client = RedisClient().client

            if not redis_client:
                # Fallback: execute function without cache
                return func(*args, **kwargs)

            # Generate cache key
            cache_key = f"{prefix}:{func.__name__}:{args}:{kwargs}"
            cache_key = cache_key.replace(" ", "")

            # Try to get from cache
            try:
                cached = redis_client.get(cache_key)
                if cached:
                    logger.debug(f"Cache hit: {cache_key}")
                    import json
                    return json.loads(cached)
            except Exception as e:
                logger.warning(f"Cache get failed: {e}")

            # Execute function
            result = func(*args, **kwargs)

            # Store in cache
            try:
                import json
                redis_client.setex(
                    cache_key,
                    timedelta(seconds=ttl),
                    json.dumps(result)
                )
                logger.debug(f"Cached: {cache_key} (TTL: {ttl}s)")
            except Exception as e:
                logger.warning(f"Cache set failed: {e}")

            return result

        return wrapper
    return decorator


def redis_invalidate(pattern):
    """
    Decorator to invalidate Redis cache keys matching a pattern

    Usage:
        @redis_invalidate(pattern="user:*")
        def update_user(user_id, name):
            # Cache will be invalidated after function execution
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            redis_client = RedisClient().client
            if redis_client:
                try:
                    keys = redis_client.keys(pattern)
                    if keys:
                        redis_client.delete(*keys)
                        logger.info(f"Invalidated {len(keys)} cache keys: {pattern}")
                except Exception as e:
                    logger.warning(f"Cache invalidation failed: {e}")

            return result
        return wrapper
    return decorator


# ============================================
# SESSION MANAGEMENT
# ============================================

class RedisSessionManager:
    """Manage user sessions with Redis"""

    def __init__(self):
        self.redis_client = RedisClient().client
        self.ttl = RedisConfig.CACHE_TTL_LONG

    def create_session(self, session_id, data):
        """Create new session"""
        if not self.redis_client:
            logger.error("Redis not available for session creation")
            return False

        try:
            key = f"{RedisConfig.SESSION_PREFIX}{session_id}"
            import json
            self.redis_client.setex(key, timedelta(seconds=self.ttl), json.dumps(data))
            logger.info(f"Session created: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Session creation failed: {e}")
            return False

    def get_session(self, session_id):
        """Get session data"""
        if not self.redis_client:
            return None

        try:
            key = f"{RedisConfig.SESSION_PREFIX}{session_id}"
            data = self.redis_client.get(key)
            if data:
                import json
                return json.loads(data)
        except Exception as e:
            logger.error(f"Session retrieval failed: {e}")
        return None

    def update_session(self, session_id, data):
        """Update session data"""
        if not self.redis_client:
            return False

        try:
            key = f"{RedisConfig.SESSION_PREFIX}{session_id}"
            import json
            self.redis_client.setex(key, timedelta(seconds=self.ttl), json.dumps(data))
            return True
        except Exception as e:
            logger.error(f"Session update failed: {e}")
            return False

    def delete_session(self, session_id):
        """Delete session"""
        if not self.redis_client:
            return False

        try:
            key = f"{RedisConfig.SESSION_PREFIX}{session_id}"
            self.redis_client.delete(key)
            logger.info(f"Session deleted: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Session deletion failed: {e}")
            return False


# ============================================
# JOB QUEUE MANAGEMENT
# ============================================

class RedisJobQueue:
    """Manage async job queuing with Redis"""

    def __init__(self, queue_name="default"):
        self.redis_client = RedisClient().client
        self.queue_name = queue_name
        self.queue_key = f"{RedisConfig.JOB_PREFIX}{queue_name}"

    def enqueue_job(self, job_id, job_data):
        """Add job to queue"""
        if not self.redis_client:
            logger.error("Redis not available for job queueing")
            return False

        try:
            import json
            self.redis_client.rpush(self.queue_key, json.dumps({"id": job_id, "data": job_data}))
            logger.info(f"Job queued: {job_id} in {self.queue_name}")
            return True
        except Exception as e:
            logger.error(f"Job queueing failed: {e}")
            return False

    def dequeue_job(self):
        """Get next job from queue"""
        if not self.redis_client:
            return None

        try:
            job = self.redis_client.lpop(self.queue_key)
            if job:
                import json
                return json.loads(job)
        except Exception as e:
            logger.error(f"Job dequeueing failed: {e}")
        return None

    def get_queue_size(self):
        """Get number of jobs in queue"""
        if not self.redis_client:
            return 0

        try:
            return self.redis_client.llen(self.queue_key)
        except Exception as e:
            logger.error(f"Queue size check failed: {e}")
            return 0


# ============================================
# INITIALIZATION
# ============================================

def initialize_redis():
    """Initialize Redis client on app startup"""
    try:
        redis_client = RedisClient()
        if redis_client.is_available():
            logger.info("✅ Redis initialized successfully")
            return True
        else:
            logger.warning("⚠️  Redis unavailable - falling back to in-memory cache")
            return False
    except Exception as e:
        logger.error(f"❌ Redis initialization failed: {e}")
        return False


# Convenience instances
session_manager = RedisSessionManager()
job_queue_default = RedisJobQueue("default")
job_queue_priority = RedisJobQueue("priority")

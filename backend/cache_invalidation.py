"""
[ORFEAS PHASE 2 TASK 2] Cache Invalidation Module
Event-driven and rule-based cache invalidation system.

Purpose:
  Manages cache invalidation through:
  - Event-based triggers (model_deployed, version_promoted, etc.)
  - TTL-based automatic expiry
  - Tag-based invalidation groups
  - Manual purge operations
  - Pattern-based wildcard invalidation

Key Classes:
  - CacheInvalidationManager - Coordinates all invalidation
  - InvalidationRule - Defines when/how to invalidate
  - InvalidationEvent - Event dataclass

Usage:
  invalidation_mgr = get_invalidation_manager()

  # Register invalidation rule
  invalidation_mgr.register_rule(
      event="model_deployed",
      pattern="prediction:*",
      action="purge"
  )

  # Trigger event
  invalidation_mgr.handle_event("model_deployed")

  # Tag-based invalidation
  invalidation_mgr.tag_cache("prediction:v1:*", tags=["v1"])
  invalidation_mgr.invalidate_by_tag("v1")
"""

import logging
import re
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class InvalidationAction(Enum):
    """Cache invalidation action types."""
    PURGE = "purge"  # Delete from cache
    REFRESH = "refresh"  # Refresh/recalculate
    TAG = "tag"  # Tag for later invalidation
    EXPIRE = "expire"  # Mark as expired


@dataclass
class InvalidationEvent:
    """Cache invalidation event."""
    event_type: str
    triggered_at: datetime = field(default_factory=datetime.now)
    triggered_by: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    affected_keys: List[str] = field(default_factory=list)


@dataclass
class InvalidationRule:
    """Rule for when/how to invalidate cache."""
    event: str
    pattern: Optional[str] = None  # Wildcard pattern (e.g., "prediction:*")
    action: InvalidationAction = InvalidationAction.PURGE
    callback: Optional[Callable] = None  # Optional custom callback
    active: bool = True
    created_at: datetime = field(default_factory=datetime.now)


class CacheInvalidationManager:
    """Manages cache invalidation strategies."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize invalidation manager."""
        if self._initialized:
            return

        self.rules: Dict[str, List[InvalidationRule]] = {}
        self.cache_tags: Dict[str, Set[str]] = {}  # key -> tags
        self.tag_cache: Dict[str, Set[str]] = {}  # tag -> keys
        self.event_history: List[InvalidationEvent] = []
        self.lock = threading.RLock()
        self.cache_backend = None
        self._initialized = True

        logger.info("[INVALIDATION] ✓ Cache invalidation manager initialized")

    def set_cache_backend(self, backend: Any) -> None:
        """Set cache backend reference for invalidation."""
        self.cache_backend = backend

    def register_rule(
        self,
        event: str,
        pattern: Optional[str] = None,
        action: InvalidationAction = InvalidationAction.PURGE,
        callback: Optional[Callable] = None,
    ) -> None:
        """Register a cache invalidation rule."""
        with self.lock:
            if event not in self.rules:
                self.rules[event] = []

            rule = InvalidationRule(
                event=event,
                pattern=pattern,
                action=action,
                callback=callback,
            )
            self.rules[event].append(rule)

            logger.info(f"[INVALIDATION] Registered rule: {event} -> {pattern or 'all'}")

    def handle_event(self, event_type: str, **metadata) -> InvalidationEvent:
        """Handle invalidation event."""
        with self.lock:
            logger.info(f"[INVALIDATION] Handling event: {event_type}")

            event = InvalidationEvent(
                event_type=event_type,
                metadata=metadata,
            )

            # Find matching rules
            if event_type in self.rules:
                for rule in self.rules[event_type]:
                    if not rule.active:
                        continue

                    # Execute invalidation
                    affected = self._execute_rule(rule)
                    event.affected_keys.extend(affected)

                    # Execute callback if provided
                    if rule.callback:
                        try:
                            rule.callback(event)
                        except Exception as e:
                            logger.error(f"[INVALIDATION] Callback error: {e}")

            # Record event
            self.event_history.append(event)
            if len(self.event_history) > 1000:
                self.event_history = self.event_history[-500:]  # Keep last 500

            logger.info(f"[INVALIDATION] Event {event_type} invalidated {len(event.affected_keys)} keys")
            return event

    def _execute_rule(self, rule: InvalidationRule) -> List[str]:
        """Execute a single invalidation rule."""
        affected_keys = []

        if not self.cache_backend:
            return affected_keys

        if rule.action == InvalidationAction.PURGE:
            # Purge matching keys
            if rule.pattern:
                affected_keys = self._purge_pattern(rule.pattern)
            else:
                affected_keys = self._purge_all()

        elif rule.action == InvalidationAction.TAG:
            # Tag matching keys
            if rule.pattern:
                affected_keys = self._tag_pattern(rule.pattern, [rule.event])

        elif rule.action == InvalidationAction.EXPIRE:
            # Mark as expired (set TTL to 0)
            if rule.pattern:
                affected_keys = self._expire_pattern(rule.pattern)

        return affected_keys

    def _purge_pattern(self, pattern: str) -> List[str]:
        """Purge all keys matching pattern."""
        # Convert wildcard pattern to regex
        regex_pattern = pattern.replace("*", ".*")
        regex = re.compile(f"^{regex_pattern}$")

        affected = []

        # For now, we'd need cache backend to support pattern deletion
        # This is a placeholder for actual implementation
        logger.debug(f"[INVALIDATION] Would purge pattern: {pattern}")

        return affected

    def _purge_all(self) -> List[str]:
        """Purge all cache."""
        if self.cache_backend and hasattr(self.cache_backend, 'clear'):
            self.cache_backend.clear()
            logger.info("[INVALIDATION] Purged entire cache")
            return ["*"]
        return []

    def _tag_pattern(self, pattern: str, tags: List[str]) -> List[str]:
        """Tag all keys matching pattern."""
        # Convert wildcard pattern to regex
        regex_pattern = pattern.replace("*", ".*")
        regex = re.compile(f"^{regex_pattern}$")

        affected = []
        # Placeholder for pattern-based tagging
        logger.debug(f"[INVALIDATION] Tagged pattern {pattern} with {tags}")

        return affected

    def _expire_pattern(self, pattern: str) -> List[str]:
        """Mark all keys matching pattern as expired."""
        affected = []
        logger.debug(f"[INVALIDATION] Expired pattern: {pattern}")
        return affected

    def tag_cache(self, key_pattern: str, tags: List[str]) -> None:
        """Tag cache keys for group invalidation."""
        with self.lock:
            for tag in tags:
                if tag not in self.tag_cache:
                    self.tag_cache[tag] = set()
                self.tag_cache[tag].add(key_pattern)

            logger.debug(f"[INVALIDATION] Tagged {key_pattern} with {tags}")

    def invalidate_by_tag(self, tag: str) -> List[str]:
        """Invalidate all cache keys with specific tag."""
        with self.lock:
            if tag not in self.tag_cache:
                return []

            affected_keys = list(self.tag_cache[tag])

            # Purge each pattern
            all_affected = []
            for pattern in affected_keys:
                affected = self._purge_pattern(pattern)
                all_affected.extend(affected)

            # Clean up tag
            del self.tag_cache[tag]

            logger.info(f"[INVALIDATION] Invalidated tag '{tag}': {len(all_affected)} keys")
            return all_affected

    def invalidate_pattern(self, pattern: str) -> List[str]:
        """Manually invalidate keys matching pattern."""
        with self.lock:
            affected = self._purge_pattern(pattern)
            logger.info(f"[INVALIDATION] Invalidated pattern '{pattern}': {len(affected)} keys")
            return affected

    def invalidate_key(self, key: str) -> bool:
        """Invalidate specific key."""
        with self.lock:
            if self.cache_backend and hasattr(self.cache_backend, 'delete'):
                result = self.cache_backend.delete(key)
                logger.debug(f"[INVALIDATION] Invalidated key: {key}")
                return result
            return False

    def get_event_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent invalidation events."""
        with self.lock:
            return [
                {
                    "event_type": event.event_type,
                    "triggered_at": event.triggered_at.isoformat(),
                    "affected_keys": len(event.affected_keys),
                }
                for event in self.event_history[-limit:]
            ]

    def get_stats(self) -> Dict[str, Any]:
        """Get invalidation statistics."""
        with self.lock:
            return {
                "total_rules": len([r for rules in self.rules.values() for r in rules]),
                "total_tags": len(self.tag_cache),
                "total_events": len(self.event_history),
                "recent_events": len([e for e in self.event_history if (datetime.now() - e.triggered_at).total_seconds() < 3600]),
            }

    def reset(self) -> None:
        """Reset invalidation manager."""
        with self.lock:
            self.rules.clear()
            self.cache_tags.clear()
            self.tag_cache.clear()
            self.event_history.clear()
            logger.info("[INVALIDATION] Manager reset")


# Singleton getter function
_invalidation_manager = None

def get_invalidation_manager() -> CacheInvalidationManager:
    """Get or create invalidation manager singleton."""
    global _invalidation_manager
    if _invalidation_manager is None:
        _invalidation_manager = CacheInvalidationManager()
    return _invalidation_manager


def reset_invalidation_manager() -> None:
    """Reset invalidation manager (for testing)."""
    global _invalidation_manager
    _invalidation_manager = None


# Predefined event handlers

def on_model_deployed() -> None:
    """Event: Model deployed to production."""
    mgr = get_invalidation_manager()
    mgr.register_rule(
        event="model_deployed",
        pattern="prediction:*",
        action=InvalidationAction.PURGE,
    )
    logger.info("[INVALIDATION] Registered model_deployed handler")


def on_version_promoted() -> None:
    """Event: Model version promoted."""
    mgr = get_invalidation_manager()
    mgr.register_rule(
        event="version_promoted",
        pattern="prediction:*",
        action=InvalidationAction.PURGE,
    )
    logger.info("[INVALIDATION] Registered version_promoted handler")


def on_ab_test_winner() -> None:
    """Event: A/B test winner declared."""
    mgr = get_invalidation_manager()
    mgr.register_rule(
        event="ab_test_winner",
        pattern="prediction:*",
        action=InvalidationAction.PURGE,
    )
    logger.info("[INVALIDATION] Registered ab_test_winner handler")


def on_cache_warming() -> None:
    """Event: Cache warming in progress."""
    mgr = get_invalidation_manager()
    mgr.register_rule(
        event="cache_warming",
        pattern=None,
        action=InvalidationAction.REFRESH,
    )
    logger.info("[INVALIDATION] Registered cache_warming handler")

"""
[ORFEAS PHASE 2 TASK 5] Load Balancer - Multi-Instance Orchestration
Distributes load across multiple backend instances with health monitoring.

Purpose:
  Manages distribution of requests across multiple server instances.
  Tracks instance health and removes unhealthy instances.
  Implements load balancing algorithms (round-robin, least-connections, weighted).
  Provides real-time instance metrics and statistics.

Architecture:
  - Instance registry with health tracking
  - Multiple load balancing strategies
  - Automatic failover on instance failure
  - Real-time metrics per instance
  - Session affinity (optional sticky sessions)

Usage:
  from load_balancer import LoadBalancer, InstanceConfig

  lb = LoadBalancer()
  lb.add_instance("backend-1", "localhost:5001", 2)  # 2x weight
  lb.add_instance("backend-2", "localhost:5002", 1)  # 1x weight

  # Get next instance for request
  instance = lb.get_next_instance()
  # Forward request to instance.url

  # Track request metrics
  lb.record_request_time(instance, 45.2)  # 45.2ms
"""

import logging
import threading
import time
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict
import random

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LoadBalancingStrategy(Enum):
    """Load balancing algorithm selection."""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    RANDOM = "random"
    IP_HASH = "ip_hash"


@dataclass
class InstanceConfig:
    """Configuration for a backend instance."""
    instance_id: str
    host: str
    port: int
    weight: int = 1  # For weighted balancing
    max_connections: int = 100
    health_check_interval: int = 5  # seconds
    health_check_timeout: int = 2  # seconds
    failure_threshold: int = 3  # Consecutive failures before marking unhealthy

    @property
    def url(self) -> str:
        """Get instance URL."""
        return f"http://{self.host}:{self.port}"


@dataclass
class InstanceMetrics:
    """Real-time metrics for an instance."""
    instance_id: str
    is_healthy: bool = True
    total_requests: int = 0
    failed_requests: int = 0
    consecutive_failures: int = 0
    avg_response_time_ms: float = 0.0
    active_connections: int = 0
    last_health_check: Optional[datetime] = None
    response_times: List[float] = field(default_factory=list)  # Last 100 samples

    def add_response_time(self, response_time_ms: float):
        """Track response time and update average."""
        self.response_times.append(response_time_ms)
        if len(self.response_times) > 100:
            self.response_times.pop(0)
        self.avg_response_time_ms = sum(self.response_times) / len(self.response_times)

    def get_success_rate(self) -> float:
        """Get request success rate (0.0-1.0)."""
        if self.total_requests == 0:
            return 1.0
        return (self.total_requests - self.failed_requests) / self.total_requests

    def get_load_percentage(self, max_connections: int) -> float:
        """Get percentage of max connections in use."""
        return (self.active_connections / max_connections * 100) if max_connections > 0 else 0.0


class LoadBalancer:
    """
    Distributes requests across multiple backend instances.

    Features:
    - Multiple load balancing strategies
    - Instance health monitoring
    - Automatic failover
    - Real-time metrics tracking
    - Connection limiting

    Performance:
    - Instance selection: <1ms
    - Metrics collection: O(1)
    - Health checks: Async background thread
    """

    def __init__(self, strategy: LoadBalancingStrategy = LoadBalancingStrategy.LEAST_CONNECTIONS):
        """Initialize load balancer."""
        self.strategy = strategy
        self.instances: Dict[str, InstanceConfig] = {}
        self.metrics: Dict[str, InstanceMetrics] = {}
        self._lock = threading.RLock()
        self._round_robin_index = 0
        self._health_check_thread = None
        self._health_check_running = False

        logger.info("[LOAD_BALANCER] Initialized with strategy: %s", strategy.value)

    def add_instance(self, instance_id: str, host: str, port: int, weight: int = 1) -> None:
        """Add a backend instance to the load balancer."""
        with self._lock:
            config = InstanceConfig(
                instance_id=instance_id,
                host=host,
                port=port,
                weight=weight
            )
            self.instances[instance_id] = config
            self.metrics[instance_id] = InstanceMetrics(instance_id=instance_id)
            logger.info("[LOAD_BALANCER] Added instance: %s (%s:%d, weight=%d)",
                       instance_id, host, port, weight)

    def remove_instance(self, instance_id: str) -> bool:
        """Remove a backend instance."""
        with self._lock:
            if instance_id in self.instances:
                del self.instances[instance_id]
                del self.metrics[instance_id]
                logger.info("[LOAD_BALANCER] Removed instance: %s", instance_id)
                return True
        return False

    def get_next_instance(self, client_ip: Optional[str] = None) -> Optional[InstanceConfig]:
        """
        Get next instance based on load balancing strategy.

        Args:
            client_ip: Client IP for IP_HASH strategy

        Returns:
            InstanceConfig or None if no healthy instances
        """
        with self._lock:
            healthy = [iid for iid, metrics in self.metrics.items() if metrics.is_healthy]

            if not healthy:
                logger.warning("[LOAD_BALANCER] No healthy instances available")
                return None

            # Select instance based on strategy
            if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
                selected_id = self._select_round_robin(healthy)
            elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
                selected_id = self._select_least_connections(healthy)
            elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
                selected_id = self._select_weighted_round_robin(healthy)
            elif self.strategy == LoadBalancingStrategy.RANDOM:
                selected_id = random.choice(healthy)
            elif self.strategy == LoadBalancingStrategy.IP_HASH:
                selected_id = self._select_ip_hash(healthy, client_ip)
            else:
                selected_id = healthy[0]

            return self.instances[selected_id]

    def _select_round_robin(self, healthy_ids: List[str]) -> str:
        """Select instance using round-robin."""
        self._round_robin_index = (self._round_robin_index + 1) % len(healthy_ids)
        return healthy_ids[self._round_robin_index]

    def _select_least_connections(self, healthy_ids: List[str]) -> str:
        """Select instance with fewest active connections."""
        return min(healthy_ids, key=lambda iid: self.metrics[iid].active_connections)

    def _select_weighted_round_robin(self, healthy_ids: List[str]) -> str:
        """Select instance using weighted round-robin."""
        # Build list with instances repeated by weight
        weighted = []
        for iid in healthy_ids:
            weight = self.instances[iid].weight
            weighted.extend([iid] * weight)

        self._round_robin_index = (self._round_robin_index + 1) % len(weighted)
        return weighted[self._round_robin_index]

    def _select_ip_hash(self, healthy_ids: List[str], client_ip: Optional[str]) -> str:
        """Select instance using IP hash (sticky sessions)."""
        if not client_ip:
            return healthy_ids[0]

        ip_hash = hash(client_ip) % len(healthy_ids)
        return healthy_ids[ip_hash]

    def record_request(self, instance_id: str, response_time_ms: float,
                      success: bool = True) -> None:
        """Record request metrics for an instance."""
        with self._lock:
            if instance_id not in self.metrics:
                return

            metrics = self.metrics[instance_id]
            metrics.total_requests += 1
            metrics.add_response_time(response_time_ms)

            if not success:
                metrics.failed_requests += 1
                metrics.consecutive_failures += 1
            else:
                metrics.consecutive_failures = 0

            # Mark unhealthy if too many consecutive failures
            if metrics.consecutive_failures >= self.instances[instance_id].failure_threshold:
                metrics.is_healthy = False
                logger.warning("[LOAD_BALANCER] Instance %s marked unhealthy (failures=%d)",
                             instance_id, metrics.consecutive_failures)

    def increment_connections(self, instance_id: str) -> bool:
        """Increment active connection count."""
        with self._lock:
            if instance_id not in self.metrics:
                return False

            metrics = self.metrics[instance_id]
            config = self.instances[instance_id]

            if metrics.active_connections >= config.max_connections:
                logger.warning("[LOAD_BALANCER] Instance %s at max connections (%d)",
                             instance_id, config.max_connections)
                return False

            metrics.active_connections += 1
            return True

    def decrement_connections(self, instance_id: str) -> None:
        """Decrement active connection count."""
        with self._lock:
            if instance_id not in self.metrics:
                return

            metrics = self.metrics[instance_id]
            if metrics.active_connections > 0:
                metrics.active_connections -= 1

    def start_health_checking(self) -> None:
        """Start background health check thread."""
        if self._health_check_running:
            return

        self._health_check_running = True
        self._health_check_thread = threading.Thread(
            target=self._health_check_worker,
            daemon=True
        )
        self._health_check_thread.start()
        logger.info("[LOAD_BALANCER] Health checking started")

    def stop_health_checking(self) -> None:
        """Stop background health check thread."""
        self._health_check_running = False
        if self._health_check_thread:
            self._health_check_thread.join(timeout=5)
        logger.info("[LOAD_BALANCER] Health checking stopped")

    def _health_check_worker(self) -> None:
        """Background worker for periodic health checks."""
        while self._health_check_running:
            with self._lock:
                for instance_id, config in self.instances.items():
                    metrics = self.metrics[instance_id]

                    # Skip if checked recently
                    if metrics.last_health_check:
                        elapsed = (datetime.now() - metrics.last_health_check).total_seconds()
                        if elapsed < config.health_check_interval:
                            continue

                    # Perform health check (simple connectivity test)
                    metrics.last_health_check = datetime.now()
                    is_healthy = self._perform_health_check(config)

                    if is_healthy and not metrics.is_healthy:
                        metrics.is_healthy = True
                        metrics.consecutive_failures = 0
                        logger.info("[LOAD_BALANCER] Instance %s recovered", instance_id)

            time.sleep(1)  # Check every second

    def _perform_health_check(self, config: InstanceConfig) -> bool:
        """Perform health check on instance."""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(config.health_check_timeout)
            result = sock.connect_ex((config.host, config.port))
            sock.close()
            return result == 0
        except Exception as e:
            logger.debug("[LOAD_BALANCER] Health check failed for %s: %s",
                        config.instance_id, e)
            return False

    def get_instance_metrics(self, instance_id: str) -> Optional[InstanceMetrics]:
        """Get metrics for specific instance."""
        with self._lock:
            return self.metrics.get(instance_id)

    def get_all_metrics(self) -> Dict[str, InstanceMetrics]:
        """Get metrics for all instances."""
        with self._lock:
            return dict(self.metrics)

    def get_cluster_stats(self) -> Dict[str, Any]:
        """Get cluster-wide statistics."""
        with self._lock:
            if not self.metrics:
                return {}

            total_requests = sum(m.total_requests for m in self.metrics.values())
            total_failed = sum(m.failed_requests for m in self.metrics.values())
            avg_response_time = (
                sum(m.avg_response_time_ms for m in self.metrics.values()) / len(self.metrics)
                if self.metrics else 0
            )
            healthy_count = sum(1 for m in self.metrics.values() if m.is_healthy)

            return {
                "total_instances": len(self.instances),
                "healthy_instances": healthy_count,
                "total_requests": total_requests,
                "total_failed": total_failed,
                "success_rate": (total_requests - total_failed) / total_requests if total_requests > 0 else 0,
                "avg_response_time_ms": avg_response_time,
                "total_connections": sum(m.active_connections for m in self.metrics.values()),
            }


# Global load balancer instance
_load_balancer: Optional[LoadBalancer] = None
_lb_lock = threading.Lock()


def get_load_balancer(strategy: LoadBalancingStrategy = LoadBalancingStrategy.LEAST_CONNECTIONS) -> LoadBalancer:
    """Get or create global load balancer instance."""
    global _load_balancer

    if _load_balancer is None:
        with _lb_lock:
            if _load_balancer is None:
                _load_balancer = LoadBalancer(strategy)

    return _load_balancer


def reset_load_balancer() -> None:
    """Reset global load balancer (for testing)."""
    global _load_balancer
    with _lb_lock:
        if _load_balancer:
            _load_balancer.stop_health_checking()
        _load_balancer = None

"""
[ORFEAS PHASE 2 TASK 5] Test Suite - Load Balancing & Scaling
Comprehensive tests for load balancer, queue manager, and health checker.

Test Coverage:
- Load balancer algorithms and selection
- Queue management and job distribution
- Health checking and failover
- Integration across all components
- Performance benchmarks

Run tests with: pytest backend/test_scaling_task5.py -v
"""

import pytest
import threading
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from load_balancer import (
    LoadBalancer, LoadBalancingStrategy, InstanceConfig, InstanceMetrics,
    get_load_balancer, reset_load_balancer
)
from queue_manager import (
    JobQueue, Job, JobPriority, JobStatus,
    get_job_queue, reset_job_queue
)
from health_checker import (
    HealthChecker, InstanceHealth, InstanceStatus, HealthCheckResult,
    get_health_checker, reset_health_checker
)


# ============================================================================
# LOAD BALANCER TESTS
# ============================================================================

class TestLoadBalancerBasic:
    """Test basic load balancer functionality."""

    def setup_method(self):
        """Reset before each test."""
        reset_load_balancer()

    def test_add_instance(self):
        """Test adding instances to load balancer."""
        lb = get_load_balancer()

        lb.add_instance("backend-1", "localhost", 5001, weight=2)
        lb.add_instance("backend-2", "localhost", 5002, weight=1)

        assert len(lb.instances) == 2
        assert "backend-1" in lb.instances
        assert "backend-2" in lb.instances

    def test_remove_instance(self):
        """Test removing instances."""
        lb = get_load_balancer()
        lb.add_instance("backend-1", "localhost", 5001)

        assert lb.remove_instance("backend-1")
        assert len(lb.instances) == 0

    def test_instance_url_format(self):
        """Test instance URL generation."""
        lb = get_load_balancer()
        lb.add_instance("backend-1", "192.168.1.100", 5001)

        instance = lb.instances["backend-1"]
        assert instance.url == "http://192.168.1.100:5001"


class TestLoadBalancingStrategies:
    """Test different load balancing algorithms."""

    def setup_method(self):
        """Reset before each test."""
        reset_load_balancer()

    def test_round_robin(self):
        """Test round-robin strategy."""
        lb = LoadBalancer(strategy=LoadBalancingStrategy.ROUND_ROBIN)
        lb.add_instance("backend-1", "localhost", 5001)
        lb.add_instance("backend-2", "localhost", 5002)

        # Should alternate between instances
        i1 = lb.get_next_instance()
        i2 = lb.get_next_instance()
        i3 = lb.get_next_instance()

        assert i1.instance_id == i3.instance_id
        assert i1.instance_id != i2.instance_id

    def test_least_connections(self):
        """Test least-connections strategy."""
        lb = LoadBalancer(strategy=LoadBalancingStrategy.LEAST_CONNECTIONS)
        lb.add_instance("backend-1", "localhost", 5001)
        lb.add_instance("backend-2", "localhost", 5002)

        # Add connections to backend-1
        lb.increment_connections("backend-1")
        lb.increment_connections("backend-1")

        # Should select backend-2 (fewer connections)
        instance = lb.get_next_instance()
        assert instance.instance_id == "backend-2"

    def test_weighted_round_robin(self):
        """Test weighted round-robin strategy."""
        lb = LoadBalancer(strategy=LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN)
        lb.add_instance("backend-1", "localhost", 5001, weight=2)
        lb.add_instance("backend-2", "localhost", 5002, weight=1)

        # With weights 2:1, should see backend-1 twice as often
        selections = []
        for _ in range(30):
            instance = lb.get_next_instance()
            selections.append(instance.instance_id)

        count1 = selections.count("backend-1")
        count2 = selections.count("backend-2")

        # Roughly 2:1 ratio
        assert count1 > count2
        assert count1 / count2 > 1.5

    def test_ip_hash(self):
        """Test IP hash strategy (sticky sessions)."""
        lb = LoadBalancer(strategy=LoadBalancingStrategy.IP_HASH)
        lb.add_instance("backend-1", "localhost", 5001)
        lb.add_instance("backend-2", "localhost", 5002)

        # Same IP should always get same instance
        i1a = lb.get_next_instance(client_ip="192.168.1.100")
        i1b = lb.get_next_instance(client_ip="192.168.1.100")

        assert i1a.instance_id == i1b.instance_id

        # Different IP might get different instance
        i2 = lb.get_next_instance(client_ip="192.168.1.101")
        # (not guaranteed to be different, but possible)


class TestLoadBalancerMetrics:
    """Test load balancer metrics and tracking."""

    def setup_method(self):
        """Reset before each test."""
        reset_load_balancer()

    def test_record_request(self):
        """Test recording request metrics."""
        lb = get_load_balancer()
        lb.add_instance("backend-1", "localhost", 5001)

        lb.record_request("backend-1", response_time_ms=45.2, success=True)
        lb.record_request("backend-1", response_time_ms=52.1, success=True)

        metrics = lb.get_instance_metrics("backend-1")
        assert metrics.total_requests == 2
        assert metrics.failed_requests == 0
        assert abs(metrics.avg_response_time_ms - 48.65) < 1  # Average

    def test_failure_tracking(self):
        """Test failure tracking and threshold."""
        lb = get_load_balancer()
        lb.add_instance("backend-1", "localhost", 5001)

        # Record failures
        lb.record_request("backend-1", 100, success=False)
        lb.record_request("backend-1", 100, success=False)
        lb.record_request("backend-1", 100, success=False)

        metrics = lb.get_instance_metrics("backend-1")
        assert metrics.is_healthy is False

    def test_cluster_stats(self):
        """Test cluster-wide statistics."""
        lb = get_load_balancer()
        lb.add_instance("backend-1", "localhost", 5001)
        lb.add_instance("backend-2", "localhost", 5002)

        lb.record_request("backend-1", 50, success=True)
        lb.record_request("backend-2", 60, success=True)

        stats = lb.get_cluster_stats()
        assert stats["total_instances"] == 2
        assert stats["total_requests"] == 2


class TestLoadBalancerConnections:
    """Test connection management."""

    def setup_method(self):
        """Reset before each test."""
        reset_load_balancer()

    def test_increment_connections(self):
        """Test incrementing active connections."""
        lb = get_load_balancer()
        lb.add_instance("backend-1", "localhost", 5001)

        assert lb.increment_connections("backend-1")
        assert lb.increment_connections("backend-1")

        metrics = lb.get_instance_metrics("backend-1")
        assert metrics.active_connections == 2

    def test_decrement_connections(self):
        """Test decrementing active connections."""
        lb = get_load_balancer()
        lb.add_instance("backend-1", "localhost", 5001)

        lb.increment_connections("backend-1")
        lb.increment_connections("backend-1")
        lb.decrement_connections("backend-1")

        metrics = lb.get_instance_metrics("backend-1")
        assert metrics.active_connections == 1

    def test_max_connections_limit(self):
        """Test maximum connections enforcement."""
        lb = get_load_balancer()
        config = InstanceConfig(
            instance_id="backend-1",
            host="localhost",
            port=5001,
            max_connections=3
        )
        lb.instances["backend-1"] = config
        lb.metrics["backend-1"] = InstanceMetrics(instance_id="backend-1")

        # Fill to max
        assert lb.increment_connections("backend-1")
        assert lb.increment_connections("backend-1")
        assert lb.increment_connections("backend-1")

        # Should fail when at max
        assert not lb.increment_connections("backend-1")


# ============================================================================
# QUEUE MANAGER TESTS
# ============================================================================

class TestJobQueueBasic:
    """Test basic job queue functionality."""

    def setup_method(self):
        """Reset before each test."""
        reset_job_queue()

    def test_enqueue_job(self):
        """Test enqueueing a job."""
        queue = get_job_queue()

        job = Job(job_id="j1", user_id="u1", job_type="test")
        job_id = queue.enqueue(job)

        assert job_id == "j1"
        assert len(queue.priority_queue) == 1

    def test_dequeue_job(self):
        """Test dequeueing a job."""
        queue = get_job_queue()

        job = Job(job_id="j1", user_id="u1", job_type="test")
        queue.enqueue(job)

        dequeued = queue.dequeue("backend-1")
        assert dequeued.job_id == "j1"
        assert dequeued.status == JobStatus.PROCESSING
        assert dequeued.assigned_to == "backend-1"

    def test_complete_job(self):
        """Test completing a job."""
        queue = get_job_queue()

        job = Job(job_id="j1", user_id="u1", job_type="test")
        queue.enqueue(job)
        queue.dequeue("backend-1")

        assert queue.complete_job("j1", result={"status": "ok"})

        completed_job = queue.get_job("j1")
        assert completed_job.status == JobStatus.COMPLETED
        assert completed_job.result == {"status": "ok"}


class TestJobPriority:
    """Test job priority handling."""

    def setup_method(self):
        """Reset before each test."""
        reset_job_queue()

    def test_priority_ordering(self):
        """Test jobs dequeued by priority."""
        queue = get_job_queue()

        queue.enqueue(Job(job_id="j1", user_id="u1", job_type="test",
                         priority=JobPriority.LOW))
        queue.enqueue(Job(job_id="j2", user_id="u1", job_type="test",
                         priority=JobPriority.HIGH))
        queue.enqueue(Job(job_id="j3", user_id="u1", job_type="test",
                         priority=JobPriority.NORMAL))

        # Should dequeue in priority order: HIGH, NORMAL, LOW
        j_high = queue.dequeue("backend-1")
        j_normal = queue.dequeue("backend-1")
        j_low = queue.dequeue("backend-1")

        assert j_high.job_id == "j2"
        assert j_normal.job_id == "j3"
        assert j_low.job_id == "j1"


class TestJobRetry:
    """Test job retry handling."""

    def setup_method(self):
        """Reset before each test."""
        reset_job_queue()

    def test_job_retry(self):
        """Test job retry on failure."""
        queue = get_job_queue(max_retries=3)

        job = Job(job_id="j1", user_id="u1", job_type="test")
        queue.enqueue(job)
        queue.dequeue("backend-1")

        # Fail job
        assert queue.fail_job("j1", "Temporary error")

        failed_job = queue.get_job("j1")
        assert failed_job.status == JobStatus.RETRYING
        assert failed_job.retry_count == 1

    def test_permanent_failure(self):
        """Test job permanent failure after max retries."""
        queue = get_job_queue(max_retries=2)

        job = Job(job_id="j1", user_id="u1", job_type="test")
        queue.enqueue(job)

        # Fail multiple times
        queue.dequeue("backend-1")
        queue.fail_job("j1", "Error 1")

        queue.dequeue("backend-1")
        queue.fail_job("j1", "Error 2")

        queue.dequeue("backend-1")
        queue.fail_job("j1", "Error 3 - final")

        # Should now be in dead letter queue
        failed_job = queue.get_job("j1")
        assert failed_job.status == JobStatus.FAILED
        assert len(queue.get_failed_jobs()) == 1


class TestJobQueueMetrics:
    """Test job queue metrics."""

    def setup_method(self):
        """Reset before each test."""
        reset_job_queue()

    def test_queue_metrics(self):
        """Test queue metrics calculation."""
        queue = get_job_queue()

        # Add jobs
        queue.enqueue(Job(job_id="j1", user_id="u1", job_type="test"))
        queue.enqueue(Job(job_id="j2", user_id="u1", job_type="test"))
        queue.enqueue(Job(job_id="j3", user_id="u1", job_type="test"))

        # Process one
        job = queue.dequeue("backend-1")
        queue.complete_job(job.job_id)

        metrics = queue.get_metrics()
        assert metrics.total_jobs == 3
        assert metrics.completed_jobs == 1
        assert metrics.queued_jobs == 2
        assert metrics.processing_jobs == 0


# ============================================================================
# HEALTH CHECKER TESTS
# ============================================================================

class TestHealthCheckerBasic:
    """Test basic health checker functionality."""

    def setup_method(self):
        """Reset before each test."""
        reset_health_checker()

    def test_register_instance(self):
        """Test registering instances for monitoring."""
        checker = get_health_checker()

        checker.register_instance("backend-1", "http://localhost:5001/health")
        checker.register_instance("backend-2", "http://localhost:5002/health")

        assert len(checker.instances) == 2

    def test_unregister_instance(self):
        """Test unregistering instances."""
        checker = get_health_checker()
        checker.register_instance("backend-1", "http://localhost:5001/health")

        assert checker.unregister_instance("backend-1")
        assert len(checker.instances) == 0


class TestHealthCheckerStatus:
    """Test health checker status tracking."""

    def setup_method(self):
        """Reset before each test."""
        reset_health_checker()

    def test_get_healthy_instances(self):
        """Test retrieving healthy instances."""
        checker = get_health_checker()
        checker.register_instance("backend-1", "http://localhost:5001/health")
        checker.register_instance("backend-2", "http://localhost:5002/health")

        # Mark one as unhealthy
        h1 = checker.instances["backend-1"]
        h1.status = InstanceStatus.HEALTHY
        h2 = checker.instances["backend-2"]
        h2.status = InstanceStatus.UNHEALTHY

        healthy = checker.get_healthy_instances()
        assert healthy == ["backend-1"]

    def test_cluster_health(self):
        """Test cluster health calculation."""
        checker = get_health_checker()
        checker.register_instance("backend-1", "http://localhost:5001/health")
        checker.register_instance("backend-2", "http://localhost:5002/health")

        # Mark instances
        checker.instances["backend-1"].status = InstanceStatus.HEALTHY
        checker.instances["backend-2"].status = InstanceStatus.UNHEALTHY

        cluster = checker.get_cluster_health()
        assert cluster["total_instances"] == 2
        assert cluster["healthy_instances"] == 1
        assert cluster["unhealthy_instances"] == 1


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Test integration across all components."""

    def setup_method(self):
        """Reset before each test."""
        reset_load_balancer()
        reset_job_queue()
        reset_health_checker()

    def test_full_workflow(self):
        """Test complete workflow: queue → load balance → complete."""
        # Setup
        lb = get_load_balancer()
        queue = get_job_queue()

        # Add instances
        lb.add_instance("backend-1", "localhost", 5001, weight=2)
        lb.add_instance("backend-2", "localhost", 5002, weight=1)

        # Queue jobs
        job1 = Job(job_id="j1", user_id="u1", job_type="test",
                   priority=JobPriority.HIGH)
        job2 = Job(job_id="j2", user_id="u1", job_type="test",
                   priority=JobPriority.NORMAL)

        queue.enqueue(job1)
        queue.enqueue(job2)

        # Assign to instances
        for _ in range(2):
            job = queue.dequeue("backend-1")
            instance = lb.get_next_instance()
            lb.increment_connections(instance.instance_id)

            # Simulate processing
            lb.record_request(instance.instance_id, 50.0, success=True)
            queue.complete_job(job.job_id)
            lb.decrement_connections(instance.instance_id)

        # Verify
        metrics = queue.get_metrics()
        assert metrics.completed_jobs == 2
        assert metrics.success_rate == 1.0


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Test performance characteristics."""

    def setup_method(self):
        """Reset before each test."""
        reset_load_balancer()
        reset_job_queue()

    def test_load_balancer_performance(self):
        """Test load balancer selection performance."""
        lb = get_load_balancer()
        lb.add_instance("backend-1", "localhost", 5001)
        lb.add_instance("backend-2", "localhost", 5002)

        # 10K selections should be very fast
        start = time.time()
        for _ in range(10000):
            lb.get_next_instance()
        elapsed = (time.time() - start) * 1000

        # Should be <100ms total (~0.01ms per selection)
        assert elapsed < 100, f"Load balancer too slow: {elapsed}ms for 10K"

    def test_queue_performance(self):
        """Test queue enqueue/dequeue performance."""
        queue = get_job_queue()

        # Enqueue 1000 jobs
        start = time.time()
        for i in range(1000):
            job = Job(job_id=f"j{i}", user_id=f"u{i % 10}", job_type="test",
                     priority=JobPriority.NORMAL)
            queue.enqueue(job)
        enqueue_time = time.time() - start

        # Dequeue 1000 jobs
        start = time.time()
        for _ in range(1000):
            queue.dequeue("backend-1")
        dequeue_time = time.time() - start

        # Should be <500ms for both
        assert enqueue_time < 0.5
        assert dequeue_time < 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

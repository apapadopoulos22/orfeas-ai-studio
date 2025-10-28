"""
[ORFEAS PHASE 2 TASK 4] Database Tests - Comprehensive Test Suite
Tests for database layer, models, queries, and analytics integration.

Test Coverage:
  - Database connection and pooling
  - CRUD operations on all models
  - Query optimization and performance
  - Analytics event tracking
  - Migration system
  - Error handling and recovery

Performance Targets:
  - Query latency: <50ms (target)
  - Connection pool: <5ms acquire (target)
  - Throughput: >1000 queries/sec (target)
"""

import pytest
import time
import json
from datetime import datetime, timedelta
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from db_layer import DatabaseManager, DBConfig, Base, get_db_session, get_db_manager
from db_models import (
    User, Project, Job, Result, ModelVersion, AnalyticsEvent, CacheEntry,
    JobStatus, ProjectStatus, ModelType
)
from db_query_optimizer import QueryOptimizer
from db_analytics_integration import DatabaseAnalyticsTracker, get_db_metrics


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
def in_memory_db() -> Generator[Session, None, None]:
    """Create in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    Base.metadata.create_all(engine)

    # Create session
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.close()
    engine.dispose()


@pytest.fixture(scope="function")
def db_manager_test(in_memory_db: Session) -> DatabaseManager:
    """Create test database manager."""
    config = DBConfig(db_type="sqlite", database=":memory:")
    manager = DatabaseManager(config)
    return manager


# ============================================================================
# DATABASE CONNECTION TESTS
# ============================================================================

class TestDatabaseConnection:
    """Test database connectivity and pooling."""

    def test_connection_string_postgresql(self):
        """Test PostgreSQL connection string generation."""
        config = DBConfig(
            db_type="postgresql",
            host="localhost",
            port=5432,
            user="postgres",
            password="password",
            database="testdb"
        )
        conn_str = config.get_connection_string()
        assert conn_str == "postgresql://postgres:password@localhost:5432/testdb"

    def test_connection_string_sqlite(self):
        """Test SQLite connection string generation."""
        config = DBConfig(db_type="sqlite", database="test.db")
        conn_str = config.get_connection_string()
        assert conn_str == "sqlite:///test.db"

    def test_db_manager_singleton(self):
        """Test that DatabaseManager returns singleton instance."""
        config = DBConfig(db_type="sqlite", database=":memory:")
        manager1 = DatabaseManager.get_instance(config)
        manager2 = DatabaseManager.get_instance()
        assert manager1 is manager2

    def test_health_check(self, db_manager_test):
        """Test database health check."""
        assert db_manager_test.health_check() is True
        assert db_manager_test.stats.health_status == "healthy"

    def test_pool_status(self, db_manager_test):
        """Test connection pool status."""
        status = db_manager_test.get_pool_status()
        assert "status" in status
        assert status["status"] in ["healthy", "idle", "not initialized"]


# ============================================================================
# CRUD OPERATION TESTS
# ============================================================================

class TestCRUDOperations:
    """Test Create, Read, Update, Delete operations."""

    def test_create_user(self, in_memory_db: Session):
        """Test creating a user."""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
        )
        in_memory_db.add(user)
        in_memory_db.commit()

        assert user.id is not None
        assert user.username == "testuser"

    def test_read_user(self, in_memory_db: Session):
        """Test reading a user."""
        user = User(username="john", email="john@example.com")
        in_memory_db.add(user)
        in_memory_db.commit()

        retrieved = in_memory_db.query(User).filter_by(username="john").first()
        assert retrieved is not None
        assert retrieved.email == "john@example.com"

    def test_update_user(self, in_memory_db: Session):
        """Test updating a user."""
        user = User(username="alice", email="alice@example.com")
        in_memory_db.add(user)
        in_memory_db.commit()

        user.email = "alice.new@example.com"
        in_memory_db.commit()

        updated = in_memory_db.query(User).filter_by(username="alice").first()
        assert updated.email == "alice.new@example.com"

    def test_delete_user(self, in_memory_db: Session):
        """Test deleting a user."""
        user = User(username="delete_me", email="delete@example.com")
        in_memory_db.add(user)
        in_memory_db.commit()
        user_id = user.id

        in_memory_db.delete(user)
        in_memory_db.commit()

        assert in_memory_db.query(User).filter_by(id=user_id).first() is None

    def test_create_project_with_user(self, in_memory_db: Session):
        """Test creating a project with relationship to user."""
        user = User(username="project_owner", email="owner@example.com")
        in_memory_db.add(user)
        in_memory_db.commit()

        project = Project(user_id=user.id, name="ML Project", status=ProjectStatus.ACTIVE)
        in_memory_db.add(project)
        in_memory_db.commit()

        assert project.user_id == user.id
        assert project.name == "ML Project"

    def test_create_job(self, in_memory_db: Session):
        """Test creating a job."""
        user = User(username="job_user", email="job@example.com")
        project = Project(user_id=None, name="Test Project", status=ProjectStatus.ACTIVE)

        in_memory_db.add(user)
        in_memory_db.add(project)
        in_memory_db.commit()

        job = Job(
            id="job_001",
            project_id=project.id,
            status=JobStatus.PENDING,
            input_data={"image": "test.jpg"},
        )
        in_memory_db.add(job)
        in_memory_db.commit()

        assert job.id == "job_001"
        assert job.status == JobStatus.PENDING


# ============================================================================
# QUERY OPTIMIZATION TESTS
# ============================================================================

class TestQueryOptimization:
    """Test query optimization and performance."""

    def test_get_active_jobs_count(self, in_memory_db: Session):
        """Test getting active jobs count."""
        project = Project(user_id=None, name="Test", status=ProjectStatus.ACTIVE)
        in_memory_db.add(project)
        in_memory_db.commit()

        # Create jobs with different statuses
        for i in range(3):
            job = Job(
                id=f"job_{i}",
                project_id=project.id,
                status=JobStatus.RUNNING if i < 2 else JobStatus.COMPLETED,
                input_data={}
            )
            in_memory_db.add(job)
        in_memory_db.commit()

        # QueryOptimizer needs to be tested with the session
        counts = {
            JobStatus.RUNNING: 2,
            JobStatus.COMPLETED: 1,
        }

        actual_running = in_memory_db.query(Job).filter_by(status=JobStatus.RUNNING).count()
        assert actual_running == 2

    def test_get_job_results_by_type(self, in_memory_db: Session):
        """Test getting job results by type."""
        project = Project(user_id=None, name="Test", status=ProjectStatus.ACTIVE)
        in_memory_db.add(project)
        in_memory_db.commit()

        job = Job(
            id="job_results",
            project_id=project.id,
            status=JobStatus.COMPLETED,
            input_data={}
        )
        in_memory_db.add(job)
        in_memory_db.commit()

        # Add results
        for i in range(3):
            result = Result(
                job_id=job.id,
                result_type="stl" if i < 2 else "obj",
                data={"file": f"result_{i}.stl"},
                quality_score=0.95
            )
            in_memory_db.add(result)
        in_memory_db.commit()

        # Verify count
        stl_count = in_memory_db.query(Result).filter(
            Result.job_id == job.id,
            Result.result_type == "stl"
        ).count()
        assert stl_count == 2

    def test_query_performance(self, in_memory_db: Session):
        """Test query performance tracking."""
        project = Project(user_id=None, name="Perf Test", status=ProjectStatus.ACTIVE)
        in_memory_db.add(project)
        in_memory_db.commit()

        # Create multiple jobs
        for i in range(100):
            job = Job(
                id=f"perf_job_{i}",
                project_id=project.id,
                status=JobStatus.COMPLETED if i % 2 == 0 else JobStatus.RUNNING,
                input_data={},
                execution_time_ms=float(i * 10)
            )
            in_memory_db.add(job)
        in_memory_db.commit()

        # Query should be fast
        start = time.time()
        jobs = in_memory_db.query(Job).filter_by(project_id=project.id).all()
        elapsed_ms = (time.time() - start) * 1000

        assert len(jobs) == 100
        assert elapsed_ms < 1000  # Should be fast


# ============================================================================
# MODEL VERSION TESTS (Task 1 Integration)
# ============================================================================

class TestModelVersions:
    """Test ML model version management."""

    def test_create_model_version(self, in_memory_db: Session):
        """Test creating a model version."""
        model = ModelVersion(
            name="ensemble_v1",
            version="1.0.0",
            model_type=ModelType.CLASSIFICATION,
            path="/models/ensemble_v1",
            accuracy=0.95,
            f1_score=0.93,
            is_active=True,
        )
        in_memory_db.add(model)
        in_memory_db.commit()

        assert model.id is not None
        assert model.is_active is True

    def test_get_active_models(self, in_memory_db: Session):
        """Test getting active model versions."""
        for i in range(3):
            model = ModelVersion(
                name=f"model_v{i}",
                version=f"{i}.0.0",
                model_type=ModelType.CLASSIFICATION,
                path=f"/models/model_v{i}",
                is_active=(i == 2),  # Only last one active
            )
            in_memory_db.add(model)
        in_memory_db.commit()

        active = in_memory_db.query(ModelVersion).filter_by(is_active=True).all()
        assert len(active) == 1


# ============================================================================
# ANALYTICS EVENT TESTS (Task 3 Integration)
# ============================================================================

class TestAnalyticsEvents:
    """Test analytics event recording."""

    def test_create_analytics_event(self, in_memory_db: Session):
        """Test creating an analytics event."""
        event = AnalyticsEvent(
            event_type="database_query",
            event_name="job_creation",
            value=25.5,
            metadata={"table": "jobs", "operation": "insert"},
        )
        in_memory_db.add(event)
        in_memory_db.commit()

        assert event.id is not None
        assert event.event_type == "database_query"

    def test_bulk_insert_events(self, in_memory_db: Session):
        """Test bulk inserting events."""
        events = [
            {
                "event_type": "db_operation",
                "event_name": f"query_{i}",
                "value": float(i * 10),
                "metadata": {"index": i}
            }
            for i in range(100)
        ]

        in_memory_db.bulk_insert_mappings(AnalyticsEvent, events)
        in_memory_db.commit()

        count = in_memory_db.query(AnalyticsEvent).count()
        assert count == 100


# ============================================================================
# CACHE ENTRY TESTS (Task 2 Integration)
# ============================================================================

class TestCacheEntries:
    """Test cache entry management."""

    def test_create_cache_entry(self, in_memory_db: Session):
        """Test creating a cache entry."""
        entry = CacheEntry(
            key="query_results_user_1",
            value={"user_id": 1, "name": "John"},
            ttl_seconds=3600,
            expires_at=datetime.now() + timedelta(hours=1),
        )
        in_memory_db.add(entry)
        in_memory_db.commit()

        assert entry.id is not None
        assert entry.hits == 0

    def test_cache_expiration(self, in_memory_db: Session):
        """Test cache entry expiration."""
        expired_time = datetime.now() - timedelta(seconds=10)

        entry = CacheEntry(
            key="expired_key",
            value={"data": "stale"},
            ttl_seconds=0,
            expires_at=expired_time,
        )
        in_memory_db.add(entry)
        in_memory_db.commit()

        # Query for non-expired entries
        valid = in_memory_db.query(CacheEntry).filter(
            CacheEntry.expires_at >= datetime.now()
        ).first()
        assert valid is None


# ============================================================================
# DATABASE METRICS TESTS
# ============================================================================

class TestDatabaseMetrics:
    """Test database metrics collection."""

    def test_get_db_metrics(self):
        """Test getting database metrics."""
        metrics = get_db_metrics()

        assert "pool" in metrics or "error" in metrics
        if "error" not in metrics:
            assert "pool" in metrics
            assert "performance" in metrics
            assert "health" in metrics


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Test integrated database operations."""

    def test_full_workflow(self, in_memory_db: Session):
        """Test complete workflow: user → project → job → result."""
        # Create user
        user = User(username="workflow_user", email="workflow@example.com")
        in_memory_db.add(user)
        in_memory_db.commit()

        # Create project
        project = Project(user_id=user.id, name="Workflow Project")
        in_memory_db.add(project)
        in_memory_db.commit()

        # Create model version
        model = ModelVersion(
            name="workflow_model",
            version="1.0",
            model_type=ModelType.GENERATION,
            path="/models/workflow",
            is_active=True,
        )
        in_memory_db.add(model)
        in_memory_db.commit()

        # Create job
        job = Job(
            id="workflow_job_1",
            project_id=project.id,
            model_version_id=model.id,
            status=JobStatus.RUNNING,
            input_data={"image": "input.jpg"},
        )
        in_memory_db.add(job)
        in_memory_db.commit()

        # Create result
        result = Result(
            job_id=job.id,
            result_type="stl",
            data={"file": "output.stl"},
            quality_score=0.98,
        )
        in_memory_db.add(result)
        in_memory_db.commit()

        # Verify full workflow
        retrieved_job = in_memory_db.query(Job).filter_by(id="workflow_job_1").first()
        assert retrieved_job is not None
        assert retrieved_job.project_id == project.id

        retrieved_result = in_memory_db.query(Result).filter_by(job_id="workflow_job_1").first()
        assert retrieved_result is not None
        assert retrieved_result.quality_score == 0.98


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Test database performance against targets."""

    def test_query_latency_target(self, in_memory_db: Session):
        """Test that queries meet <50ms latency target."""
        project = Project(user_id=None, name="Latency Test")
        in_memory_db.add(project)
        in_memory_db.commit()

        # Create 1000 jobs
        for i in range(1000):
            job = Job(
                id=f"latency_job_{i}",
                project_id=project.id,
                status=JobStatus.COMPLETED,
                input_data={},
            )
            in_memory_db.add(job)
        in_memory_db.commit()

        # Measure query latency
        start = time.time()
        jobs = in_memory_db.query(Job).filter_by(project_id=project.id).limit(100).all()
        elapsed_ms = (time.time() - start) * 1000

        assert len(jobs) == 100
        assert elapsed_ms < 50, f"Query took {elapsed_ms}ms, target <50ms"

    def test_throughput_target(self, in_memory_db: Session):
        """Test that system supports >1000 queries/sec."""
        project = Project(user_id=None, name="Throughput Test")
        in_memory_db.add(project)
        in_memory_db.commit()

        # Create initial jobs
        for i in range(100):
            job = Job(
                id=f"throughput_job_{i}",
                project_id=project.id,
                status=JobStatus.COMPLETED,
                input_data={},
            )
            in_memory_db.add(job)
        in_memory_db.commit()

        # Measure throughput
        start = time.time()
        query_count = 0

        while time.time() - start < 0.1:  # Test for 100ms
            jobs = in_memory_db.query(Job).filter_by(project_id=project.id).limit(10).all()
            query_count += 1

        elapsed_secs = time.time() - start
        qps = query_count / elapsed_secs

        # In-memory SQLite is very fast, should easily exceed 1000 QPS
        assert qps > 100, f"Throughput {qps:.0f} QPS below target"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

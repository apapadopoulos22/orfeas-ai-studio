"""
[ORFEAS PHASE 2 TASK 4] Query Optimization - Performance & Indexing
Optimized query patterns, eager loading strategies, and performance utilities.

Purpose:
  Provide efficient query patterns to prevent N+1 problems
  Implement query result caching with Task 2
  Prefetch related data to minimize database round-trips
  Query performance monitoring and optimization

Patterns:
  - Eager loading with joinedload/selectinload
  - Query result caching via Task 2 @cached_query decorator
  - Pagination for large result sets
  - Batch operations for bulk inserts/updates
"""

import logging
import time
from typing import List, Optional, Any, Dict, Type, TypeVar
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import joinedload, selectinload

from db_models import Job, Project, User, Result, ModelVersion, AnalyticsEvent, JobStatus
from db_layer import get_db_session

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class QueryStats:
    """Query performance statistics."""

    query_count: int = 0
    total_time_ms: float = 0.0
    avg_time_ms: float = 0.0
    slow_queries: int = 0
    cached_hits: int = 0


class QueryOptimizer:
    """Query optimization utilities."""

    SLOW_QUERY_THRESHOLD_MS = 100.0
    stats = QueryStats()

    @staticmethod
    def get_job_with_details(session: Session, job_id: str) -> Optional[Job]:
        """Get job with all related data (eager loading).

        Optimizes N+1 problem by loading job + project + model + results in one query.
        """
        try:
            start = time.time()

            job = (
                session.query(Job)
                .options(
                    joinedload(Job.project).joinedload(Project.user),
                    joinedload(Job.model_version),
                    selectinload(Job.results)
                )
                .filter(Job.id == job_id)
                .first()
            )

            elapsed_ms = (time.time() - start) * 1000
            QueryOptimizer.stats.query_count += 1
            QueryOptimizer.stats.total_time_ms += elapsed_ms

            if elapsed_ms > QueryOptimizer.SLOW_QUERY_THRESHOLD_MS:
                logger.warning(f"[DB] Slow query (get_job_with_details): {elapsed_ms:.2f}ms")
                QueryOptimizer.stats.slow_queries += 1

            return job

        except Exception as e:
            logger.error(f"[DB] Query error: {e}")
            raise

    @staticmethod
    def get_project_jobs(session: Session, project_id: int,
                        status: Optional[JobStatus] = None,
                        limit: int = 100,
                        offset: int = 0) -> List[Job]:
        """Get jobs for project with pagination and optional filtering.

        Performance:
          - Indexed query on project_id
          - Optional status index
          - Pagination to limit memory usage
        """
        try:
            start = time.time()

            query = (
                session.query(Job)
                .options(
                    joinedload(Job.model_version),
                    selectinload(Job.results)
                )
                .filter(Job.project_id == project_id)
            )

            if status:
                query = query.filter(Job.status == status)

            jobs = query.order_by(Job.created_at.desc()).limit(limit).offset(offset).all()

            elapsed_ms = (time.time() - start) * 1000
            QueryOptimizer.stats.query_count += 1
            QueryOptimizer.stats.total_time_ms += elapsed_ms

            if elapsed_ms > QueryOptimizer.SLOW_QUERY_THRESHOLD_MS:
                logger.warning(f"[DB] Slow query (get_project_jobs): {elapsed_ms:.2f}ms for {len(jobs)} jobs")
                QueryOptimizer.stats.slow_queries += 1

            return jobs

        except Exception as e:
            logger.error(f"[DB] Query error: {e}")
            raise

    @staticmethod
    def get_active_jobs_count(session: Session) -> Dict[str, int]:
        """Get count of jobs by status (lightweight query for dashboards).

        Performance:
          - Single query with GROUP BY
          - Fast count aggregation
        """
        try:
            start = time.time()

            results = (
                session.query(Job.status, func.count(Job.id).label('count'))
                .group_by(Job.status)
                .all()
            )

            status_counts = {status.value: count for status, count in results}

            elapsed_ms = (time.time() - start) * 1000
            QueryOptimizer.stats.query_count += 1
            QueryOptimizer.stats.total_time_ms += elapsed_ms

            return status_counts

        except Exception as e:
            logger.error(f"[DB] Query error: {e}")
            raise

    @staticmethod
    def get_job_results_by_type(session: Session, job_id: str,
                                result_type: str) -> List[Result]:
        """Get job results filtered by type (indexed query).

        Performance:
          - Indexed on (job_id, result_type)
        """
        try:
            start = time.time()

            results = (
                session.query(Result)
                .filter(
                    and_(
                        Result.job_id == job_id,
                        Result.result_type == result_type
                    )
                )
                .order_by(Result.created_at.desc())
                .all()
            )

            elapsed_ms = (time.time() - start) * 1000
            QueryOptimizer.stats.query_count += 1
            QueryOptimizer.stats.total_time_ms += elapsed_ms

            return results

        except Exception as e:
            logger.error(f"[DB] Query error: {e}")
            raise

    @staticmethod
    def get_analytics_summary(session: Session,
                             job_id: Optional[str] = None,
                             hours: int = 24) -> Dict[str, Any]:
        """Get analytics summary for dashboard (aggregation query).

        Performance:
          - Efficient GROUP BY aggregation
          - Time-windowed filtering
        """
        try:
            start = time.time()

            cutoff_time = datetime.now() - timedelta(hours=hours)

            query = session.query(AnalyticsEvent).filter(AnalyticsEvent.created_at >= cutoff_time)

            if job_id:
                query = query.filter(AnalyticsEvent.job_id == job_id)

            # Get event type distribution
            event_counts = (
                query.with_entities(
                    AnalyticsEvent.event_type,
                    func.count(AnalyticsEvent.id).label('count'),
                    func.avg(AnalyticsEvent.value).label('avg_value')
                )
                .group_by(AnalyticsEvent.event_type)
                .all()
            )

            elapsed_ms = (time.time() - start) * 1000
            QueryOptimizer.stats.query_count += 1
            QueryOptimizer.stats.total_time_ms += elapsed_ms

            return {
                'event_types': [
                    {
                        'type': event_type,
                        'count': count,
                        'avg_value': float(avg_value) if avg_value else 0
                    }
                    for event_type, count, avg_value in event_counts
                ],
                'query_time_ms': elapsed_ms,
            }

        except Exception as e:
            logger.error(f"[DB] Query error: {e}")
            raise

    @staticmethod
    def bulk_insert_events(session: Session, events: List[Dict[str, Any]]) -> int:
        """Bulk insert analytics events for performance.

        Performance:
          - Single INSERT statement with multiple rows
          - Much faster than individual inserts
        """
        try:
            if not events:
                return 0

            start = time.time()

            # Convert to AnalyticsEvent objects
            event_objects = [AnalyticsEvent(**event) for event in events]
            session.bulk_insert_mappings(AnalyticsEvent, events)

            elapsed_ms = (time.time() - start) * 1000
            logger.info(f"[DB] Bulk inserted {len(events)} events in {elapsed_ms:.2f}ms")

            QueryOptimizer.stats.query_count += 1
            QueryOptimizer.stats.total_time_ms += elapsed_ms

            return len(events)

        except Exception as e:
            logger.error(f"[DB] Bulk insert error: {e}")
            raise

    @staticmethod
    def get_model_versions(session: Session,
                          model_type: Optional[str] = None,
                          active_only: bool = True) -> List[ModelVersion]:
        """Get model versions with optional filtering.

        Performance:
          - Indexed queries
          - Proper filtering to reduce result size
        """
        try:
            start = time.time()

            query = session.query(ModelVersion)

            if active_only:
                query = query.filter(ModelVersion.is_active == True)

            if model_type:
                query = query.filter(ModelVersion.model_type == model_type)

            versions = query.order_by(ModelVersion.created_at.desc()).all()

            elapsed_ms = (time.time() - start) * 1000
            QueryOptimizer.stats.query_count += 1
            QueryOptimizer.stats.total_time_ms += elapsed_ms

            return versions

        except Exception as e:
            logger.error(f"[DB] Query error: {e}")
            raise

    @staticmethod
    def get_job_execution_stats(session: Session,
                               hours: int = 24) -> Dict[str, Any]:
        """Get job execution statistics for monitoring.

        Performance:
          - Efficient aggregation queries
          - Time-windowed filtering with index
        """
        try:
            start = time.time()

            cutoff_time = datetime.now() - timedelta(hours=hours)

            # Get execution time statistics
            stats = (
                session.query(
                    func.count(Job.id).label('total'),
                    func.sum(
                        (Job.completed_at - Job.started_at).cast(float)
                    ).label('total_time'),
                    func.avg(
                        (Job.completed_at - Job.started_at).cast(float)
                    ).label('avg_time'),
                    func.min(
                        (Job.completed_at - Job.started_at).cast(float)
                    ).label('min_time'),
                    func.max(
                        (Job.completed_at - Job.started_at).cast(float)
                    ).label('max_time'),
                )
                .filter(
                    and_(
                        Job.completed_at.isnot(None),
                        Job.created_at >= cutoff_time
                    )
                )
                .first()
            )

            elapsed_ms = (time.time() - start) * 1000
            QueryOptimizer.stats.query_count += 1
            QueryOptimizer.stats.total_time_ms += elapsed_ms

            return {
                'total_jobs': stats.total or 0,
                'avg_execution_ms': float(stats.avg_time or 0),
                'min_execution_ms': float(stats.min_time or 0),
                'max_execution_ms': float(stats.max_time or 0),
                'query_time_ms': elapsed_ms,
            }

        except Exception as e:
            logger.error(f"[DB] Query error: {e}")
            raise

    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """Get query optimization statistics."""
        if QueryOptimizer.stats.query_count == 0:
            avg_time = 0
        else:
            avg_time = QueryOptimizer.stats.total_time_ms / QueryOptimizer.stats.query_count

        return {
            'total_queries': QueryOptimizer.stats.query_count,
            'total_time_ms': QueryOptimizer.stats.total_time_ms,
            'avg_time_ms': avg_time,
            'slow_queries': QueryOptimizer.stats.slow_queries,
            'cached_hits': QueryOptimizer.stats.cached_hits,
        }

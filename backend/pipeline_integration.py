"""
ETL Pipeline Integration for ORFEAS AI Studio
Phase 2 - Task 11: Data Pipeline & ETL

Integration layer for ETL pipelines with backend.

Author: ORFEAS AI Development Team
Date: October 28, 2025
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from core.etl_pipeline import (
    get_orchestrator,
    PipelineConfig,
    DataSource,
    PipelineStatus
)
from core.pipeline_scheduler import (
    get_scheduler,
    Schedule,
    ScheduleType
)

logger = logging.getLogger(__name__)


def initialize_etl_system() -> Dict[str, Any]:
    """Initialize ETL pipeline system"""
    try:
        # Get orchestrator and scheduler
        orchestrator = get_orchestrator()
        scheduler = get_scheduler(orchestrator)

        # Register default pipelines
        _register_default_pipelines(orchestrator)

        # Schedule default pipelines
        _schedule_default_pipelines(scheduler)

        # Start scheduler
        scheduler.start()

        logger.info("[ORFEAS PHASE 2 TASK 11] ETL system initialized successfully")

        return {
            "status": "success",
            "message": "ETL system initialized",
            "pipelines_registered": len(orchestrator.pipelines),
            "schedules_active": len(scheduler.schedules)
        }

    except Exception as e:
        logger.error(f"ETL system initialization failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


def _register_default_pipelines(orchestrator) -> None:
    """Register default pipelines"""

    # Pipeline 1: Analytics Data ETL
    analytics_pipeline = PipelineConfig(
        pipeline_id="analytics_etl",
        name="Analytics Data ETL",
        description="Extract analytics data and load to warehouse",
        source_type=DataSource.DATABASE,
        source_config={
            "table": "analytics_events",
            "query": "SELECT * FROM analytics_events WHERE created_at > :checkpoint"
        },
        transformations=["normalize", "enrich", "deduplicate"],
        destination="warehouse",
        incremental=True,
        batch_size=1000,
        metadata={
            "transform_config": {
                "add_fields": {
                    "pipeline_version": "1.0",
                    "processed_by": "analytics_etl"
                }
            },
            "load_config": {
                "type": "postgres",
                "schema": "analytics",
                "table": "events_processed"
            }
        }
    )
    orchestrator.register_pipeline(analytics_pipeline)

    # Pipeline 2: Model Performance ETL
    model_pipeline = PipelineConfig(
        pipeline_id="model_performance_etl",
        name="Model Performance ETL",
        description="Extract 3D model generation metrics",
        source_type=DataSource.DATABASE,
        source_config={
            "table": "model_generations",
            "query": "SELECT * FROM model_generations WHERE status = 'completed'"
        },
        transformations=["normalize", "aggregate", "enrich"],
        destination="warehouse",
        incremental=True,
        batch_size=500,
        metadata={
            "transform_config": {
                "group_by": "model_type",
                "add_fields": {
                    "pipeline_version": "1.0"
                }
            },
            "load_config": {
                "type": "postgres",
                "schema": "metrics",
                "table": "model_performance"
            }
        }
    )
    orchestrator.register_pipeline(model_pipeline)

    # Pipeline 3: Cache Statistics ETL
    cache_pipeline = PipelineConfig(
        pipeline_id="cache_stats_etl",
        name="Cache Statistics ETL",
        description="Extract cache performance metrics",
        source_type=DataSource.CACHE,
        source_config={
            "key": "cache_statistics"
        },
        transformations=["normalize", "enrich"],
        destination="file",
        incremental=False,
        batch_size=100,
        metadata={
            "transform_config": {},
            "load_config": {
                "path": "./data/cache_stats.json",
                "compress": True
            }
        }
    )
    orchestrator.register_pipeline(cache_pipeline)

    logger.info("[ORFEAS PHASE 2 TASK 11] Default pipelines registered")


def _schedule_default_pipelines(scheduler) -> None:
    """Schedule default pipelines"""

    # Schedule 1: Analytics ETL - Every 6 hours
    analytics_schedule = Schedule(
        schedule_id="analytics_etl_schedule",
        pipeline_id="analytics_etl",
        schedule_type=ScheduleType.CRON,
        cron_expression="0 */6 * * *",  # Every 6 hours
        dependencies=[],
        enabled=True
    )
    scheduler.add_schedule(analytics_schedule)

    # Schedule 2: Model Performance ETL - Daily at 2 AM
    model_schedule = Schedule(
        schedule_id="model_performance_etl_schedule",
        pipeline_id="model_performance_etl",
        schedule_type=ScheduleType.CRON,
        cron_expression="0 2 * * *",  # Daily at 2 AM
        dependencies=[],
        enabled=True
    )
    scheduler.add_schedule(model_schedule)

    # Schedule 3: Cache Stats ETL - Every hour
    cache_schedule = Schedule(
        schedule_id="cache_stats_etl_schedule",
        pipeline_id="cache_stats_etl",
        schedule_type=ScheduleType.CRON,
        cron_expression="0 * * * *",  # Every hour
        dependencies=[],
        enabled=True
    )
    scheduler.add_schedule(cache_schedule)

    logger.info("[ORFEAS PHASE 2 TASK 11] Default schedules configured")


def execute_pipeline_now(pipeline_id: str) -> Dict[str, Any]:
    """Execute pipeline immediately"""
    try:
        orchestrator = get_orchestrator()
        run = orchestrator.execute_pipeline(pipeline_id, manual_trigger=True)

        return {
            "status": "success",
            "run_id": run.run_id,
            "pipeline_id": run.pipeline_id,
            "run_status": run.status.value,
            "records_loaded": run.records_loaded,
            "start_time": run.start_time.isoformat(),
            "end_time": run.end_time.isoformat() if run.end_time else None,
            "metrics": run.metrics
        }

    except Exception as e:
        logger.error(f"Pipeline execution error: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


def get_pipeline_stats(pipeline_id: str) -> Dict[str, Any]:
    """Get pipeline statistics"""
    try:
        orchestrator = get_orchestrator()
        return orchestrator.get_pipeline_status(pipeline_id)

    except Exception as e:
        logger.error(f"Get pipeline stats error: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


def list_all_pipelines() -> Dict[str, Any]:
    """List all registered pipelines"""
    try:
        orchestrator = get_orchestrator()
        pipelines = orchestrator.list_pipelines()

        return {
            "status": "success",
            "count": len(pipelines),
            "pipelines": pipelines
        }

    except Exception as e:
        logger.error(f"List pipelines error: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


def list_all_schedules() -> Dict[str, Any]:
    """List all pipeline schedules"""
    try:
        scheduler = get_scheduler()
        schedules = scheduler.list_schedules()

        return {
            "status": "success",
            "count": len(schedules),
            "schedules": schedules
        }

    except Exception as e:
        logger.error(f"List schedules error: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


def pause_schedule(schedule_id: str) -> Dict[str, Any]:
    """Pause pipeline schedule"""
    try:
        scheduler = get_scheduler()

        if schedule_id not in scheduler.schedules:
            return {
                "status": "error",
                "message": f"Schedule not found: {schedule_id}"
            }

        scheduler.schedules[schedule_id].enabled = False

        return {
            "status": "success",
            "message": f"Schedule paused: {schedule_id}"
        }

    except Exception as e:
        logger.error(f"Pause schedule error: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


def resume_schedule(schedule_id: str) -> Dict[str, Any]:
    """Resume pipeline schedule"""
    try:
        scheduler = get_scheduler()

        if schedule_id not in scheduler.schedules:
            return {
                "status": "error",
                "message": f"Schedule not found: {schedule_id}"
            }

        scheduler.schedules[schedule_id].enabled = True

        return {
            "status": "success",
            "message": f"Schedule resumed: {schedule_id}"
        }

    except Exception as e:
        logger.error(f"Resume schedule error: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


def get_etl_health() -> Dict[str, Any]:
    """Get ETL system health"""
    try:
        orchestrator = get_orchestrator()
        scheduler = get_scheduler()

        # Count pipelines by status
        pipelines = orchestrator.list_pipelines()
        enabled_count = sum(1 for p in pipelines if p.get("enabled"))

        # Count schedules
        schedules = scheduler.list_schedules()
        active_schedules = sum(1 for s in schedules if s.get("enabled"))

        # Check recent failures
        recent_failures = 0
        for pipeline in pipelines:
            status = orchestrator.get_pipeline_status(pipeline["pipeline_id"])
            if status and "recent_runs" in status:
                recent_runs = status["recent_runs"][:5]
                recent_failures += sum(
                    1 for r in recent_runs
                    if r.get("status") == "failed"
                )

        health_status = "healthy" if recent_failures < 3 else "degraded"

        return {
            "status": "success",
            "health": health_status,
            "pipelines": {
                "total": len(pipelines),
                "enabled": enabled_count
            },
            "schedules": {
                "total": len(schedules),
                "active": active_schedules
            },
            "recent_failures": recent_failures,
            "scheduler_running": scheduler._scheduler_thread.is_alive() if scheduler._scheduler_thread else False
        }

    except Exception as e:
        logger.error(f"Get ETL health error: {e}")
        return {
            "status": "error",
            "health": "unknown",
            "message": str(e)
        }

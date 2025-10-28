"""
Pipeline Scheduler for ORFEAS AI Studio
Phase 2 - Task 11: Data Pipeline & ETL

Cron-like scheduler for ETL pipelines with:
- Cron expression parsing
- Scheduled pipeline execution
- Dependency management
- Parallel execution
- Health monitoring

Author: ORFEAS AI Development Team
Date: October 28, 2025
"""

import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import re

logger = logging.getLogger(__name__)


class ScheduleType(Enum):
    """Schedule type"""
    CRON = "cron"
    INTERVAL = "interval"
    ONCE = "once"


@dataclass
class Schedule:
    """Pipeline schedule configuration"""
    schedule_id: str
    pipeline_id: str
    schedule_type: ScheduleType
    cron_expression: Optional[str] = None  # e.g., "0 */6 * * *" (every 6 hours)
    interval_seconds: Optional[int] = None
    scheduled_time: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None


class CronParser:
    """Parse cron expressions"""

    @staticmethod
    def parse(expression: str) -> Dict[str, Set[int]]:
        """
        Parse cron expression
        Format: minute hour day month weekday
        Examples:
            "0 0 * * *" - Daily at midnight
            "0 */6 * * *" - Every 6 hours
            "*/15 * * * *" - Every 15 minutes
            "0 9 * * 1-5" - Weekdays at 9am
        """
        parts = expression.split()
        if len(parts) != 5:
            raise ValueError(f"Invalid cron expression: {expression}")

        minute, hour, day, month, weekday = parts

        return {
            "minute": CronParser._parse_field(minute, 0, 59),
            "hour": CronParser._parse_field(hour, 0, 23),
            "day": CronParser._parse_field(day, 1, 31),
            "month": CronParser._parse_field(month, 1, 12),
            "weekday": CronParser._parse_field(weekday, 0, 6)
        }

    @staticmethod
    def _parse_field(field: str, min_val: int, max_val: int) -> Set[int]:
        """Parse cron field"""
        values = set()

        # Handle wildcard
        if field == "*":
            return set(range(min_val, max_val + 1))

        # Handle ranges and steps
        for part in field.split(","):
            if "/" in part:
                # Step values
                range_part, step = part.split("/")
                step = int(step)

                if range_part == "*":
                    start, end = min_val, max_val
                else:
                    start = end = int(range_part)

                values.update(range(start, end + 1, step))

            elif "-" in part:
                # Range
                start, end = map(int, part.split("-"))
                values.update(range(start, end + 1))

            else:
                # Single value
                values.add(int(part))

        return values

    @staticmethod
    def next_run_time(expression: str, after: datetime = None) -> datetime:
        """Calculate next run time from cron expression"""
        if after is None:
            after = datetime.now()

        parsed = CronParser.parse(expression)

        # Start from next minute
        current = after.replace(second=0, microsecond=0) + timedelta(minutes=1)

        # Find next matching time (max 1 year ahead)
        max_iterations = 365 * 24 * 60
        for _ in range(max_iterations):
            if (current.minute in parsed["minute"] and
                current.hour in parsed["hour"] and
                current.day in parsed["day"] and
                current.month in parsed["month"] and
                current.weekday() in parsed["weekday"]):
                return current

            current += timedelta(minutes=1)

        raise ValueError("Could not find next run time")


class PipelineScheduler:
    """Schedule and execute pipelines"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.schedules: Dict[str, Schedule] = {}
        self.running_pipelines: Set[str] = set()
        self._lock = threading.Lock()
        self._scheduler_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        logger.info("[ORFEAS PHASE 2 TASK 11] Pipeline scheduler initialized")

    def add_schedule(self, schedule: Schedule) -> None:
        """Add pipeline schedule"""
        with self._lock:
            self.schedules[schedule.schedule_id] = schedule

            # Calculate next run
            if schedule.schedule_type == ScheduleType.CRON and schedule.cron_expression:
                schedule.next_run = CronParser.next_run_time(schedule.cron_expression)
            elif schedule.schedule_type == ScheduleType.INTERVAL and schedule.interval_seconds:
                schedule.next_run = datetime.now() + timedelta(seconds=schedule.interval_seconds)
            elif schedule.schedule_type == ScheduleType.ONCE and schedule.scheduled_time:
                schedule.next_run = schedule.scheduled_time

            logger.info(f"Schedule added: {schedule.schedule_id} - Next run: {schedule.next_run}")

    def remove_schedule(self, schedule_id: str) -> None:
        """Remove schedule"""
        with self._lock:
            if schedule_id in self.schedules:
                del self.schedules[schedule_id]
                logger.info(f"Schedule removed: {schedule_id}")

    def start(self) -> None:
        """Start scheduler"""
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            logger.warning("Scheduler already running")
            return

        self._stop_event.clear()
        self._scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self._scheduler_thread.start()

        logger.info("[ORFEAS PHASE 2 TASK 11] Scheduler started")

    def stop(self) -> None:
        """Stop scheduler"""
        self._stop_event.set()
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5)

        logger.info("[ORFEAS PHASE 2 TASK 11] Scheduler stopped")

    def _scheduler_loop(self) -> None:
        """Main scheduler loop"""
        while not self._stop_event.is_set():
            try:
                now = datetime.now()

                with self._lock:
                    for schedule in list(self.schedules.values()):
                        if not schedule.enabled:
                            continue

                        if schedule.next_run and now >= schedule.next_run:
                            self._execute_scheduled_pipeline(schedule)

                # Sleep for 30 seconds
                time.sleep(30)

            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
                time.sleep(60)

    def _execute_scheduled_pipeline(self, schedule: Schedule) -> None:
        """Execute scheduled pipeline"""

        # Check if pipeline already running
        if schedule.pipeline_id in self.running_pipelines:
            logger.warning(f"Pipeline already running: {schedule.pipeline_id}")
            return

        # Check dependencies
        if not self._check_dependencies(schedule):
            logger.warning(f"Dependencies not met for: {schedule.pipeline_id}")
            return

        # Mark as running
        self.running_pipelines.add(schedule.pipeline_id)

        # Execute in separate thread
        thread = threading.Thread(
            target=self._run_pipeline,
            args=(schedule,),
            daemon=True
        )
        thread.start()

    def _run_pipeline(self, schedule: Schedule) -> None:
        """Run pipeline in thread"""
        try:
            logger.info(f"Executing scheduled pipeline: {schedule.pipeline_id}")

            # Execute pipeline
            run = self.orchestrator.execute_pipeline(schedule.pipeline_id)

            # Update schedule
            schedule.last_run = datetime.now()

            # Calculate next run
            if schedule.schedule_type == ScheduleType.CRON and schedule.cron_expression:
                schedule.next_run = CronParser.next_run_time(schedule.cron_expression)
            elif schedule.schedule_type == ScheduleType.INTERVAL and schedule.interval_seconds:
                schedule.next_run = datetime.now() + timedelta(seconds=schedule.interval_seconds)
            elif schedule.schedule_type == ScheduleType.ONCE:
                schedule.enabled = False  # Disable after one-time execution

            logger.info(f"Pipeline completed: {schedule.pipeline_id} - Status: {run.status.value}")

        except Exception as e:
            logger.error(f"Pipeline execution error: {schedule.pipeline_id} - {e}")

        finally:
            # Remove from running
            with self._lock:
                self.running_pipelines.discard(schedule.pipeline_id)

    def _check_dependencies(self, schedule: Schedule) -> bool:
        """Check if dependencies are met"""
        if not schedule.dependencies:
            return True

        for dep_pipeline_id in schedule.dependencies:
            # Check if dependency pipeline ran successfully recently
            status = self.orchestrator.get_pipeline_status(dep_pipeline_id)

            if not status or "recent_runs" not in status:
                return False

            recent_runs = status["recent_runs"]
            if not recent_runs:
                return False

            last_run = recent_runs[0]
            if last_run["status"] != "success":
                return False

        return True

    def get_schedule_status(self, schedule_id: str) -> Optional[Dict]:
        """Get schedule status"""
        with self._lock:
            if schedule_id not in self.schedules:
                return None

            schedule = self.schedules[schedule_id]
            return {
                "schedule_id": schedule.schedule_id,
                "pipeline_id": schedule.pipeline_id,
                "schedule_type": schedule.schedule_type.value,
                "enabled": schedule.enabled,
                "last_run": schedule.last_run.isoformat() if schedule.last_run else None,
                "next_run": schedule.next_run.isoformat() if schedule.next_run else None,
                "is_running": schedule.pipeline_id in self.running_pipelines
            }

    def list_schedules(self) -> List[Dict]:
        """List all schedules"""
        with self._lock:
            return [
                self.get_schedule_status(schedule_id)
                for schedule_id in self.schedules.keys()
            ]


# Global scheduler instance
_scheduler: Optional[PipelineScheduler] = None
_scheduler_lock = threading.Lock()


def get_scheduler(orchestrator=None) -> PipelineScheduler:
    """Get global scheduler instance"""
    global _scheduler

    if _scheduler is None:
        with _scheduler_lock:
            if _scheduler is None:
                if orchestrator is None:
                    from .etl_pipeline import get_orchestrator
                    orchestrator = get_orchestrator()
                _scheduler = PipelineScheduler(orchestrator)

    return _scheduler

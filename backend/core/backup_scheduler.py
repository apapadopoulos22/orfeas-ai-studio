"""
Backup Scheduler for ORFEAS AI Studio
Phase 2 - Task 12: Disaster Recovery & Backup

Automated backup scheduling with:
- Cron-based scheduling
- Automatic backup execution
- Health monitoring
- Failure notifications

Author: ORFEAS AI Development Team
Date: October 28, 2025
"""

import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from core.backup_manager import BackupManager, BackupType

logger = logging.getLogger(__name__)


class ScheduleFrequency(Enum):
    """Schedule frequency"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


@dataclass
class BackupSchedule:
    """Backup schedule configuration"""
    schedule_id: str
    backup_id: str
    frequency: ScheduleFrequency
    backup_type: BackupType
    hour: int = 2  # Default: 2 AM
    day_of_week: Optional[int] = None  # 0 = Monday
    day_of_month: Optional[int] = None  # 1-31
    cron_expression: Optional[str] = None
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None


class BackupScheduler:
    """Schedule and execute automated backups"""

    def __init__(self, backup_manager: BackupManager):
        self.backup_manager = backup_manager
        self.schedules: Dict[str, BackupSchedule] = {}
        self._lock = threading.Lock()
        self._scheduler_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        logger.info("[ORFEAS PHASE 2 TASK 12] Backup scheduler initialized")

    def add_schedule(self, schedule: BackupSchedule) -> None:
        """Add backup schedule"""
        with self._lock:
            self.schedules[schedule.schedule_id] = schedule

            # Calculate next run
            schedule.next_run = self._calculate_next_run(schedule)

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

        logger.info("[ORFEAS PHASE 2 TASK 12] Backup scheduler started")

    def stop(self) -> None:
        """Stop scheduler"""
        self._stop_event.set()
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5)

        logger.info("[ORFEAS PHASE 2 TASK 12] Backup scheduler stopped")

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
                            self._execute_scheduled_backup(schedule)

                # Sleep for 60 seconds
                time.sleep(60)

            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
                time.sleep(60)

    def _execute_scheduled_backup(self, schedule: BackupSchedule) -> None:
        """Execute scheduled backup"""
        logger.info(f"Executing scheduled backup: {schedule.backup_id}")

        # Execute in separate thread
        thread = threading.Thread(
            target=self._run_backup,
            args=(schedule,),
            daemon=True
        )
        thread.start()

    def _run_backup(self, schedule: BackupSchedule) -> None:
        """Run backup in thread"""
        try:
            # Execute backup
            record = self.backup_manager.create_backup(
                schedule.backup_id,
                schedule.backup_type
            )

            # Update schedule
            schedule.last_run = datetime.now()
            schedule.next_run = self._calculate_next_run(schedule)

            logger.info(f"Scheduled backup completed: {schedule.backup_id} - Status: {record.status.value}")

        except Exception as e:
            logger.error(f"Scheduled backup failed: {schedule.backup_id} - {e}")

    def _calculate_next_run(self, schedule: BackupSchedule) -> datetime:
        """Calculate next run time"""
        now = datetime.now()

        if schedule.frequency == ScheduleFrequency.HOURLY:
            # Next hour
            return (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)

        elif schedule.frequency == ScheduleFrequency.DAILY:
            # Next day at specified hour
            next_run = now.replace(hour=schedule.hour, minute=0, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            return next_run

        elif schedule.frequency == ScheduleFrequency.WEEKLY:
            # Next week at specified day and hour
            days_ahead = schedule.day_of_week - now.weekday()
            if days_ahead < 0:
                days_ahead += 7
            elif days_ahead == 0 and now.hour >= schedule.hour:
                days_ahead = 7

            next_run = now + timedelta(days=days_ahead)
            next_run = next_run.replace(hour=schedule.hour, minute=0, second=0, microsecond=0)
            return next_run

        elif schedule.frequency == ScheduleFrequency.MONTHLY:
            # Next month at specified day and hour
            if schedule.day_of_month:
                next_run = now.replace(
                    day=schedule.day_of_month,
                    hour=schedule.hour,
                    minute=0,
                    second=0,
                    microsecond=0
                )
                if next_run <= now:
                    # Next month
                    if now.month == 12:
                        next_run = next_run.replace(year=now.year + 1, month=1)
                    else:
                        next_run = next_run.replace(month=now.month + 1)
                return next_run

        # Default: next day
        return now + timedelta(days=1)

    def get_schedule_status(self, schedule_id: str) -> Optional[Dict[str, Any]]:
        """Get schedule status"""
        with self._lock:
            if schedule_id not in self.schedules:
                return None

            schedule = self.schedules[schedule_id]
            return {
                "schedule_id": schedule.schedule_id,
                "backup_id": schedule.backup_id,
                "frequency": schedule.frequency.value,
                "backup_type": schedule.backup_type.value,
                "enabled": schedule.enabled,
                "last_run": schedule.last_run.isoformat() if schedule.last_run else None,
                "next_run": schedule.next_run.isoformat() if schedule.next_run else None
            }

    def list_schedules(self) -> List[Dict[str, Any]]:
        """List all schedules"""
        with self._lock:
            return [
                self.get_schedule_status(schedule_id)
                for schedule_id in self.schedules.keys()
            ]


# Global scheduler instance
_scheduler: Optional[BackupScheduler] = None
_scheduler_lock = threading.Lock()


def get_backup_scheduler(backup_manager=None) -> BackupScheduler:
    """Get global scheduler instance"""
    global _scheduler

    if _scheduler is None:
        with _scheduler_lock:
            if _scheduler is None:
                if backup_manager is None:
                    from core.backup_manager import get_backup_manager
                    backup_manager = get_backup_manager()
                _scheduler = BackupScheduler(backup_manager)

    return _scheduler

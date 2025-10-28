"""
Disaster Recovery Integration for ORFEAS AI Studio
Phase 2 - Task 12: Disaster Recovery & Backup

Integration layer for backup and disaster recovery.

Author: ORFEAS AI Development Team
Date: October 28, 2025
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from core.backup_manager import (
    get_backup_manager,
    BackupConfig,
    BackupType,
    BackupStatus
)
from core.backup_scheduler import (
    get_backup_scheduler,
    BackupSchedule,
    ScheduleFrequency
)

logger = logging.getLogger(__name__)


def initialize_backup_system(backup_dir: str = "./backups") -> Dict[str, Any]:
    """Initialize backup and disaster recovery system"""
    try:
        # Get backup manager and scheduler
        backup_manager = get_backup_manager(backup_dir)
        scheduler = get_backup_scheduler(backup_manager)

        # Register default backup configurations
        _register_default_backups(backup_manager)

        # Schedule default backups
        _schedule_default_backups(scheduler)

        # Start scheduler
        scheduler.start()

        logger.info("[ORFEAS PHASE 2 TASK 12] Backup system initialized successfully")

        return {
            "status": "success",
            "message": "Backup system initialized",
            "backups_registered": len(backup_manager.configs),
            "schedules_active": len(scheduler.schedules),
            "backup_directory": backup_dir
        }

    except Exception as e:
        logger.error(f"Backup system initialization failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


def _register_default_backups(backup_manager) -> None:
    """Register default backup configurations"""

    # Backup 1: Application Data
    app_data_backup = BackupConfig(
        backup_id="app_data_backup",
        name="Application Data Backup",
        description="Backup of critical application data",
        source_paths=[
            "./data",
            "./cache",
            "./uploads"
        ],
        backup_dir="./backups/app_data",
        backup_type=BackupType.FULL,
        compress=True,
        encrypt=False,
        retention_days=30,
        max_backups=10,
        verify_after_backup=True
    )
    backup_manager.register_backup(app_data_backup)

    # Backup 2: Database
    database_backup = BackupConfig(
        backup_id="database_backup",
        name="Database Backup",
        description="Backup of database files",
        source_paths=[
            "./database"
        ],
        backup_dir="./backups/database",
        backup_type=BackupType.FULL,
        compress=True,
        encrypt=True,
        retention_days=60,
        max_backups=20,
        verify_after_backup=True,
        metadata={
            "critical": True
        }
    )
    backup_manager.register_backup(database_backup)

    # Backup 3: Configuration Files
    config_backup = BackupConfig(
        backup_id="config_backup",
        name="Configuration Backup",
        description="Backup of system configuration files",
        source_paths=[
            "./backend/config",
            "./.env"
        ],
        backup_dir="./backups/config",
        backup_type=BackupType.FULL,
        compress=True,
        encrypt=True,
        retention_days=90,
        max_backups=30,
        verify_after_backup=True,
        metadata={
            "critical": True
        }
    )
    backup_manager.register_backup(config_backup)

    # Backup 4: Models (3D Generation Models)
    models_backup = BackupConfig(
        backup_id="models_backup",
        name="AI Models Backup",
        description="Backup of trained AI models",
        source_paths=[
            "./models",
            "./weights"
        ],
        backup_dir="./backups/models",
        backup_type=BackupType.INCREMENTAL,
        compress=True,
        encrypt=False,
        retention_days=180,
        max_backups=5,
        verify_after_backup=True
    )
    backup_manager.register_backup(models_backup)

    logger.info("[ORFEAS PHASE 2 TASK 12] Default backups registered")


def _schedule_default_backups(scheduler) -> None:
    """Schedule default backups"""

    # Schedule 1: Application Data - Daily at 2 AM
    app_data_schedule = BackupSchedule(
        schedule_id="app_data_daily",
        backup_id="app_data_backup",
        frequency=ScheduleFrequency.DAILY,
        backup_type=BackupType.FULL,
        hour=2,
        enabled=True
    )
    scheduler.add_schedule(app_data_schedule)

    # Schedule 2: Database - Daily at 3 AM
    database_schedule = BackupSchedule(
        schedule_id="database_daily",
        backup_id="database_backup",
        frequency=ScheduleFrequency.DAILY,
        backup_type=BackupType.FULL,
        hour=3,
        enabled=True
    )
    scheduler.add_schedule(database_schedule)

    # Schedule 3: Configuration - Weekly on Sunday at 4 AM
    config_schedule = BackupSchedule(
        schedule_id="config_weekly",
        backup_id="config_backup",
        frequency=ScheduleFrequency.WEEKLY,
        backup_type=BackupType.FULL,
        hour=4,
        day_of_week=6,  # Sunday
        enabled=True
    )
    scheduler.add_schedule(config_schedule)

    # Schedule 4: Models - Monthly on 1st at 5 AM
    models_schedule = BackupSchedule(
        schedule_id="models_monthly",
        backup_id="models_backup",
        frequency=ScheduleFrequency.MONTHLY,
        backup_type=BackupType.INCREMENTAL,
        hour=5,
        day_of_month=1,
        enabled=True
    )
    scheduler.add_schedule(models_schedule)

    logger.info("[ORFEAS PHASE 2 TASK 12] Default schedules configured")


def create_backup_now(backup_id: str, backup_type: Optional[str] = None) -> Dict[str, Any]:
    """Create backup immediately"""
    try:
        backup_manager = get_backup_manager()

        # Convert backup_type string to enum
        backup_type_enum = None
        if backup_type:
            backup_type_enum = BackupType(backup_type)

        record = backup_manager.create_backup(backup_id, backup_type_enum)

        return {
            "status": "success",
            "record_id": record.record_id,
            "backup_id": record.backup_id,
            "backup_status": record.status.value,
            "backup_size_mb": record.backup_size / 1024 / 1024,
            "files_backed_up": record.files_backed_up,
            "compression_ratio": record.compression_ratio,
            "start_time": record.start_time.isoformat(),
            "end_time": record.end_time.isoformat() if record.end_time else None
        }

    except Exception as e:
        logger.error(f"Backup creation error: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


def restore_backup(record_id: str, restore_dir: str) -> Dict[str, Any]:
    """Restore from backup"""
    try:
        backup_manager = get_backup_manager()

        success = backup_manager.restore_backup(record_id, restore_dir, verify_first=True)

        if success:
            return {
                "status": "success",
                "message": f"Backup restored to {restore_dir}",
                "record_id": record_id
            }
        else:
            return {
                "status": "error",
                "message": "Restore failed"
            }

    except Exception as e:
        logger.error(f"Backup restore error: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


def get_backup_stats(backup_id: str) -> Dict[str, Any]:
    """Get backup statistics"""
    try:
        backup_manager = get_backup_manager()
        return backup_manager.get_backup_status(backup_id)

    except Exception as e:
        logger.error(f"Get backup stats error: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


def list_all_backups() -> Dict[str, Any]:
    """List all backup configurations"""
    try:
        backup_manager = get_backup_manager()
        backups = backup_manager.list_backups()

        return {
            "status": "success",
            "count": len(backups),
            "backups": backups
        }

    except Exception as e:
        logger.error(f"List backups error: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


def list_backup_schedules() -> Dict[str, Any]:
    """List all backup schedules"""
    try:
        scheduler = get_backup_scheduler()
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


def pause_backup_schedule(schedule_id: str) -> Dict[str, Any]:
    """Pause backup schedule"""
    try:
        scheduler = get_backup_scheduler()

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


def resume_backup_schedule(schedule_id: str) -> Dict[str, Any]:
    """Resume backup schedule"""
    try:
        scheduler = get_backup_scheduler()

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


def get_backup_health() -> Dict[str, Any]:
    """Get backup system health"""
    try:
        backup_manager = get_backup_manager()
        scheduler = get_backup_scheduler()

        # Count backups by status
        all_records = list(backup_manager.records.values())
        verified_backups = sum(1 for r in all_records if r.status == BackupStatus.VERIFIED)
        failed_backups = sum(1 for r in all_records[-10:] if r.status == BackupStatus.FAILED)  # Last 10

        # Calculate total backup size
        total_size = sum(r.backup_size for r in all_records if r.status == BackupStatus.VERIFIED)

        # Check scheduler
        schedules = scheduler.list_schedules()
        active_schedules = sum(1 for s in schedules if s.get("enabled"))

        # Determine health
        health_status = "healthy"
        if failed_backups > 3:
            health_status = "degraded"
        elif failed_backups > 5:
            health_status = "critical"

        return {
            "status": "success",
            "health": health_status,
            "backups": {
                "total": len(all_records),
                "verified": verified_backups,
                "recent_failures": failed_backups
            },
            "storage": {
                "total_size_mb": total_size / 1024 / 1024,
                "total_size_gb": total_size / 1024 / 1024 / 1024
            },
            "schedules": {
                "total": len(schedules),
                "active": active_schedules
            },
            "scheduler_running": scheduler._scheduler_thread.is_alive() if scheduler._scheduler_thread else False
        }

    except Exception as e:
        logger.error(f"Get backup health error: {e}")
        return {
            "status": "error",
            "health": "unknown",
            "message": str(e)
        }


def test_disaster_recovery() -> Dict[str, Any]:
    """Test disaster recovery procedures"""
    try:
        results = []

        # Test 1: Create test backup
        test_backup_config = BackupConfig(
            backup_id="dr_test",
            name="DR Test Backup",
            description="Test backup for disaster recovery",
            source_paths=["./README.md"],
            backup_dir="./backups/dr_test",
            backup_type=BackupType.FULL,
            compress=True,
            encrypt=False,
            retention_days=1,
            max_backups=1
        )

        backup_manager = get_backup_manager()
        backup_manager.register_backup(test_backup_config)

        # Create backup
        record = backup_manager.create_backup("dr_test")
        results.append({
            "test": "create_backup",
            "passed": record.status == BackupStatus.VERIFIED,
            "details": f"Status: {record.status.value}"
        })

        # Test 2: Restore backup
        restore_dir = "./backups/dr_test/restore"
        success = backup_manager.restore_backup(record.record_id, restore_dir)
        results.append({
            "test": "restore_backup",
            "passed": success,
            "details": f"Restored to {restore_dir}"
        })

        # Cleanup
        import shutil
        if Path(restore_dir).exists():
            shutil.rmtree(restore_dir)

        all_passed = all(r["passed"] for r in results)

        return {
            "status": "success",
            "dr_test_passed": all_passed,
            "tests": results
        }

    except Exception as e:
        logger.error(f"DR test error: {e}")
        return {
            "status": "error",
            "dr_test_passed": False,
            "message": str(e)
        }

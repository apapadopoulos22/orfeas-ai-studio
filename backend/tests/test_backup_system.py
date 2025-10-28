"""
Test Suite for Backup and Disaster Recovery System
Phase 2 - Task 12: Disaster Recovery & Backup

Comprehensive tests for backup manager, scheduler, and integration.

Author: ORFEAS AI Development Team
Date: October 28, 2025
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import time

from core.backup_manager import (
    BackupManager,
    BackupConfig,
    BackupType,
    BackupStatus,
    BackupCompressor,
    BackupEncryptor,
    BackupVerifier
)
from core.backup_scheduler import (
    BackupScheduler,
    BackupSchedule,
    ScheduleFrequency
)
from disaster_recovery import (
    initialize_backup_system,
    create_backup_now,
    restore_backup,
    get_backup_health,
    test_disaster_recovery
)


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    temp = tempfile.mkdtemp()
    yield temp
    shutil.rmtree(temp, ignore_errors=True)


@pytest.fixture
def backup_manager(temp_dir):
    """Create BackupManager instance"""
    return BackupManager(base_backup_dir=temp_dir)


@pytest.fixture
def test_config(temp_dir):
    """Create test backup configuration"""
    source_dir = Path(temp_dir) / "source"
    source_dir.mkdir()

    # Create test files
    (source_dir / "file1.txt").write_text("Test content 1")
    (source_dir / "file2.txt").write_text("Test content 2")

    return BackupConfig(
        backup_id="test_backup",
        name="Test Backup",
        description="Test backup configuration",
        source_paths=[str(source_dir)],
        backup_dir=str(Path(temp_dir) / "backups"),
        backup_type=BackupType.FULL,
        compress=True,
        encrypt=False,
        retention_days=7,
        max_backups=5
    )


class TestBackupCompressor:
    """Test backup compression"""

    def test_compress_directory(self, temp_dir):
        """Test directory compression"""
        source_dir = Path(temp_dir) / "source"
        source_dir.mkdir()

        # Create test files
        (source_dir / "file1.txt").write_text("A" * 1000)
        (source_dir / "file2.txt").write_text("B" * 2000)

        compressor = BackupCompressor()
        archive_path = Path(temp_dir) / "test.tar.gz"

        original_size, compressed_size = compressor.compress_directory(
            str(source_dir),
            str(archive_path)
        )

        assert archive_path.exists()
        assert original_size > 0
        assert compressed_size > 0
        assert compressed_size < original_size  # Compression should reduce size

    def test_decompress_archive(self, temp_dir):
        """Test archive decompression"""
        source_dir = Path(temp_dir) / "source"
        source_dir.mkdir()

        # Create test file
        test_content = "Test content for decompression"
        (source_dir / "test.txt").write_text(test_content)

        # Compress
        compressor = BackupCompressor()
        archive_path = Path(temp_dir) / "test.tar.gz"
        compressor.compress_directory(str(source_dir), str(archive_path))

        # Decompress
        extract_dir = Path(temp_dir) / "extracted"
        compressor.decompress_archive(str(archive_path), str(extract_dir))

        # Verify
        extracted_file = extract_dir / "test.txt"
        assert extracted_file.exists()
        assert extracted_file.read_text() == test_content

    def test_compression_ratio(self, temp_dir):
        """Test compression ratio calculation"""
        source_dir = Path(temp_dir) / "source"
        source_dir.mkdir()

        # Create highly compressible content
        (source_dir / "repeat.txt").write_text("A" * 10000)

        compressor = BackupCompressor()
        archive_path = Path(temp_dir) / "test.tar.gz"

        original_size, compressed_size = compressor.compress_directory(
            str(source_dir),
            str(archive_path)
        )

        ratio = (1 - compressed_size / original_size) * 100
        assert ratio > 50  # Should compress >50%


class TestBackupEncryptor:
    """Test backup encryption"""

    def test_encrypt_decrypt_file(self, temp_dir):
        """Test file encryption and decryption"""
        encryptor = BackupEncryptor()

        # Create test file
        original_file = Path(temp_dir) / "original.txt"
        test_content = "Secret backup content"
        original_file.write_bytes(test_content.encode())

        # Encrypt
        encrypted_file = Path(temp_dir) / "encrypted.bin"
        encryptor.encrypt_file(str(original_file), str(encrypted_file))

        assert encrypted_file.exists()
        assert encrypted_file.read_bytes() != test_content.encode()

        # Decrypt
        decrypted_file = Path(temp_dir) / "decrypted.txt"
        encryptor.decrypt_file(str(encrypted_file), str(decrypted_file))

        assert decrypted_file.read_text() == test_content

    def test_encryption_key_consistency(self, temp_dir):
        """Test encryption with same key produces consistent results"""
        encryptor = BackupEncryptor()

        original_file = Path(temp_dir) / "original.txt"
        original_file.write_text("Test content")

        encrypted_file = Path(temp_dir) / "encrypted.bin"
        encryptor.encrypt_file(str(original_file), str(encrypted_file))

        decrypted_file = Path(temp_dir) / "decrypted.txt"
        encryptor.decrypt_file(str(encrypted_file), str(decrypted_file))

        assert original_file.read_text() == decrypted_file.read_text()


class TestBackupVerifier:
    """Test backup verification"""

    def test_calculate_checksum(self, temp_dir):
        """Test checksum calculation"""
        verifier = BackupVerifier()

        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("Test content for checksum")

        checksum = verifier.calculate_checksum(str(test_file))

        assert checksum is not None
        assert len(checksum) == 64  # SHA-256 hex length

    def test_verify_backup(self, temp_dir):
        """Test backup verification"""
        verifier = BackupVerifier()

        test_file = Path(temp_dir) / "backup.tar.gz"
        test_file.write_text("Backup content")

        checksum = verifier.calculate_checksum(str(test_file))

        # Verification should pass with correct checksum
        assert verifier.verify_backup(str(test_file), checksum) is True

        # Verification should fail with wrong checksum
        assert verifier.verify_backup(str(test_file), "wrong_checksum") is False

    def test_test_restore(self, temp_dir):
        """Test restore testing"""
        # Create backup archive
        source_dir = Path(temp_dir) / "source"
        source_dir.mkdir()
        (source_dir / "test.txt").write_text("Test content")

        compressor = BackupCompressor()
        archive_path = Path(temp_dir) / "test.tar.gz"
        compressor.compress_directory(str(source_dir), str(archive_path))

        # Test restore
        verifier = BackupVerifier()
        test_dir = Path(temp_dir) / "test_restore"

        result = verifier.test_restore(str(archive_path), str(test_dir))
        assert result is True


class TestBackupManager:
    """Test BackupManager"""

    def test_register_backup(self, backup_manager, test_config):
        """Test backup registration"""
        backup_manager.register_backup(test_config)

        assert "test_backup" in backup_manager.configs
        assert backup_manager.configs["test_backup"].name == "Test Backup"

    def test_create_full_backup(self, backup_manager, test_config):
        """Test full backup creation"""
        backup_manager.register_backup(test_config)

        record = backup_manager.create_backup("test_backup", BackupType.FULL)

        assert record is not None
        assert record.backup_id == "test_backup"
        assert record.backup_type == BackupType.FULL
        assert record.files_backed_up > 0

    def test_backup_verification(self, backup_manager, test_config):
        """Test backup verification after creation"""
        test_config.verify_after_backup = True
        backup_manager.register_backup(test_config)

        record = backup_manager.create_backup("test_backup")

        assert record.status in [BackupStatus.VERIFIED, BackupStatus.COMPLETED]
        assert record.checksum is not None

    def test_restore_backup(self, backup_manager, test_config, temp_dir):
        """Test backup restoration"""
        backup_manager.register_backup(test_config)

        # Create backup
        record = backup_manager.create_backup("test_backup")

        # Restore
        restore_dir = Path(temp_dir) / "restored"
        success = backup_manager.restore_backup(record.record_id, str(restore_dir))

        assert success is True
        assert restore_dir.exists()

    def test_retention_policy_max_backups(self, backup_manager, test_config, temp_dir):
        """Test retention policy - max backups"""
        test_config.max_backups = 3
        backup_manager.register_backup(test_config)

        # Create 5 backups
        for i in range(5):
            backup_manager.create_backup("test_backup")
            time.sleep(0.1)  # Ensure different timestamps

        # Should only keep 3 backups
        records = [r for r in backup_manager.records.values() if r.backup_id == "test_backup"]
        assert len(records) <= 3

    def test_backup_persistence(self, backup_manager, test_config, temp_dir):
        """Test backup record persistence"""
        backup_manager.register_backup(test_config)

        # Create backup
        record = backup_manager.create_backup("test_backup")

        # Save records
        backup_manager._save_records()

        # Create new manager instance
        new_manager = BackupManager(base_backup_dir=temp_dir)

        # Records should be loaded
        assert record.record_id in new_manager.records

    def test_get_backup_status(self, backup_manager, test_config):
        """Test getting backup status"""
        backup_manager.register_backup(test_config)
        backup_manager.create_backup("test_backup")

        status = backup_manager.get_backup_status("test_backup")

        assert "backup_id" in status
        assert "total_backups" in status
        assert "latest_backup" in status


class TestBackupScheduler:
    """Test BackupScheduler"""

    def test_add_schedule(self, backup_manager):
        """Test adding backup schedule"""
        scheduler = BackupScheduler(backup_manager)

        schedule = BackupSchedule(
            schedule_id="test_schedule",
            backup_id="test_backup",
            frequency=ScheduleFrequency.DAILY,
            backup_type=BackupType.FULL,
            hour=2
        )

        scheduler.add_schedule(schedule)

        assert "test_schedule" in scheduler.schedules

    def test_remove_schedule(self, backup_manager):
        """Test removing backup schedule"""
        scheduler = BackupScheduler(backup_manager)

        schedule = BackupSchedule(
            schedule_id="test_schedule",
            backup_id="test_backup",
            frequency=ScheduleFrequency.DAILY
        )

        scheduler.add_schedule(schedule)
        scheduler.remove_schedule("test_schedule")

        assert "test_schedule" not in scheduler.schedules

    def test_calculate_next_run_hourly(self, backup_manager):
        """Test calculating next run for hourly frequency"""
        scheduler = BackupScheduler(backup_manager)

        schedule = BackupSchedule(
            schedule_id="test",
            backup_id="test",
            frequency=ScheduleFrequency.HOURLY
        )

        next_run = scheduler._calculate_next_run(schedule)

        assert next_run > datetime.now()
        assert (next_run - datetime.now()).total_seconds() <= 3600

    def test_calculate_next_run_daily(self, backup_manager):
        """Test calculating next run for daily frequency"""
        scheduler = BackupScheduler(backup_manager)

        schedule = BackupSchedule(
            schedule_id="test",
            backup_id="test",
            frequency=ScheduleFrequency.DAILY,
            hour=3
        )

        next_run = scheduler._calculate_next_run(schedule)

        assert next_run > datetime.now()
        assert next_run.hour == 3

    def test_calculate_next_run_weekly(self, backup_manager):
        """Test calculating next run for weekly frequency"""
        scheduler = BackupScheduler(backup_manager)

        schedule = BackupSchedule(
            schedule_id="test",
            backup_id="test",
            frequency=ScheduleFrequency.WEEKLY,
            hour=4,
            day_of_week=6  # Sunday
        )

        next_run = scheduler._calculate_next_run(schedule)

        assert next_run > datetime.now()
        assert next_run.weekday() == 6
        assert next_run.hour == 4

    def test_scheduler_start_stop(self, backup_manager):
        """Test scheduler start and stop"""
        scheduler = BackupScheduler(backup_manager)

        scheduler.start()
        assert scheduler._running is True

        scheduler.stop()
        assert scheduler._running is False

    def test_list_schedules(self, backup_manager):
        """Test listing schedules"""
        scheduler = BackupScheduler(backup_manager)

        schedule = BackupSchedule(
            schedule_id="test",
            backup_id="test",
            frequency=ScheduleFrequency.DAILY
        )

        scheduler.add_schedule(schedule)
        schedules = scheduler.list_schedules()

        assert len(schedules) == 1
        assert schedules[0]["schedule_id"] == "test"


class TestDisasterRecoveryIntegration:
    """Test disaster recovery integration"""

    def test_initialize_backup_system(self, temp_dir):
        """Test backup system initialization"""
        result = initialize_backup_system(temp_dir)

        assert result["status"] == "success"
        assert result["backups_registered"] > 0
        assert result["schedules_active"] > 0

    def test_create_backup_now(self, temp_dir):
        """Test immediate backup creation"""
        initialize_backup_system(temp_dir)

        result = create_backup_now("app_data_backup", "FULL")

        assert "record_id" in result or "status" in result

    def test_get_backup_health(self, temp_dir):
        """Test backup health check"""
        initialize_backup_system(temp_dir)

        health = get_backup_health()

        assert "status" in health
        assert "health" in health
        assert "backups" in health
        assert "schedules" in health

    def test_disaster_recovery_test(self):
        """Test disaster recovery testing function"""
        result = test_disaster_recovery()

        assert "status" in result
        assert "dr_test_passed" in result


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

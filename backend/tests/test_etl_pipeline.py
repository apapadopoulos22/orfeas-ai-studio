"""
Test Suite for ETL Pipeline System
Phase 2 - Task 11: Data Pipeline & ETL

Comprehensive tests for:
- Pipeline orchestration
- Data extraction, transformation, loading
- Pipeline scheduling
- Cron expression parsing
- Error handling and retries
- Integration with backend

Author: ORFEAS AI Development Team
Date: October 28, 2025
"""

import pytest
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
import tempfile

# Import core modules
from core.etl_pipeline import (
    PipelineOrchestrator,
    PipelineConfig,
    DataSource,
    PipelineStatus,
    DataExtractor,
    DataTransformer,
    DataLoader,
    DataValidator
)
from core.pipeline_scheduler import (
    PipelineScheduler,
    Schedule,
    ScheduleType,
    CronParser
)
from pipeline_integration import (
    initialize_etl_system,
    execute_pipeline_now,
    get_pipeline_stats,
    list_all_pipelines,
    list_all_schedules,
    get_etl_health
)


class TestCronParser:
    """Test cron expression parsing"""

    def test_parse_wildcard(self):
        """Test wildcard parsing"""
        result = CronParser.parse("* * * * *")
        assert len(result["minute"]) == 60
        assert len(result["hour"]) == 24

    def test_parse_specific_values(self):
        """Test specific values"""
        result = CronParser.parse("0 9 * * 1-5")
        assert 0 in result["minute"]
        assert 9 in result["hour"]
        assert 1 in result["weekday"]
        assert 5 in result["weekday"]

    def test_parse_step_values(self):
        """Test step values"""
        result = CronParser.parse("*/15 */6 * * *")
        assert 0 in result["minute"]
        assert 15 in result["minute"]
        assert 30 in result["minute"]
        assert 45 in result["minute"]
        assert 0 in result["hour"]
        assert 6 in result["hour"]
        assert 12 in result["hour"]

    def test_parse_ranges(self):
        """Test range parsing"""
        result = CronParser.parse("0 9-17 * * *")
        assert all(h in result["hour"] for h in range(9, 18))

    def test_next_run_time(self):
        """Test next run time calculation"""
        # Every hour at minute 0
        now = datetime(2025, 10, 28, 14, 30)
        next_run = CronParser.next_run_time("0 * * * *", after=now)
        assert next_run.hour == 15
        assert next_run.minute == 0

    def test_next_run_time_daily(self):
        """Test daily schedule"""
        now = datetime(2025, 10, 28, 14, 0)
        next_run = CronParser.next_run_time("0 2 * * *", after=now)
        assert next_run.day == 29  # Next day at 2 AM
        assert next_run.hour == 2


class TestDataValidator:
    """Test data validation"""

    def test_add_rule(self):
        """Test adding validation rule"""
        validator = DataValidator()
        validator.add_rule("is_positive", lambda x: x > 0)
        assert "is_positive" in validator.validation_rules

    def test_validate_success(self):
        """Test successful validation"""
        validator = DataValidator()
        validator.add_rule("is_dict", lambda x: isinstance(x, dict))

        is_valid, errors = validator.validate({"key": "value"}, ["is_dict"])
        assert is_valid
        assert len(errors) == 0

    def test_validate_failure(self):
        """Test validation failure"""
        validator = DataValidator()
        validator.add_rule("is_list", lambda x: isinstance(x, list))

        is_valid, errors = validator.validate({"key": "value"}, ["is_list"])
        assert not is_valid
        assert len(errors) > 0

    def test_validate_unknown_rule(self):
        """Test unknown rule"""
        validator = DataValidator()
        is_valid, errors = validator.validate({}, ["unknown_rule"])
        assert not is_valid
        assert "Unknown rule" in errors[0]


class TestDataExtractor:
    """Test data extraction"""

    def test_extract_from_api(self):
        """Test API extraction"""
        extractor = DataExtractor()
        data, checkpoint = extractor.extract(
            DataSource.API,
            {"url": "https://api.example.com/data"}
        )
        assert len(data) > 0
        assert checkpoint is not None

    def test_extract_from_database(self):
        """Test database extraction"""
        extractor = DataExtractor()
        data, checkpoint = extractor.extract(
            DataSource.DATABASE,
            {"table": "test_table", "query": "SELECT * FROM test"}
        )
        assert len(data) > 0
        assert checkpoint is not None

    def test_extract_from_file(self):
        """Test file extraction"""
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([{"id": 1, "name": "test"}], f)
            temp_path = f.name

        try:
            extractor = DataExtractor()
            data, checkpoint = extractor.extract(
                DataSource.FILE,
                {"path": temp_path}
            )
            assert len(data) > 0
            assert "id" in data[0]
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_extract_with_checkpoint(self):
        """Test incremental extraction"""
        extractor = DataExtractor()
        checkpoint = (datetime.now() - timedelta(hours=1)).isoformat()

        data, new_checkpoint = extractor.extract(
            DataSource.API,
            {"url": "https://api.example.com/data"},
            checkpoint=checkpoint
        )

        # New checkpoint should be more recent than old checkpoint
        assert new_checkpoint is not None
        assert len(data) > 0
class TestDataTransformer:
    """Test data transformation"""

    def test_normalize(self):
        """Test normalization"""
        transformer = DataTransformer()
        data = [{"Name": "Test", "VALUE": 123}]

        result = transformer.transform(data, ["normalize"])
        assert "name" in result[0]
        assert "value" in result[0]
        assert "_processed_at" in result[0]

    def test_aggregate(self):
        """Test aggregation"""
        transformer = DataTransformer()
        data = [
            {"type": "A", "value": 1},
            {"type": "A", "value": 2},
            {"type": "B", "value": 3}
        ]

        result = transformer.transform(
            data,
            ["aggregate"],
            {"group_by": "type"}
        )

        assert len(result) == 2  # Two groups: A and B
        assert any(r["type"] == "A" and r["count"] == 2 for r in result)

    def test_filter(self):
        """Test filtering"""
        transformer = DataTransformer()
        data = [
            {"status": "active", "value": 1},
            {"status": "inactive", "value": 2},
            {"status": "active", "value": 3}
        ]

        result = transformer.transform(
            data,
            ["filter"],
            {"filter_key": "status", "filter_value": "active"}
        )

        assert len(result) == 2
        assert all(r["status"] == "active" for r in result)

    def test_enrich(self):
        """Test enrichment"""
        transformer = DataTransformer()
        data = [{"id": 1}]

        result = transformer.transform(
            data,
            ["enrich"],
            {"add_fields": {"source": "test", "version": "1.0"}}
        )

        assert "source" in result[0]
        assert result[0]["source"] == "test"
        assert "_record_hash" in result[0]

    def test_deduplicate(self):
        """Test deduplication"""
        transformer = DataTransformer()
        data = [
            {"id": 1, "name": "test"},
            {"id": 1, "name": "test"},
            {"id": 2, "name": "other"}
        ]

        # First enrich to add hashes
        enriched = transformer.transform(data, ["enrich"])
        # Then deduplicate
        result = transformer.transform(enriched, ["deduplicate"])

        assert len(result) == 2  # Two unique records

    def test_hash_sensitive_data(self):
        """Test sensitive data hashing"""
        transformer = DataTransformer()
        data = [{"email": "user@example.com", "name": "Test"}]

        result = transformer.transform(
            data,
            ["hash"],
            {"sensitive_fields": ["email"]}
        )

        assert result[0]["email"] != "user@example.com"
        assert len(result[0]["email"]) == 64  # SHA256 hash length


class TestDataLoader:
    """Test data loading"""

    def test_load_to_file(self):
        """Test file loading"""
        loader = DataLoader()
        data = [{"id": 1, "value": "test"}]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = str(Path(tmpdir) / "output.json")

            count = loader.load(
                data,
                "file",
                {"path": output_path}
            )

            assert count == len(data)
            assert Path(output_path).exists()

            # Verify content
            with open(output_path) as f:
                loaded = json.load(f)
                assert loaded == data

    def test_load_to_file_compressed(self):
        """Test compressed file loading"""
        loader = DataLoader()
        data = [{"id": i, "data": f"test_{i}"} for i in range(100)]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = str(Path(tmpdir) / "output.json")

            count = loader.load(
                data,
                "file",
                {"path": output_path, "compress": True}
            )

            assert count == len(data)
            assert Path(f"{output_path}.gz").exists()

    def test_load_to_database(self):
        """Test database loading"""
        loader = DataLoader()
        data = [{"id": 1, "name": "test"}]

        count = loader.load(
            data,
            "database",
            {"table": "test_table"}
        )

        assert count == len(data)

    def test_load_incremental(self):
        """Test incremental loading"""
        loader = DataLoader()
        data = [{"id": 1, "value": "updated"}]

        count = loader.load(
            data,
            "database",
            {"table": "test_table"},
            incremental=True
        )

        assert count == len(data)


class TestPipelineOrchestrator:
    """Test pipeline orchestration"""

    def test_register_pipeline(self):
        """Test pipeline registration"""
        orchestrator = PipelineOrchestrator()

        config = PipelineConfig(
            pipeline_id="test_pipeline",
            name="Test Pipeline",
            description="Test",
            source_type=DataSource.API,
            source_config={"url": "https://api.example.com"},
            transformations=["normalize"],
            destination="file"
        )

        orchestrator.register_pipeline(config)
        assert "test_pipeline" in orchestrator.pipelines

    def test_execute_pipeline(self):
        """Test pipeline execution"""
        orchestrator = PipelineOrchestrator()

        # Create temp output directory
        with tempfile.TemporaryDirectory() as tmpdir:
            config = PipelineConfig(
                pipeline_id="test_exec",
                name="Test Execution",
                description="Test",
                source_type=DataSource.API,
                source_config={"url": "https://api.example.com"},
                transformations=["normalize", "enrich"],
                destination="file",
                metadata={
                    "load_config": {
                        "path": str(Path(tmpdir) / "output.json")
                    }
                }
            )

            orchestrator.register_pipeline(config)
            run = orchestrator.execute_pipeline("test_exec", manual_trigger=True)

            assert run.status == PipelineStatus.SUCCESS
            assert run.records_extracted > 0
            assert run.records_transformed > 0
            assert run.records_loaded > 0
            assert run.end_time is not None

    def test_execute_with_retry(self):
        """Test retry logic"""
        orchestrator = PipelineOrchestrator()

        config = PipelineConfig(
            pipeline_id="test_retry",
            name="Test Retry",
            description="Test",
            source_type=DataSource.FILE,  # Will fail - file doesn't exist
            source_config={"path": "/nonexistent/file.json"},
            transformations=[],
            destination="file",
            max_retries=2,
            retry_delay=1
        )

        orchestrator.register_pipeline(config)
        run = orchestrator.execute_pipeline("test_retry", manual_trigger=True)

        # Should fail but not crash
        assert run.status in [PipelineStatus.FAILED, PipelineStatus.RETRYING]

    def test_get_pipeline_status(self):
        """Test getting pipeline status"""
        orchestrator = PipelineOrchestrator()

        config = PipelineConfig(
            pipeline_id="test_status",
            name="Test Status",
            description="Test",
            source_type=DataSource.API,
            source_config={"url": "https://api.example.com"},
            transformations=["normalize"],
            destination="file"
        )

        orchestrator.register_pipeline(config)
        orchestrator.execute_pipeline("test_status", manual_trigger=True)

        status = orchestrator.get_pipeline_status("test_status")
        assert status["pipeline_id"] == "test_status"
        assert "recent_runs" in status

    def test_list_pipelines(self):
        """Test listing pipelines"""
        orchestrator = PipelineOrchestrator()

        for i in range(3):
            config = PipelineConfig(
                pipeline_id=f"test_list_{i}",
                name=f"Test List {i}",
                description="Test",
                source_type=DataSource.API,
                source_config={"url": "https://api.example.com"},
                transformations=[],
                destination="file"
            )
            orchestrator.register_pipeline(config)

        pipelines = orchestrator.list_pipelines()
        assert len(pipelines) >= 3


class TestPipelineScheduler:
    """Test pipeline scheduling"""

    def test_add_schedule(self):
        """Test adding schedule"""
        orchestrator = PipelineOrchestrator()
        scheduler = PipelineScheduler(orchestrator)

        schedule = Schedule(
            schedule_id="test_schedule",
            pipeline_id="test_pipeline",
            schedule_type=ScheduleType.INTERVAL,
            interval_seconds=3600
        )

        scheduler.add_schedule(schedule)
        assert "test_schedule" in scheduler.schedules
        assert schedule.next_run is not None

    def test_cron_schedule(self):
        """Test cron-based schedule"""
        orchestrator = PipelineOrchestrator()
        scheduler = PipelineScheduler(orchestrator)

        schedule = Schedule(
            schedule_id="test_cron",
            pipeline_id="test_pipeline",
            schedule_type=ScheduleType.CRON,
            cron_expression="0 */6 * * *"  # Every 6 hours
        )

        scheduler.add_schedule(schedule)
        assert schedule.next_run is not None
        assert schedule.next_run > datetime.now()

    def test_scheduler_start_stop(self):
        """Test starting and stopping scheduler"""
        orchestrator = PipelineOrchestrator()
        scheduler = PipelineScheduler(orchestrator)

        scheduler.start()
        assert scheduler._scheduler_thread is not None
        assert scheduler._scheduler_thread.is_alive()

        scheduler.stop()
        time.sleep(1)
        assert not scheduler._scheduler_thread.is_alive()

    def test_get_schedule_status(self):
        """Test getting schedule status"""
        orchestrator = PipelineOrchestrator()
        scheduler = PipelineScheduler(orchestrator)

        schedule = Schedule(
            schedule_id="test_status_check",
            pipeline_id="test_pipeline",
            schedule_type=ScheduleType.INTERVAL,
            interval_seconds=3600
        )

        scheduler.add_schedule(schedule)
        status = scheduler.get_schedule_status("test_status_check")

        assert status is not None
        assert status["schedule_id"] == "test_status_check"
        assert "next_run" in status

    def test_list_schedules(self):
        """Test listing schedules"""
        orchestrator = PipelineOrchestrator()
        scheduler = PipelineScheduler(orchestrator)

        for i in range(3):
            schedule = Schedule(
                schedule_id=f"test_list_{i}",
                pipeline_id=f"pipeline_{i}",
                schedule_type=ScheduleType.INTERVAL,
                interval_seconds=3600
            )
            scheduler.add_schedule(schedule)

        schedules = scheduler.list_schedules()
        assert len(schedules) >= 3


class TestIntegration:
    """Test integration layer"""

    def test_initialize_etl_system(self):
        """Test ETL system initialization"""
        result = initialize_etl_system()
        assert result["status"] == "success"
        assert result["pipelines_registered"] > 0

    def test_list_all_pipelines(self):
        """Test listing all pipelines"""
        initialize_etl_system()
        result = list_all_pipelines()

        assert result["status"] == "success"
        assert result["count"] > 0
        assert "pipelines" in result

    def test_list_all_schedules(self):
        """Test listing all schedules"""
        initialize_etl_system()
        result = list_all_schedules()

        assert result["status"] == "success"
        assert result["count"] > 0
        assert "schedules" in result

    def test_get_etl_health(self):
        """Test ETL health check"""
        initialize_etl_system()
        result = get_etl_health()

        assert result["status"] == "success"
        assert result["health"] in ["healthy", "degraded"]
        assert "pipelines" in result
        assert "schedules" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

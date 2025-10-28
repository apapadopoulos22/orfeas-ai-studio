"""
ETL Pipeline Framework for ORFEAS AI Studio
Phase 2 - Task 11: Data Pipeline & ETL

Enterprise-grade ETL system with:
- Pipeline orchestration and scheduling
- Data extraction from multiple sources
- Data transformation and validation
- Data warehouse loading (incremental)
- Error handling and retry logic
- Performance monitoring
- Pipeline versioning

Author: ORFEAS AI Development Team
Date: October 28, 2025
"""

import logging
import json
import time
import hashlib
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
import pickle
import gzip

logger = logging.getLogger(__name__)


class PipelineStatus(Enum):
    """Pipeline execution status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class DataSource(Enum):
    """Supported data sources"""
    API = "api"
    DATABASE = "database"
    FILE = "file"
    STREAM = "stream"
    CACHE = "cache"


@dataclass
class PipelineConfig:
    """Pipeline configuration"""
    pipeline_id: str
    name: str
    description: str
    source_type: DataSource
    source_config: Dict[str, Any]
    transformations: List[str]
    destination: str
    schedule: Optional[str] = None  # Cron format
    incremental: bool = True
    batch_size: int = 1000
    max_retries: int = 3
    retry_delay: int = 60  # seconds
    timeout: int = 3600  # seconds
    version: str = "1.0"
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineRun:
    """Pipeline execution run"""
    run_id: str
    pipeline_id: str
    status: PipelineStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    records_extracted: int = 0
    records_transformed: int = 0
    records_loaded: int = 0
    records_failed: int = 0
    error_message: Optional[str] = None
    retry_count: int = 0
    metrics: Dict[str, Any] = field(default_factory=dict)
    checkpoint: Optional[str] = None


class DataValidator:
    """Data validation for ETL pipeline"""

    def __init__(self):
        self.validation_rules: Dict[str, Callable] = {}

    def add_rule(self, name: str, validator: Callable) -> None:
        """Add validation rule"""
        self.validation_rules[name] = validator

    def validate(self, data: Any, rules: List[str]) -> Tuple[bool, List[str]]:
        """Validate data against rules"""
        errors = []

        for rule_name in rules:
            if rule_name not in self.validation_rules:
                errors.append(f"Unknown rule: {rule_name}")
                continue

            try:
                if not self.validation_rules[rule_name](data):
                    errors.append(f"Validation failed: {rule_name}")
            except Exception as e:
                errors.append(f"Rule error {rule_name}: {str(e)}")

        return len(errors) == 0, errors


class DataExtractor:
    """Extract data from various sources"""

    def __init__(self):
        self.extractors: Dict[DataSource, Callable] = {
            DataSource.API: self._extract_from_api,
            DataSource.DATABASE: self._extract_from_database,
            DataSource.FILE: self._extract_from_file,
            DataSource.STREAM: self._extract_from_stream,
            DataSource.CACHE: self._extract_from_cache,
        }

    def extract(
        self,
        source_type: DataSource,
        config: Dict[str, Any],
        checkpoint: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Extract data from source"""

        if source_type not in self.extractors:
            raise ValueError(f"Unsupported source type: {source_type}")

        extractor = self.extractors[source_type]
        return extractor(config, checkpoint)

    def _extract_from_api(
        self,
        config: Dict[str, Any],
        checkpoint: Optional[str]
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Extract from API endpoint"""
        # Placeholder: In production, use requests library
        logger.info(f"Extracting from API: {config.get('url')}")

        # Simulate API data
        data = []
        for i in range(10):
            data.append({
                "id": f"api_{i}",
                "timestamp": datetime.now().isoformat(),
                "data": f"sample_{i}"
            })

        new_checkpoint = data[-1]["timestamp"] if data else checkpoint
        return data, new_checkpoint

    def _extract_from_database(
        self,
        config: Dict[str, Any],
        checkpoint: Optional[str]
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Extract from database"""
        logger.info(f"Extracting from database: {config.get('table')}")

        # Placeholder: In production, use SQLAlchemy
        query = config.get("query", "SELECT * FROM table")

        # Simulate database data
        data = []
        for i in range(10):
            data.append({
                "id": f"db_{i}",
                "created_at": datetime.now().isoformat(),
                "value": i * 100
            })

        new_checkpoint = data[-1]["created_at"] if data else checkpoint
        return data, new_checkpoint

    def _extract_from_file(
        self,
        config: Dict[str, Any],
        checkpoint: Optional[str]
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Extract from file"""
        file_path = config.get("path")
        logger.info(f"Extracting from file: {file_path}")

        if not file_path or not Path(file_path).exists():
            return [], checkpoint

        data = []
        try:
            with open(file_path, 'r') as f:
                if file_path.endswith('.json'):
                    data = json.load(f)
                elif file_path.endswith('.jsonl'):
                    data = [json.loads(line) for line in f]
                else:
                    # CSV or other format
                    data = [{"line": line.strip()} for line in f]
        except Exception as e:
            logger.error(f"File extraction error: {e}")

        return data, datetime.now().isoformat()

    def _extract_from_stream(
        self,
        config: Dict[str, Any],
        checkpoint: Optional[str]
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Extract from stream (Kafka, etc)"""
        logger.info(f"Extracting from stream: {config.get('topic')}")

        # Placeholder: In production, use kafka-python
        data = [{"stream_id": i, "event": f"event_{i}"} for i in range(5)]
        return data, datetime.now().isoformat()

    def _extract_from_cache(
        self,
        config: Dict[str, Any],
        checkpoint: Optional[str]
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Extract from cache"""
        logger.info(f"Extracting from cache: {config.get('key')}")

        # Placeholder: In production, integrate with Task 10 cache
        data = [{"cache_key": i, "cached_data": f"data_{i}"} for i in range(5)]
        return data, datetime.now().isoformat()


class DataTransformer:
    """Transform data with various operations"""

    def __init__(self):
        self.transformations: Dict[str, Callable] = {
            "normalize": self._normalize,
            "aggregate": self._aggregate,
            "filter": self._filter,
            "enrich": self._enrich,
            "deduplicate": self._deduplicate,
            "hash": self._hash_sensitive_data,
        }

    def transform(
        self,
        data: List[Dict[str, Any]],
        operations: List[str],
        config: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Apply transformations to data"""

        transformed = data
        config = config or {}

        for operation in operations:
            if operation not in self.transformations:
                logger.warning(f"Unknown transformation: {operation}")
                continue

            try:
                transformed = self.transformations[operation](transformed, config)
            except Exception as e:
                logger.error(f"Transformation error {operation}: {e}")
                raise

        return transformed

    def _normalize(
        self,
        data: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Normalize data structure"""
        normalized = []

        for record in data:
            normalized_record = {}
            for key, value in record.items():
                # Convert to lowercase keys
                normalized_key = key.lower().replace(" ", "_")
                normalized_record[normalized_key] = value

            # Add processing metadata
            normalized_record["_processed_at"] = datetime.now().isoformat()
            normalized.append(normalized_record)

        return normalized

    def _aggregate(
        self,
        data: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Aggregate data"""
        # Group by key and aggregate
        group_key = config.get("group_by", "id")

        groups: Dict[str, List[Dict]] = {}
        for record in data:
            key = record.get(group_key, "default")
            if key not in groups:
                groups[key] = []
            groups[key].append(record)

        # Create aggregated records
        aggregated = []
        for key, records in groups.items():
            aggregated.append({
                group_key: key,
                "count": len(records),
                "records": records
            })

        return aggregated

    def _filter(
        self,
        data: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Filter data based on conditions"""
        filter_key = config.get("filter_key")
        filter_value = config.get("filter_value")

        if not filter_key:
            return data

        filtered = [
            record for record in data
            if record.get(filter_key) == filter_value
        ]

        return filtered

    def _enrich(
        self,
        data: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Enrich data with additional information"""
        enriched = []

        for record in data:
            enriched_record = record.copy()

            # Add derived fields
            enriched_record["_record_hash"] = self._compute_hash(record)
            enriched_record["_enriched_at"] = datetime.now().isoformat()

            # Add custom enrichments from config
            for key, value in config.get("add_fields", {}).items():
                enriched_record[key] = value

            enriched.append(enriched_record)

        return enriched

    def _deduplicate(
        self,
        data: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Remove duplicate records"""
        dedup_key = config.get("dedup_key", "_record_hash")

        seen = set()
        deduplicated = []

        for record in data:
            # Compute hash for deduplication
            if dedup_key == "_record_hash":
                key = self._compute_hash(record)
            else:
                key = record.get(dedup_key)

            if key not in seen:
                seen.add(key)
                deduplicated.append(record)

        return deduplicated

    def _hash_sensitive_data(
        self,
        data: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Hash sensitive fields"""
        sensitive_fields = config.get("sensitive_fields", [])

        hashed = []
        for record in data:
            hashed_record = record.copy()

            for field in sensitive_fields:
                if field in hashed_record:
                    value = str(hashed_record[field])
                    hashed_record[field] = hashlib.sha256(value.encode()).hexdigest()

            hashed.append(hashed_record)

        return hashed

    @staticmethod
    def _compute_hash(record: Dict[str, Any]) -> str:
        """Compute hash of record"""
        # Sort keys for consistent hashing
        record_str = json.dumps(record, sort_keys=True)
        return hashlib.md5(record_str.encode()).hexdigest()


class DataLoader:
    """Load data to destination"""

    def __init__(self):
        self.loaders: Dict[str, Callable] = {
            "database": self._load_to_database,
            "file": self._load_to_file,
            "warehouse": self._load_to_warehouse,
            "cache": self._load_to_cache,
        }

    def load(
        self,
        data: List[Dict[str, Any]],
        destination: str,
        config: Dict[str, Any],
        incremental: bool = True
    ) -> int:
        """Load data to destination"""

        if destination not in self.loaders:
            raise ValueError(f"Unsupported destination: {destination}")

        loader = self.loaders[destination]
        return loader(data, config, incremental)

    def _load_to_database(
        self,
        data: List[Dict[str, Any]],
        config: Dict[str, Any],
        incremental: bool
    ) -> int:
        """Load to database"""
        table = config.get("table", "etl_data")
        logger.info(f"Loading {len(data)} records to database table: {table}")

        # Placeholder: In production, use SQLAlchemy
        # For incremental, use UPSERT or INSERT ON CONFLICT

        return len(data)

    def _load_to_file(
        self,
        data: List[Dict[str, Any]],
        config: Dict[str, Any],
        incremental: bool
    ) -> int:
        """Load to file"""
        file_path = config.get("path", "etl_output.json")
        compress = config.get("compress", False)

        logger.info(f"Loading {len(data)} records to file: {file_path}")

        try:
            output_path = Path(file_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if compress:
                with gzip.open(f"{file_path}.gz", 'wt') as f:
                    json.dump(data, f, indent=2)
            else:
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)

            return len(data)
        except Exception as e:
            logger.error(f"File load error: {e}")
            raise

    def _load_to_warehouse(
        self,
        data: List[Dict[str, Any]],
        config: Dict[str, Any],
        incremental: bool
    ) -> int:
        """Load to data warehouse"""
        warehouse_type = config.get("type", "postgres")
        schema = config.get("schema", "public")
        table = config.get("table", "etl_data")

        logger.info(f"Loading {len(data)} records to warehouse: {warehouse_type}.{schema}.{table}")

        # Placeholder: In production, use warehouse-specific connectors
        # - Snowflake: snowflake-connector-python
        # - BigQuery: google-cloud-bigquery
        # - Redshift: psycopg2 with COPY command

        return len(data)

    def _load_to_cache(
        self,
        data: List[Dict[str, Any]],
        config: Dict[str, Any],
        incremental: bool
    ) -> int:
        """Load to cache"""
        cache_prefix = config.get("prefix", "etl")
        ttl = config.get("ttl", 3600)

        logger.info(f"Loading {len(data)} records to cache with prefix: {cache_prefix}")

        # Placeholder: In production, integrate with Task 10 cache

        return len(data)


class PipelineOrchestrator:
    """Orchestrate ETL pipeline execution"""

    def __init__(self):
        self.pipelines: Dict[str, PipelineConfig] = {}
        self.runs: Dict[str, PipelineRun] = {}
        self.extractor = DataExtractor()
        self.transformer = DataTransformer()
        self.loader = DataLoader()
        self.validator = DataValidator()
        self._lock = threading.Lock()

        # Add default validation rules
        self._setup_default_validators()

        logger.info("[ORFEAS PHASE 2 TASK 11] Pipeline orchestrator initialized")

    def _setup_default_validators(self):
        """Setup default validation rules"""
        self.validator.add_rule("not_empty", lambda x: len(x) > 0)
        self.validator.add_rule("is_dict", lambda x: isinstance(x, dict))
        self.validator.add_rule("has_id", lambda x: "id" in x or "_id" in x)

    def register_pipeline(self, config: PipelineConfig) -> None:
        """Register a new pipeline"""
        with self._lock:
            self.pipelines[config.pipeline_id] = config
            logger.info(f"Pipeline registered: {config.pipeline_id} - {config.name}")

    def execute_pipeline(
        self,
        pipeline_id: str,
        manual_trigger: bool = False
    ) -> PipelineRun:
        """Execute pipeline"""

        if pipeline_id not in self.pipelines:
            raise ValueError(f"Pipeline not found: {pipeline_id}")

        config = self.pipelines[pipeline_id]

        if not config.enabled and not manual_trigger:
            raise ValueError(f"Pipeline disabled: {pipeline_id}")

        # Create run
        run_id = f"{pipeline_id}_{int(time.time())}"
        run = PipelineRun(
            run_id=run_id,
            pipeline_id=pipeline_id,
            status=PipelineStatus.RUNNING,
            start_time=datetime.now()
        )

        with self._lock:
            self.runs[run_id] = run

        logger.info(f"Starting pipeline execution: {run_id}")

        try:
            # Execute pipeline stages
            self._execute_extract(run, config)
            self._execute_transform(run, config)
            self._execute_load(run, config)

            # Mark success
            run.status = PipelineStatus.SUCCESS
            run.end_time = datetime.now()

            # Calculate metrics
            duration = (run.end_time - run.start_time).total_seconds()
            run.metrics = {
                "duration_seconds": duration,
                "throughput_records_per_sec": run.records_loaded / duration if duration > 0 else 0,
                "success_rate": run.records_loaded / run.records_extracted if run.records_extracted > 0 else 0
            }

            logger.info(f"Pipeline completed successfully: {run_id} - {run.records_loaded} records in {duration:.2f}s")

        except Exception as e:
            run.status = PipelineStatus.FAILED
            run.end_time = datetime.now()
            run.error_message = str(e)
            logger.error(f"Pipeline failed: {run_id} - {e}")

            # Retry logic
            if run.retry_count < config.max_retries:
                run.retry_count += 1
                run.status = PipelineStatus.RETRYING
                logger.info(f"Retrying pipeline: {run_id} - Attempt {run.retry_count}/{config.max_retries}")
                time.sleep(config.retry_delay)
                return self.execute_pipeline(pipeline_id, manual_trigger=True)

        return run

    def _execute_extract(self, run: PipelineRun, config: PipelineConfig) -> None:
        """Execute extraction stage"""
        logger.info(f"[{run.run_id}] Extracting from {config.source_type.value}")

        data, checkpoint = self.extractor.extract(
            config.source_type,
            config.source_config,
            run.checkpoint
        )

        run.records_extracted = len(data)
        run.checkpoint = checkpoint
        run.metrics["extracted_data"] = data

        logger.info(f"[{run.run_id}] Extracted {len(data)} records")

    def _execute_transform(self, run: PipelineRun, config: PipelineConfig) -> None:
        """Execute transformation stage"""
        logger.info(f"[{run.run_id}] Transforming data with {len(config.transformations)} operations")

        data = run.metrics.get("extracted_data", [])

        # Validate input
        is_valid, errors = self.validator.validate(data, ["not_empty"])
        if not is_valid:
            raise ValueError(f"Input validation failed: {errors}")

        # Transform
        transformed = self.transformer.transform(
            data,
            config.transformations,
            config.metadata.get("transform_config", {})
        )

        run.records_transformed = len(transformed)
        run.metrics["transformed_data"] = transformed

        logger.info(f"[{run.run_id}] Transformed {len(transformed)} records")

    def _execute_load(self, run: PipelineRun, config: PipelineConfig) -> None:
        """Execute load stage"""
        logger.info(f"[{run.run_id}] Loading to {config.destination}")

        data = run.metrics.get("transformed_data", [])

        # Batch processing
        batch_size = config.batch_size
        total_loaded = 0

        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]

            loaded = self.loader.load(
                batch,
                config.destination,
                config.metadata.get("load_config", {}),
                config.incremental
            )

            total_loaded += loaded

            logger.info(f"[{run.run_id}] Loaded batch {i//batch_size + 1}: {loaded} records")

        run.records_loaded = total_loaded

        logger.info(f"[{run.run_id}] Total loaded: {total_loaded} records")

    def get_pipeline_status(self, pipeline_id: str) -> Dict[str, Any]:
        """Get pipeline status"""
        if pipeline_id not in self.pipelines:
            return {"error": "Pipeline not found"}

        config = self.pipelines[pipeline_id]

        # Get recent runs
        recent_runs = [
            run for run in self.runs.values()
            if run.pipeline_id == pipeline_id
        ]
        recent_runs.sort(key=lambda x: x.start_time, reverse=True)
        recent_runs = recent_runs[:10]  # Last 10 runs

        return {
            "pipeline_id": pipeline_id,
            "name": config.name,
            "enabled": config.enabled,
            "version": config.version,
            "recent_runs": [
                {
                    "run_id": run.run_id,
                    "status": run.status.value,
                    "start_time": run.start_time.isoformat(),
                    "end_time": run.end_time.isoformat() if run.end_time else None,
                    "records_loaded": run.records_loaded,
                    "metrics": run.metrics
                }
                for run in recent_runs
            ]
        }

    def list_pipelines(self) -> List[Dict[str, Any]]:
        """List all pipelines"""
        return [
            {
                "pipeline_id": config.pipeline_id,
                "name": config.name,
                "description": config.description,
                "source_type": config.source_type.value,
                "destination": config.destination,
                "enabled": config.enabled,
                "version": config.version
            }
            for config in self.pipelines.values()
        ]


# Global orchestrator instance
_orchestrator: Optional[PipelineOrchestrator] = None
_orchestrator_lock = threading.Lock()


def get_orchestrator() -> PipelineOrchestrator:
    """Get global orchestrator instance"""
    global _orchestrator

    if _orchestrator is None:
        with _orchestrator_lock:
            if _orchestrator is None:
                _orchestrator = PipelineOrchestrator()

    return _orchestrator

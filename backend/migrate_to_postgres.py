"""
Migration script: File-based job storage → PostgreSQL
Migrates existing job data from JSON files to PostgreSQL database

Usage:
    python migrate_to_postgres.py [--database-url URL] [--backup]

Options:
    --database-url URL : PostgreSQL connection URL
    --backup          : Create backup of files before migration
    --dry-run         : Test migration without committing changes
    --cleanup         : Remove old files after successful migration
"""

import os
import sys
import json
import shutil
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pg_queue import PostgresQueue, JobStatus

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JobMigrator:
    """Migrate jobs from file-based storage to PostgreSQL"""

    def __init__(
        self,
        jobs_dir: str = 'backend/outputs',
        database_url: str = None,
        backup: bool = False,
        dry_run: bool = False
    ):
        """
        Initialize migrator

        Args:
            jobs_dir: Directory containing job files
            database_url: PostgreSQL connection URL
            backup: Whether to create backup before migration
            dry_run: Test migration without committing
        """
        self.jobs_dir = Path(jobs_dir)
        self.dry_run = dry_run
        self.backup = backup

        # Initialize PostgreSQL queue
        self.pg_queue = PostgresQueue(database_url)

        # Statistics
        self.stats = {
            'total_files': 0,
            'migrated': 0,
            'skipped': 0,
            'failed': 0,
            'errors': []
        }

    def find_job_files(self) -> List[Path]:
        """
        Find all job JSON files

        Returns:
            List of job file paths
        """
        job_files = []

        # Find job_*.json files
        if self.jobs_dir.exists():
            job_files.extend(self.jobs_dir.glob('job_*.json'))
            job_files.extend(self.jobs_dir.glob('**/job_*.json'))

        logger.info(f"Found {len(job_files)} job files")
        return job_files

    def load_job_from_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Load job data from JSON file

        Args:
            file_path: Path to job JSON file

        Returns:
            Job data dictionary
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            raise

    def convert_status(self, old_status: str) -> str:
        """
        Convert old status format to new enum format

        Args:
            old_status: Old status string

        Returns:
            New status enum value
        """
        status_map = {
            'pending': 'queued',
            'queued': 'queued',
            'processing': 'processing',
            'completed': 'completed',
            'failed': 'failed',
            'error': 'failed',
            'cancelled': 'cancelled',
            'canceled': 'cancelled',
        }

        return status_map.get(old_status.lower(), 'queued')

    def migrate_job(self, job_data: Dict[str, Any]) -> bool:
        """
        Migrate single job to PostgreSQL

        Args:
            job_data: Job data from file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract job ID
            job_id = job_data.get('job_id') or job_data.get('id')
            if not job_id:
                logger.warning("Job missing ID, skipping")
                return False

            # Check if job already exists
            existing_job = self.pg_queue.get_job(job_id)
            if existing_job:
                logger.info(f"Job {job_id} already exists, skipping")
                self.stats['skipped'] += 1
                return True

            # Extract fields
            user_id = job_data.get('user_id', 'unknown')
            prompt = job_data.get('prompt')
            quality = job_data.get('quality', 7)
            parameters = job_data.get('parameters', {})
            status = self.convert_status(
                job_data.get('status', 'queued')
            )

            # Skip dry run database operations
            if self.dry_run:
                logger.info(
                    f"[DRY RUN] Would migrate job {job_id} "
                    f"(status: {status})"
                )
                self.stats['migrated'] += 1
                return True

            # Create job in PostgreSQL
            self.pg_queue.create_job(
                job_id=job_id,
                user_id=user_id,
                prompt=prompt,
                quality=quality,
                parameters=parameters
            )

            # Update status if not queued
            if status != 'queued':
                progress = job_data.get('progress', 0.0)
                stage = job_data.get('stage', 'unknown')
                error_msg = job_data.get('error_message') or job_data.get('error')

                self.pg_queue.update_job_status(
                    job_id=job_id,
                    status=status,
                    progress=progress,
                    stage=stage,
                    error_message=error_msg
                )

            # Update result if completed
            if status == 'completed':
                result_file = job_data.get('result_file') or job_data.get('output_file')
                result_metadata = job_data.get('result_metadata', {})
                gpu_time = job_data.get('gpu_time')

                if result_file:
                    self.pg_queue.complete_job(
                        job_id=job_id,
                        result_file=result_file,
                        result_metadata=result_metadata,
                        gpu_time=gpu_time
                    )

            logger.info(f"Migrated job {job_id} (status: {status})")
            self.stats['migrated'] += 1
            return True

        except Exception as e:
            logger.error(f"Failed to migrate job: {e}")
            self.stats['failed'] += 1
            self.stats['errors'].append(str(e))
            return False

    def create_backup(self):
        """Create backup of job files"""
        if not self.backup:
            return

        backup_dir = Path('backups') / f"jobs_backup_{datetime.now():%Y%m%d_%H%M%S}"
        backup_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Creating backup in {backup_dir}")

        # Copy all job files
        job_files = self.find_job_files()
        for job_file in job_files:
            try:
                shutil.copy2(job_file, backup_dir / job_file.name)
            except Exception as e:
                logger.warning(f"Failed to backup {job_file}: {e}")

        logger.info(f"Backup created: {len(list(backup_dir.glob('*.json')))} files")

    def migrate_all(self) -> Dict[str, Any]:
        """
        Migrate all jobs from files to PostgreSQL

        Returns:
            Migration statistics
        """
        logger.info("=" * 60)
        logger.info("ORFEAS AI - Job Migration: Files → PostgreSQL")
        logger.info("=" * 60)

        if self.dry_run:
            logger.warning("DRY RUN MODE - No changes will be committed")

        # Create backup if requested
        if self.backup:
            self.create_backup()

        # Find all job files
        job_files = self.find_job_files()
        self.stats['total_files'] = len(job_files)

        if not job_files:
            logger.warning("No job files found to migrate")
            return self.stats

        logger.info(f"Starting migration of {len(job_files)} jobs...")

        # Migrate each job
        for i, job_file in enumerate(job_files, 1):
            try:
                # Load job data
                job_data = self.load_job_from_file(job_file)

                # Migrate to PostgreSQL
                self.migrate_job(job_data)

                # Progress update every 10 jobs
                if i % 10 == 0:
                    logger.info(
                        f"Progress: {i}/{len(job_files)} "
                        f"({i*100//len(job_files)}%)"
                    )

            except Exception as e:
                logger.error(f"Error processing {job_file}: {e}")
                self.stats['failed'] += 1
                self.stats['errors'].append(f"{job_file.name}: {e}")

        # Print summary
        self.print_summary()

        return self.stats

    def print_summary(self):
        """Print migration summary"""
        logger.info("=" * 60)
        logger.info("MIGRATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total files:      {self.stats['total_files']}")
        logger.info(f"Migrated:         {self.stats['migrated']}")
        logger.info(f"Skipped:          {self.stats['skipped']}")
        logger.info(f"Failed:           {self.stats['failed']}")

        if self.stats['errors']:
            logger.error("\nErrors encountered:")
            for error in self.stats['errors'][:10]:  # Show first 10 errors
                logger.error(f"  - {error}")
            if len(self.stats['errors']) > 10:
                logger.error(f"  ... and {len(self.stats['errors']) - 10} more")

        # Success rate
        if self.stats['total_files'] > 0:
            success_rate = (
                self.stats['migrated'] / self.stats['total_files'] * 100
            )
            logger.info(f"\nSuccess rate: {success_rate:.1f}%")

        logger.info("=" * 60)

    def cleanup_old_files(self):
        """Remove old job files after successful migration"""
        logger.info("Cleaning up old job files...")

        job_files = self.find_job_files()
        removed = 0

        for job_file in job_files:
            try:
                job_data = self.load_job_from_file(job_file)
                job_id = job_data.get('job_id') or job_data.get('id')

                # Check if job exists in PostgreSQL
                if job_id and self.pg_queue.get_job(job_id):
                    job_file.unlink()
                    removed += 1
                    logger.debug(f"Removed {job_file}")
            except Exception as e:
                logger.warning(f"Failed to remove {job_file}: {e}")

        logger.info(f"Removed {removed} old job files")


def main():
    """Main migration entry point"""
    parser = argparse.ArgumentParser(
        description='Migrate ORFEAS AI jobs from files to PostgreSQL'
    )
    parser.add_argument(
        '--database-url',
        default=None,
        help='PostgreSQL connection URL'
    )
    parser.add_argument(
        '--jobs-dir',
        default='backend/outputs',
        help='Directory containing job files'
    )
    parser.add_argument(
        '--backup',
        action='store_true',
        help='Create backup before migration'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Test migration without committing changes'
    )
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Remove old files after successful migration'
    )

    args = parser.parse_args()

    # Create migrator
    migrator = JobMigrator(
        jobs_dir=args.jobs_dir,
        database_url=args.database_url,
        backup=args.backup,
        dry_run=args.dry_run
    )

    # Run migration
    stats = migrator.migrate_all()

    # Cleanup if requested and migration was successful
    if (args.cleanup and
        not args.dry_run and
        stats['failed'] == 0):
        migrator.cleanup_old_files()

    # Exit with error code if migration failed
    if stats['failed'] > 0:
        sys.exit(1)

    logger.info("Migration completed successfully!")


if __name__ == '__main__':
    main()

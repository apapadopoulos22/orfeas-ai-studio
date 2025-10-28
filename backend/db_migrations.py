"""
[ORFEAS PHASE 2 TASK 4] Database Migrations - Schema Version Control
Alembic migration management for database schema evolution.

Purpose:
  Version control for database schema changes
  Reversible migrations for safe deployments
  Track all schema modifications
  Enable rollback to previous versions

Usage:
  # Initialize migrations (one-time)
  alembic init migrations

  # Create migration after model changes
  alembic revision --autogenerate -m "Add user table"

  # Apply migrations
  alembic upgrade head

  # Downgrade to previous version
  alembic downgrade -1

  # Check migration status
  alembic current
  alembic history

Migration Files:
  migrations/
    ├── alembic.ini (configuration)
    ├── env.py (migration environment setup)
    ├── script.py.mako (migration template)
    └── versions/
        ├── 001_initial_schema.py
        ├── 002_add_analytics_events.py
        └── ...
"""

import os
import logging
from typing import Optional
from pathlib import Path

from alembic.config import Config
from alembic.command import (
    init, revision, upgrade, downgrade, current, history, branches
)
from alembic.util.exc import CommandError

logger = logging.getLogger(__name__)


class MigrationManager:
    """Manage database migrations using Alembic."""

    def __init__(self, db_url: str, migrations_dir: str = "migrations"):
        """Initialize migration manager.

        Args:
            db_url: SQLAlchemy database URL
            migrations_dir: Directory for migration files
        """
        self.db_url = db_url
        self.migrations_dir = migrations_dir
        self.config: Optional[Config] = None

        self._setup_config()

    def _setup_config(self) -> None:
        """Setup Alembic configuration."""
        try:
            config_path = Path(self.migrations_dir) / "alembic.ini"

            if not config_path.exists():
                logger.warning(f"[MIGRATION] Alembic config not found at {config_path}")
                return

            self.config = Config(str(config_path))
            self.config.set_main_option("sqlalchemy.url", self.db_url)

            logger.info("[MIGRATION] Alembic configuration loaded")

        except Exception as e:
            logger.error(f"[MIGRATION] Failed to setup config: {e}")

    def initialize(self) -> bool:
        """Initialize new migration repository.

        Returns:
            True if successful, False otherwise
        """
        try:
            if Path(self.migrations_dir).exists():
                logger.warning(f"[MIGRATION] Directory {self.migrations_dir} already exists")
                return False

            init(None, self.migrations_dir)
            logger.info(f"[MIGRATION] Initialized migration repository at {self.migrations_dir}")

            self._setup_config()
            return True

        except CommandError as e:
            logger.error(f"[MIGRATION] Initialization failed: {e}")
            return False

    def create_migration(self, message: str, autogenerate: bool = True) -> Optional[str]:
        """Create a new migration file.

        Args:
            message: Migration description
            autogenerate: Whether to auto-detect schema changes

        Returns:
            Migration version ID or None if failed
        """
        try:
            if self.config is None:
                logger.error("[MIGRATION] Alembic config not initialized")
                return None

            logger.info(f"[MIGRATION] Creating migration: {message}")

            if autogenerate:
                revision(self.config, message=message, autogenerate=True)
            else:
                revision(self.config, message=message)

            logger.info(f"[MIGRATION] Migration created successfully")
            return message

        except CommandError as e:
            logger.error(f"[MIGRATION] Migration creation failed: {e}")
            return None

    def upgrade(self, revision_id: str = "head") -> bool:
        """Apply migrations up to specified revision.

        Args:
            revision_id: Target revision (default: head for latest)

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.config is None:
                logger.error("[MIGRATION] Alembic config not initialized")
                return False

            logger.info(f"[MIGRATION] Upgrading database to {revision_id}")
            upgrade(self.config, revision_id)

            logger.info("[MIGRATION] Database upgraded successfully")
            return True

        except CommandError as e:
            logger.error(f"[MIGRATION] Upgrade failed: {e}")
            return False

    def downgrade(self, revision_id: str) -> bool:
        """Downgrade database to specified revision.

        Args:
            revision_id: Target revision or relative (-1 for previous)

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.config is None:
                logger.error("[MIGRATION] Alembic config not initialized")
                return False

            logger.info(f"[MIGRATION] Downgrading database to {revision_id}")
            downgrade(self.config, revision_id)

            logger.info("[MIGRATION] Database downgraded successfully")
            return True

        except CommandError as e:
            logger.error(f"[MIGRATION] Downgrade failed: {e}")
            return False

    def get_current_revision(self) -> Optional[str]:
        """Get current database revision.

        Returns:
            Current revision ID or None if not initialized
        """
        try:
            if self.config is None:
                return None

            current(self.config)
            return "See alembic output above"

        except CommandError as e:
            logger.error(f"[MIGRATION] Failed to get current revision: {e}")
            return None

    def get_history(self, verbose: bool = False) -> str:
        """Get migration history.

        Args:
            verbose: Whether to show verbose output

        Returns:
            History output string
        """
        try:
            if self.config is None:
                return "Config not initialized"

            history(self.config, verbose=verbose)
            return "See history output above"

        except CommandError as e:
            logger.error(f"[MIGRATION] Failed to get history: {e}")
            return str(e)

    def get_branches(self) -> str:
        """Get migration branches.

        Returns:
            Branches output string
        """
        try:
            if self.config is None:
                return "Config not initialized"

            branches(self.config)
            return "See branches output above"

        except CommandError as e:
            logger.error(f"[MIGRATION] Failed to get branches: {e}")
            return str(e)


# Template for initial migration
INITIAL_MIGRATION_TEMPLATE = '''"""Initial database schema

Revision ID: 001_initial_schema
Revises:
Create Date: {datetime}

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial database tables."""

    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username', name='unique_username'),
        sa.UniqueConstraint('email', name='unique_email'),
    )
    op.create_index('idx_user_email', 'users', ['email'])
    op.create_index('idx_user_created', 'users', ['created_at'])

    # Projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), default='active', nullable=False),
        sa.Column('metadata', sa.JSON(), default={{}}, nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    )
    op.create_index('idx_project_user', 'projects', ['user_id'])
    op.create_index('idx_project_status', 'projects', ['status'])
    op.create_index('idx_project_created', 'projects', ['created_at'])

    # ModelVersions table
    op.create_table(
        'model_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('version', sa.String(50), nullable=False),
        sa.Column('model_type', sa.String(50), nullable=False),
        sa.Column('path', sa.String(1000), nullable=False),
        sa.Column('accuracy', sa.Float(), nullable=True),
        sa.Column('f1_score', sa.Float(), nullable=True),
        sa.Column('config', sa.JSON(), default={{}}, nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=False, nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'version', name='unique_model_version'),
    )
    op.create_index('idx_model_name_version', 'model_versions', ['name', 'version'])
    op.create_index('idx_model_active', 'model_versions', ['is_active'])
    op.create_index('idx_model_created', 'model_versions', ['created_at'])

    # Jobs table
    op.create_table(
        'jobs',
        sa.Column('id', sa.String(50), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('model_version_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(20), default='pending', nullable=False),
        sa.Column('priority', sa.Integer(), default=0, nullable=False),
        sa.Column('progress', sa.Float(), default=0.0, nullable=False),
        sa.Column('input_data', sa.JSON(), nullable=False),
        sa.Column('output_data', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('execution_time_ms', sa.Float(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.ForeignKeyConstraint(['model_version_id'], ['model_versions.id']),
    )
    op.create_index('idx_job_project', 'jobs', ['project_id'])
    op.create_index('idx_job_status', 'jobs', ['status'])
    op.create_index('idx_job_created', 'jobs', ['created_at'])
    op.create_index('idx_job_priority_status', 'jobs', ['priority', 'status'])

    # Results table
    op.create_table(
        'results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.String(50), nullable=False),
        sa.Column('result_type', sa.String(50), nullable=False),
        sa.Column('data', sa.JSON(), nullable=False),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('file_path', sa.String(1000), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id']),
    )
    op.create_index('idx_result_job', 'results', ['job_id'])
    op.create_index('idx_result_type', 'results', ['result_type'])

    # CacheEntries table
    op.create_table(
        'cache_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(500), nullable=False),
        sa.Column('value', sa.JSON(), nullable=False),
        sa.Column('ttl_seconds', sa.Integer(), default=3600, nullable=False),
        sa.Column('hits', sa.Integer(), default=0, nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key', name='unique_cache_key'),
    )
    op.create_index('idx_cache_key', 'cache_entries', ['key'])
    op.create_index('idx_cache_expires', 'cache_entries', ['expires_at'])

    # AnalyticsEvents table
    op.create_table(
        'analytics_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.String(50), nullable=True),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('event_name', sa.String(255), nullable=False),
        sa.Column('value', sa.Float(), nullable=True),
        sa.Column('metadata', sa.JSON(), default={{}}, nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id']),
    )
    op.create_index('idx_event_type', 'analytics_events', ['event_type'])
    op.create_index('idx_event_created', 'analytics_events', ['created_at'])
    op.create_index('idx_event_job', 'analytics_events', ['job_id'])


def downgrade() -> None:
    """Drop all tables (initial migration)."""
    op.drop_table('analytics_events')
    op.drop_table('cache_entries')
    op.drop_table('results')
    op.drop_table('jobs')
    op.drop_table('model_versions')
    op.drop_table('projects')
    op.drop_table('users')
'''


def create_migration_manager(db_url: str) -> MigrationManager:
    """Create migration manager instance.

    Args:
        db_url: SQLAlchemy database URL

    Returns:
        Configured MigrationManager instance
    """
    return MigrationManager(db_url)

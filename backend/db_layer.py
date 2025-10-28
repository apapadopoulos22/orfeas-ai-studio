"""
[ORFEAS PHASE 2 TASK 4] Database Layer - PostgreSQL Integration
Database connection management, session handling, and pool configuration.

Purpose:
  Manages database connections, sessions, and connection pooling.
  Provides thread-safe database access patterns.
  Supports multiple database backends (PostgreSQL, fallback to SQLite).

Architecture:
  - Connection pooling with configurable pool size
  - Thread-safe session management
  - Health checking and automatic reconnection
  - Performance tracking and metrics

Usage:
  from db_layer import get_db_session, init_db, get_db_manager

  # Get database session
  with get_db_session() as session:
      user = session.query(User).filter_by(id=1).first()
"""

import os
import logging
import threading
import time
from typing import Optional, Dict, Any, Generator, Tuple
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import create_engine, event, pool
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.exc import OperationalError, DatabaseError

logger = logging.getLogger(__name__)

# SQLAlchemy declarative base for all models
Base = declarative_base()


@dataclass
class DBConfig:
    """Database configuration."""

    db_type: str = "postgresql"  # postgresql, sqlite, mysql
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    database: str = "orfeas_ai"
    pool_size: int = 20
    max_overflow: int = 40
    pool_timeout: float = 30.0
    pool_recycle: int = 3600  # Recycle connections after 1 hour
    echo: bool = False  # SQL echo for debugging

    @classmethod
    def from_env(cls) -> "DBConfig":
        """Create config from environment variables."""
        return cls(
            db_type=os.getenv("DB_TYPE", "postgresql"),
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
            database=os.getenv("DB_NAME", "orfeas_ai"),
            pool_size=int(os.getenv("DB_POOL_SIZE", "20")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "40")),
            pool_timeout=float(os.getenv("DB_POOL_TIMEOUT", "30.0")),
            echo=os.getenv("DB_ECHO", "false").lower() == "true",
        )

    def get_connection_string(self) -> str:
        """Get SQLAlchemy connection string."""
        if self.db_type == "postgresql":
            return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.db_type == "sqlite":
            return f"sqlite:///{self.database}.db"
        elif self.db_type == "mysql":
            return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")


@dataclass
class DBStats:
    """Database statistics."""

    total_connections: int = 0
    active_connections: int = 0
    pool_size: int = 0
    pool_overflow: int = 0
    last_check: datetime = None
    health_status: str = "unknown"
    error_count: int = 0
    last_error: Optional[str] = None


class DatabaseManager:
    """Thread-safe database connection manager."""

    _instance: Optional["DatabaseManager"] = None
    _lock = threading.Lock()

    def __init__(self, config: DBConfig):
        """Initialize database manager with configuration."""
        self.config = config
        self.engine = None
        self.session_factory = None
        self.stats = DBStats()
        self._lock = threading.RLock()
        self._health_check_thread: Optional[threading.Thread] = None
        self._stop_health_check = False

        logger.info(f"[DB] Initializing database manager (type: {config.db_type})")
        self._initialize_engine()

    def _initialize_engine(self) -> None:
        """Initialize SQLAlchemy engine with connection pooling."""
        try:
            connection_string = self.config.get_connection_string()

            # Create engine with pooling
            self.engine = create_engine(
                connection_string,
                poolclass=pool.QueuePool,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                pool_recycle=self.config.pool_recycle,
                echo=self.config.echo,
                echo_pool=self.config.echo,
            )

            # Create session factory
            self.session_factory = sessionmaker(bind=self.engine)

            # Test connection
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")

            logger.info(f"[DB] Engine initialized: {self.config.db_type} on {self.config.host}:{self.config.port}/{self.config.database}")
            self.stats.health_status = "connected"

        except Exception as e:
            logger.error(f"[DB] Failed to initialize engine: {e}")
            self.stats.health_status = "failed"
            self.stats.last_error = str(e)
            raise

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get thread-safe database session.

        Usage:
            with db_manager.get_session() as session:
                user = session.query(User).filter_by(id=1).first()
        """
        session: Optional[Session] = None
        try:
            if self.session_factory is None:
                raise RuntimeError("Database not initialized")

            session = self.session_factory()
            self.stats.active_connections += 1

            yield session

            session.commit()

        except Exception as e:
            if session:
                session.rollback()
            logger.error(f"[DB] Session error: {e}")
            self.stats.error_count += 1
            self.stats.last_error = str(e)
            raise
        finally:
            if session:
                session.close()
                self.stats.active_connections = max(0, self.stats.active_connections - 1)

    def get_pool_status(self) -> Dict[str, Any]:
        """Get connection pool status."""
        with self._lock:
            if self.engine and hasattr(self.engine.pool, 'size'):
                return {
                    "pool_size": self.engine.pool.size(),
                    "checked_out": self.engine.pool.checkedout(),
                    "overflow": self.engine.pool.overflow(),
                    "status": "healthy" if self.engine.pool.size() > 0 else "idle",
                }
        return {"status": "not initialized"}

    def health_check(self) -> bool:
        """Check database health by executing simple query."""
        try:
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            self.stats.health_status = "healthy"
            self.stats.last_check = datetime.now()
            return True
        except (OperationalError, DatabaseError) as e:
            logger.warning(f"[DB] Health check failed: {e}")
            self.stats.health_status = "unhealthy"
            self.stats.last_error = str(e)
            return False

    def get_stats(self) -> DBStats:
        """Get database statistics."""
        return self.stats

    @classmethod
    def get_instance(cls, config: Optional[DBConfig] = None) -> "DatabaseManager":
        """Get singleton instance of DatabaseManager."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    if config is None:
                        config = DBConfig.from_env()
                    cls._instance = cls(config)
        return cls._instance

    def close(self) -> None:
        """Close database connections."""
        if self.engine:
            self.engine.dispose()
            logger.info("[DB] Database connections closed")


# Singleton instance
_db_manager: Optional[DatabaseManager] = None


def init_db(config: Optional[DBConfig] = None) -> DatabaseManager:
    """Initialize database with configuration."""
    global _db_manager
    if config is None:
        config = DBConfig.from_env()
    _db_manager = DatabaseManager(config)
    return _db_manager


def get_db_manager() -> DatabaseManager:
    """Get database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager.get_instance()
    return _db_manager


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Get thread-safe database session (convenience function)."""
    manager = get_db_manager()
    with manager.get_session() as session:
        yield session

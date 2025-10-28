"""
[ORFEAS PHASE 2 TASK 4] Database Models - ORM Schema Definition
Defines SQLAlchemy ORM models for all core entities.

Purpose:
  Define database tables using SQLAlchemy ORM.
  Relationship mappings between entities.
  Type hints and validation.
  Integration with existing Task 1, 2, 3 systems.

Schema:
  Users (future Task 7 auth) → Projects → Jobs → Results
  Jobs → ModelVersions (Task 1)
  Results → CacheEntries (Task 2)
  Jobs → AnalyticsEvents (Task 3)

Performance:
  Proper indexing for common queries
  Lazy-loaded relationships to reduce memory
  Timestamps for data tracking
"""

import json
from datetime import datetime
from enum import Enum
from typing import Optional, Any, List

from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Boolean,
    ForeignKey, JSON, Text, Index, UniqueConstraint,
    Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from db_layer import Base


# Enums
class JobStatus(str, Enum):
    """Job execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ModelType(str, Enum):
    """Machine learning model types."""
    CLASSIFICATION = "classification"
    GENERATION = "generation"
    REGRESSION = "regression"


class ProjectStatus(str, Enum):
    """Project status."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


# Models
class User(Base):
    """User account (prepared for Task 7 authentication)."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    projects = relationship("Project", back_populates="user", lazy="select")

    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_created', 'created_at'),
    )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
        }


class Project(Base):
    """Project container for jobs and results."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.ACTIVE, nullable=False)
    metadata = Column(JSON, default={}, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="projects")
    jobs = relationship("Job", back_populates="project", lazy="select", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_project_user', 'user_id'),
        Index('idx_project_status', 'status'),
        Index('idx_project_created', 'created_at'),
    )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'status': self.status.value if self.status else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class ModelVersion(Base):
    """Machine learning model versions (Task 1 integration)."""

    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    version = Column(String(50), nullable=False)
    model_type = Column(SQLEnum(ModelType), nullable=False)
    path = Column(String(1000), nullable=False)
    accuracy = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    config = Column(JSON, default={}, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)

    # Relationships
    jobs = relationship("Job", back_populates="model_version", lazy="select")

    __table_args__ = (
        Index('idx_model_name_version', 'name', 'version'),
        Index('idx_model_active', 'is_active'),
        Index('idx_model_created', 'created_at'),
        UniqueConstraint('name', 'version', name='unique_model_version'),
    )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'model_type': self.model_type.value if self.model_type else None,
            'accuracy': self.accuracy,
            'f1_score': self.f1_score,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Job(Base):
    """Job execution record (main processing unit)."""

    __tablename__ = "jobs"

    id = Column(String(50), primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False, index=True)
    model_version_id = Column(Integer, ForeignKey('model_versions.id'), nullable=True)
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, nullable=False)
    priority = Column(Integer, default=0, nullable=False)
    progress = Column(Float, default=0.0, nullable=False)
    input_data = Column(JSON, nullable=False)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    execution_time_ms = Column(Float, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="jobs")
    model_version = relationship("ModelVersion", back_populates="jobs")
    results = relationship("Result", back_populates="job", lazy="select", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_job_project', 'project_id'),
        Index('idx_job_status', 'status'),
        Index('idx_job_created', 'created_at'),
        Index('idx_job_priority_status', 'priority', 'status'),
    )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'project_id': self.project_id,
            'status': self.status.value if self.status else None,
            'progress': self.progress,
            'execution_time_ms': self.execution_time_ms,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Result(Base):
    """Job result and output."""

    __tablename__ = "results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(50), ForeignKey('jobs.id'), nullable=False, index=True)
    result_type = Column(String(50), nullable=False)
    data = Column(JSON, nullable=False)
    quality_score = Column(Float, nullable=True)
    file_path = Column(String(1000), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    job = relationship("Job", back_populates="results")

    __table_args__ = (
        Index('idx_result_job', 'job_id'),
        Index('idx_result_type', 'result_type'),
    )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'job_id': self.job_id,
            'result_type': self.result_type,
            'quality_score': self.quality_score,
            'file_path': self.file_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class CacheEntry(Base):
    """Cache entries for query optimization (Task 2 integration)."""

    __tablename__ = "cache_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(500), unique=True, nullable=False, index=True)
    value = Column(JSON, nullable=False)
    ttl_seconds = Column(Integer, default=3600, nullable=False)
    hits = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index('idx_cache_key', 'key'),
        Index('idx_cache_expires', 'expires_at'),
    )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'key': self.key,
            'hits': self.hits,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class AnalyticsEvent(Base):
    """Analytics event records (Task 3 integration)."""

    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(50), ForeignKey('jobs.id'), nullable=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    event_name = Column(String(255), nullable=False)
    value = Column(Float, nullable=True)
    metadata = Column(JSON, default={}, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)

    __table_args__ = (
        Index('idx_event_type', 'event_type'),
        Index('idx_event_created', 'created_at'),
        Index('idx_event_job', 'job_id'),
    )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'job_id': self.job_id,
            'event_type': self.event_type,
            'event_name': self.event_name,
            'value': self.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

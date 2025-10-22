"""
ORFEAS Progress Tracker
========================
Calculates and tracks progress for 3D generation jobs

Features:
- Stage-based progress calculation
- ETA estimation based on historical data
- Progress smoothing for better UX
- Multi-stage pipeline support
- Configurable stage weights
- Prometheus metrics integration (Phase 2.5)

ORFEAS AI Project
"""

import logging
import time
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import threading

# Import Prometheus metrics tracking
from prometheus_metrics import track_pipeline_stage, track_pipeline_stage_error

logger = logging.getLogger(__name__)


@dataclass
class StageInfo:
    """Information about a pipeline stage"""
    name: str
    weight: float  # Relative weight (0-1)
    estimated_duration: float  # Seconds
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0  # 0-100

    @property
    def duration(self) -> Optional[float]:
        """Get actual duration if completed"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def elapsed(self) -> float:
        """Get elapsed time for current stage"""
        if self.started_at:
            end_time = self.completed_at or datetime.now()
            return (end_time - self.started_at).total_seconds()
        return 0.0


@dataclass
class JobProgress:
    """Tracks progress for a single job"""
    job_id: str
    started_at: datetime
    stages: Dict[str, StageInfo] = field(default_factory=dict)
    current_stage: Optional[str] = None
    overall_progress: float = 0.0  # 0-100
    eta_seconds: Optional[float] = None
    completed: bool = False
    success: Optional[bool] = None

    def get_elapsed_time(self) -> float:
        """Get total elapsed time"""
        return (datetime.now() - self.started_at).total_seconds()


class ProgressTracker:
    """
    Tracks progress for 3D generation jobs

    Default pipeline stages with weights:
    - image_loading (1%): Very fast
    - image_preprocessing (4%): Background removal
    - shape_generation (70%): Most time-consuming
    - texture_synthesis (20%): Texture application
    - mesh_export (5%): File writing
    """

    # Default stage configuration based on baseline profiling
    DEFAULT_STAGES = {
        'image_loading': {'weight': 0.01, 'estimated_duration': 0.5},
        'image_preprocessing': {'weight': 0.04, 'estimated_duration': 2.0},
        'shape_generation': {'weight': 0.70, 'estimated_duration': 60.0},  # 70% of time
        'texture_synthesis': {'weight': 0.20, 'estimated_duration': 15.0},
        'mesh_export': {'weight': 0.05, 'estimated_duration': 3.0}
    }

    def __init__(self, websocket_manager=None):
        """
        Initialize progress tracker

        Args:
            websocket_manager: Optional WebSocketManager for real-time updates
        """
        self.ws_manager = websocket_manager
        self.jobs: Dict[str, JobProgress] = {}
        self._lock = threading.Lock()

        # Historical data for ETA calculation
        self.stage_durations: Dict[str, List[float]] = {
            stage: [] for stage in self.DEFAULT_STAGES.keys()
        }

        logger.info("[ORFEAS] Progress Tracker initialized")

    def start_job(self, job_id: str, stages: Optional[Dict[str, Dict]] = None):
        """
        Start tracking a new job

        Args:
            job_id: Job identifier
            stages: Optional custom stage configuration
        """
        with self._lock:
            stage_config = stages or self.DEFAULT_STAGES

            job_stages = {}
            for name, config in stage_config.items():
                job_stages[name] = StageInfo(
                    name=name,
                    weight=config['weight'],
                    estimated_duration=config['estimated_duration']
                )

            self.jobs[job_id] = JobProgress(
                job_id=job_id,
                started_at=datetime.now(),
                stages=job_stages
            )

            logger.info(f"[ORFEAS] Started tracking job {job_id} with {len(job_stages)} stages")

    def start_stage(self, job_id: str, stage_name: str):
        """
        Mark a stage as started

        Args:
            job_id: Job identifier
            stage_name: Name of stage
        """
        with self._lock:
            if job_id not in self.jobs:
                logger.warning(f"[ORFEAS] Job {job_id} not found, cannot start stage {stage_name}")
                return

            job = self.jobs[job_id]

            if stage_name not in job.stages:
                logger.warning(f"[ORFEAS] Stage {stage_name} not configured for job {job_id}")
                return

            stage = job.stages[stage_name]
            stage.started_at = datetime.now()
            job.current_stage = stage_name

            logger.info(f"[ORFEAS] Job {job_id} started stage: {stage_name}")

            # Emit WebSocket event
            if self.ws_manager:
                self.ws_manager.emit_stage_change(job_id, stage_name)

    def update_stage_progress(self, job_id: str, stage_name: str, progress: float):
        """
        Update progress within a stage

        Args:
            job_id: Job identifier
            stage_name: Name of stage
            progress: Progress within stage (0-100)
        """
        with self._lock:
            if job_id not in self.jobs:
                return

            job = self.jobs[job_id]

            if stage_name not in job.stages:
                return

            stage = job.stages[stage_name]
            stage.progress = max(0, min(100, progress))

            # Calculate overall progress
            self._calculate_overall_progress(job)

            # Calculate ETA
            self._calculate_eta(job)

            # Emit WebSocket event
            if self.ws_manager:
                self.ws_manager.emit_progress(job_id, {
                    'progress': job.overall_progress,
                    'stage': stage_name,
                    'stage_progress': stage.progress,
                    'eta_seconds': job.eta_seconds
                })

    def complete_stage(self, job_id: str, stage_name: str):
        """
        Mark a stage as completed

        Args:
            job_id: Job identifier
            stage_name: Name of stage
        """
        with self._lock:
            if job_id not in self.jobs:
                return

            job = self.jobs[job_id]

            if stage_name not in job.stages:
                return

            stage = job.stages[stage_name]
            stage.completed_at = datetime.now()
            stage.progress = 100.0

            # Record duration for future ETA calculations
            if stage.duration:
                self.stage_durations[stage_name].append(stage.duration)
                # Keep last 100 samples
                if len(self.stage_durations[stage_name]) > 100:
                    self.stage_durations[stage_name].pop(0)

                # Track pipeline stage metrics in Prometheus
                track_pipeline_stage(stage_name, stage.duration)

            logger.info(f"[ORFEAS] Job {job_id} completed stage: {stage_name} ({stage.duration:.2f}s)")

            # Calculate overall progress
            self._calculate_overall_progress(job)

    def complete_job(self, job_id: str, success: bool):
        """
        Mark job as completed

        Args:
            job_id: Job identifier
            success: Whether job completed successfully
        """
        with self._lock:
            if job_id not in self.jobs:
                return

            job = self.jobs[job_id]
            job.completed = True
            job.success = success
            job.overall_progress = 100.0

            total_duration = job.get_elapsed_time()

            logger.info(f"[ORFEAS] Job {job_id} completed: {'success' if success else 'failure'} "
                       f"(total: {total_duration:.2f}s)")

            # Emit WebSocket event
            if self.ws_manager:
                self.ws_manager.emit_completion(job_id, success, {
                    'duration': total_duration,
                    'stages': {name: stage.duration for name, stage in job.stages.items() if stage.duration}
                })

    def _calculate_overall_progress(self, job: JobProgress):
        """Calculate overall job progress based on stage weights"""
        total_progress = 0.0

        for stage in job.stages.values():
            # Completed stages contribute full weight
            if stage.completed_at:
                total_progress += stage.weight * 100
            # Current stage contributes partial weight
            elif stage.started_at:
                total_progress += stage.weight * stage.progress

        job.overall_progress = min(100.0, total_progress)

    def _calculate_eta(self, job: JobProgress):
        """Calculate estimated time to completion"""
        if not job.current_stage:
            job.eta_seconds = None
            return

        # Calculate time remaining for current stage
        current_stage = job.stages[job.current_stage]

        if current_stage.progress > 0:
            # Estimate based on current progress rate
            elapsed = current_stage.elapsed
            estimated_total = elapsed / (current_stage.progress / 100)
            remaining_in_stage = max(0, estimated_total - elapsed)
        else:
            # Use estimated duration
            remaining_in_stage = current_stage.estimated_duration

        # Calculate time for remaining stages
        remaining_stages = 0.0
        found_current = False

        for stage_name, stage in job.stages.items():
            if stage_name == job.current_stage:
                found_current = True
                continue

            if found_current and not stage.started_at:
                # Use historical average if available
                if self.stage_durations[stage_name]:
                    avg_duration = sum(self.stage_durations[stage_name]) / len(self.stage_durations[stage_name])
                    remaining_stages += avg_duration
                else:
                    remaining_stages += stage.estimated_duration

        job.eta_seconds = remaining_in_stage + remaining_stages

    def get_progress(self, job_id: str) -> Optional[Dict]:
        """
        Get current progress for a job

        Args:
            job_id: Job identifier

        Returns:
            Progress data or None if job not found
        """
        with self._lock:
            if job_id not in self.jobs:
                return None

            job = self.jobs[job_id]

            return {
                'job_id': job_id,
                'overall_progress': job.overall_progress,
                'current_stage': job.current_stage,
                'stage_progress': job.stages[job.current_stage].progress if job.current_stage else 0,
                'eta_seconds': job.eta_seconds,
                'elapsed_seconds': job.get_elapsed_time(),
                'completed': job.completed,
                'success': job.success
            }

    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """
        Remove old completed jobs from tracking

        Args:
            max_age_hours: Maximum age in hours before cleanup
        """
        with self._lock:
            cutoff = datetime.now() - timedelta(hours=max_age_hours)

            old_jobs = []
            for job_id, job in self.jobs.items():
                if job.completed and job.started_at < cutoff:
                    old_jobs.append(job_id)

            for job_id in old_jobs:
                del self.jobs[job_id]

            if old_jobs:
                logger.info(f"[ORFEAS] Cleaned up {len(old_jobs)} old jobs")


# Singleton instance
_progress_tracker: Optional[ProgressTracker] = None
_tracker_lock = threading.Lock()


def initialize_progress_tracker(websocket_manager=None) -> ProgressTracker:
    """
    Initialize progress tracker singleton

    Args:
        websocket_manager: Optional WebSocketManager instance

    Returns:
        ProgressTracker instance
    """
    global _progress_tracker

    with _tracker_lock:
        if _progress_tracker is None:
            _progress_tracker = ProgressTracker(websocket_manager)
            logger.info("[ORFEAS] Progress Tracker singleton initialized")

        return _progress_tracker


def get_progress_tracker() -> Optional[ProgressTracker]:
    """
    Get progress tracker singleton

    Returns:
        ProgressTracker instance or None if not initialized
    """
    return _progress_tracker

"""
WebSocket Configuration for ORFEAS AI Studio
Real-time progress tracking and job status updates via Socket.IO

Features:
  - Real-time progress events (0-100% with stage info)
  - Live job status updates (pending/processing/complete/error)
  - Error notifications with details
  - Client subscription management (room-based)
  - Heartbeat/ping-pong for connection health
  - Graceful disconnection handling
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms

logger = logging.getLogger(__name__)

# Global storage for active jobs and connections
ACTIVE_JOBS: Dict[str, Dict[str, Any]] = {}
CLIENT_SUBSCRIPTIONS: Dict[str, List[str]] = {}  # client_id -> [job_ids]


class WebSocketManager:
    """Manages Socket.IO connections and real-time updates"""

    def __init__(self, socketio: SocketIO):
        """Initialize WebSocket manager with Flask-SocketIO instance"""
        self.socketio = socketio
        self._register_handlers()
        logger.info("[WEBSOCKET] Manager initialized")

    def _register_handlers(self):
        """Register all Socket.IO event handlers"""

        @self.socketio.on('connect')
        def on_connect(auth):
            """Handle client connection"""
            client_id = auth.get('client_id', 'anonymous') if auth else 'anonymous'
            logger.info(f"[WEBSOCKET] Client connected: {client_id}")
            emit('connection_established', {
                'status': 'connected',
                'timestamp': datetime.utcnow().isoformat(),
                'message': 'WebSocket connection established'
            })

        @self.socketio.on('disconnect')
        def on_disconnect():
            """Handle client disconnection"""
            logger.info(f"[WEBSOCKET] Client disconnected")

        @self.socketio.on('subscribe_to_job')
        def on_subscribe_to_job(data):
            """Subscribe client to job updates (joins Socket.IO room)"""
            job_id = data.get('job_id')
            if not job_id:
                emit('error', {'message': 'job_id required'})
                return

            join_room(job_id)
            logger.info(f"[WEBSOCKET] Client subscribed to job: {job_id}")
            emit('subscribed_to_job', {
                'job_id': job_id,
                'status': 'subscribed',
                'timestamp': datetime.utcnow().isoformat()
            })

        @self.socketio.on('unsubscribe_from_job')
        def on_unsubscribe_from_job(data):
            """Unsubscribe client from job updates (leaves Socket.IO room)"""
            job_id = data.get('job_id')
            if not job_id:
                emit('error', {'message': 'job_id required'})
                return

            leave_room(job_id)
            logger.info(f"[WEBSOCKET] Client unsubscribed from job: {job_id}")
            emit('unsubscribed_from_job', {
                'job_id': job_id,
                'status': 'unsubscribed',
                'timestamp': datetime.utcnow().isoformat()
            })

        @self.socketio.on('heartbeat')
        def on_heartbeat(data):
            """Respond to heartbeat ping (connection health check)"""
            emit('heartbeat_ack', {
                'timestamp': datetime.utcnow().isoformat(),
                'active_jobs': len(ACTIVE_JOBS)
            })

    def create_job(self, job_id: str, job_type: str, metadata: Dict[str, Any] = None):
        """Create a new job tracking entry"""
        ACTIVE_JOBS[job_id] = {
            'id': job_id,
            'type': job_type,
            'status': 'pending',
            'progress': 0,
            'stage': 'initialization',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'metadata': metadata or {},
            'events': []
        }
        logger.info(f"[JOB] Created: {job_id} (type: {job_type})")

    def update_job_progress(self, job_id: str, progress: int, stage: str,
                            stage_progress: int = None, eta_seconds: int = None):
        """Emit progress update for a job"""
        if job_id not in ACTIVE_JOBS:
            logger.warning(f"[JOB] Job not found: {job_id}")
            return

        job = ACTIVE_JOBS[job_id]
        job['progress'] = min(100, max(0, progress))
        job['stage'] = stage
        job['status'] = 'processing'
        job['updated_at'] = datetime.utcnow().isoformat()

        progress_data = {
            'job_id': job_id,
            'progress': job['progress'],
            'stage': stage,
            'stage_progress': stage_progress,
            'eta_seconds': eta_seconds,
            'timestamp': job['updated_at']
        }

        self.socketio.emit('generation_progress', progress_data, room=job_id)
        job['events'].append(('progress', progress_data))
        logger.debug(f"[JOB {job_id}] Progress: {job['progress']}% | Stage: {stage}")

    def complete_job(self, job_id: str, result: Dict[str, Any] = None):
        """Mark job as complete and emit completion event"""
        if job_id not in ACTIVE_JOBS:
            logger.warning(f"[JOB] Job not found: {job_id}")
            return

        job = ACTIVE_JOBS[job_id]
        job['status'] = 'complete'
        job['progress'] = 100
        job['updated_at'] = datetime.utcnow().isoformat()

        completion_data = {
            'job_id': job_id,
            'status': 'complete',
            'progress': 100,
            'result': result or {},
            'timestamp': job['updated_at']
        }

        self.socketio.emit('generation_complete', completion_data, room=job_id)
        job['events'].append(('complete', completion_data))
        logger.info(f"[JOB] Completed: {job_id}")

    def error_job(self, job_id: str, error_message: str, error_code: str = 'UNKNOWN'):
        """Mark job as errored and emit error event"""
        if job_id not in ACTIVE_JOBS:
            logger.warning(f"[JOB] Job not found: {job_id}")
            return

        job = ACTIVE_JOBS[job_id]
        job['status'] = 'error'
        job['updated_at'] = datetime.utcnow().isoformat()

        error_data = {
            'job_id': job_id,
            'status': 'error',
            'error_message': error_message,
            'error_code': error_code,
            'timestamp': job['updated_at']
        }

        self.socketio.emit('generation_error', error_data, room=job_id)
        job['events'].append(('error', error_data))
        logger.error(f"[JOB] Error in {job_id}: {error_message} ({error_code})")

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get current job status"""
        if job_id not in ACTIVE_JOBS:
            return {'error': f'Job {job_id} not found', 'status': 'not_found'}

        return ACTIVE_JOBS[job_id]

    def get_active_jobs(self) -> List[Dict[str, Any]]:
        """Get all active jobs"""
        return list(ACTIVE_JOBS.values())

    def cleanup_job(self, job_id: str):
        """Remove job from tracking (after archival)"""
        if job_id in ACTIVE_JOBS:
            del ACTIVE_JOBS[job_id]
            logger.info(f"[JOB] Cleaned up: {job_id}")


# Singleton instance (initialized in Flask app)
_websocket_manager: WebSocketManager = None


def init_websocket(app, socketio: SocketIO):
    """Initialize WebSocket manager (call from Flask app)"""
    global _websocket_manager
    _websocket_manager = WebSocketManager(socketio)
    logger.info("[WEBSOCKET] Initialized with Flask app")


def get_websocket_manager() -> WebSocketManager:
    """Get WebSocket manager instance (singleton)"""
    if _websocket_manager is None:
        raise RuntimeError("WebSocket manager not initialized. Call init_websocket() first.")
    return _websocket_manager


# Example integration with generation endpoint:
"""
from websocket_config import get_websocket_manager

@app.route('/api/generate-3d', methods=['POST'])
def generate_3d():
    job_id = str(uuid.uuid4())
    ws = get_websocket_manager()
    ws.create_job(job_id, 'generate_3d', {'model': 'hunyuan3d-2.1'})

    try:
        # Simulate progress stages
        for stage_num in range(1, 8):
            ws.update_job_progress(
                job_id=job_id,
                progress=int((stage_num / 7) * 100),
                stage=f'stage_{stage_num}',
                stage_progress=50,
                eta_seconds=30 - (stage_num * 4)
            )
            time.sleep(1)  # Simulate work

        ws.complete_job(job_id, {'output_path': '/path/to/model.stl'})
        return jsonify({'job_id': job_id, 'status': 'complete'})

    except Exception as e:
        ws.error_job(job_id, str(e), error_code='GENERATION_FAILED')
        return jsonify({'error': str(e)}), 500
"""

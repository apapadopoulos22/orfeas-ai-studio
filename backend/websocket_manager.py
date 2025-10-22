"""
ORFEAS WebSocket Manager
=========================
Real-time WebSocket connection management for progress updates

Features:
- Connection pool management
- Event broadcasting to specific clients or all
- Client tracking with metadata
- Heartbeat monitoring for connection health
- Auto-reconnect support
- Room-based messaging (per job_id)
- Prometheus metrics integration (Phase 2.5)

ORFEAS AI Project
"""

import logging
import time
import threading
from typing import Dict, Set, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from flask import request

# Import Prometheus metrics tracking
from prometheus_metrics import (
    track_websocket_connection,
    track_websocket_message,
    track_websocket_error,
    track_websocket_duration
)

logger = logging.getLogger(__name__)


@dataclass
class ClientConnection:
    """Represents a connected WebSocket client"""
    sid: str  # Socket ID
    connected_at: datetime
    last_seen: datetime
    ip_address: str
    user_agent: str
    rooms: Set[str] = field(default_factory=set)  # Job IDs subscribed to
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_alive(self, timeout_seconds: int = 60) -> bool:
        """Check if connection is still alive"""
        elapsed = (datetime.now() - self.last_seen).total_seconds()
        return elapsed < timeout_seconds


class WebSocketManager:
    """
    Manages WebSocket connections for real-time progress updates

    Usage:
        ws_mgr = WebSocketManager(socketio)
        ws_mgr.emit_progress('job_123', {'progress': 50, 'stage': 'shape_generation'})
    """

    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.clients: Dict[str, ClientConnection] = {}
        self._lock = threading.Lock()
        self._heartbeat_thread = None
        self._running = False

        # Register event handlers
        self._register_handlers()

        logger.info("[ORFEAS] WebSocket Manager initialized")

    def _register_handlers(self):
        """Register SocketIO event handlers"""

        @self.socketio.on('connect')
        def handle_connect():
            """Handle new client connection"""
            sid = request.sid

            with self._lock:
                self.clients[sid] = ClientConnection(
                    sid=sid,
                    connected_at=datetime.now(),
                    last_seen=datetime.now(),
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', 'Unknown')
                )

            # Track connection in Prometheus
            track_websocket_connection(client_type='browser', increment=True)

            logger.info(f"[ORFEAS] WebSocket client connected: {sid} from {request.remote_addr}")
            emit('connection_established', {
                'sid': sid,
                'timestamp': datetime.now().isoformat(),
                'message': 'Connected to ORFEAS 3D generation server'
            })

        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            sid = request.sid

            with self._lock:
                if sid in self.clients:
                    client = self.clients[sid]

                    # Calculate connection duration for metrics
                    duration = (datetime.now() - client.connected_at).total_seconds()
                    track_websocket_duration(duration)

                    # Track disconnection in Prometheus
                    track_websocket_connection(client_type='browser', increment=False)

                    # Leave all rooms
                    for room in list(client.rooms):
                        leave_room(room)

                    del self.clients[sid]
                    logger.info(f"[ORFEAS] WebSocket client disconnected: {sid} (duration: {duration:.1f}s)")

        @self.socketio.on('subscribe')
        def handle_subscribe(data):
            """Subscribe client to job updates"""
            sid = request.sid
            job_id = data.get('job_id')

            if not job_id:
                emit('error', {'message': 'job_id required for subscription'})
                return

            with self._lock:
                if sid in self.clients:
                    join_room(job_id)
                    self.clients[sid].rooms.add(job_id)
                    self.clients[sid].last_seen = datetime.now()

                    logger.info(f"[ORFEAS] Client {sid} subscribed to job {job_id}")
                    emit('subscribed', {
                        'job_id': job_id,
                        'timestamp': datetime.now().isoformat()
                    })

        @self.socketio.on('unsubscribe')
        def handle_unsubscribe(data):
            """Unsubscribe client from job updates"""
            sid = request.sid
            job_id = data.get('job_id')

            if not job_id:
                emit('error', {'message': 'job_id required for unsubscription'})
                return

            with self._lock:
                if sid in self.clients:
                    leave_room(job_id)
                    self.clients[sid].rooms.discard(job_id)
                    self.clients[sid].last_seen = datetime.now()

                    logger.info(f"[ORFEAS] Client {sid} unsubscribed from job {job_id}")
                    emit('unsubscribed', {'job_id': job_id})

        @self.socketio.on('ping')
        def handle_ping():
            """Handle client heartbeat ping"""
            sid = request.sid

            with self._lock:
                if sid in self.clients:
                    self.clients[sid].last_seen = datetime.now()

            emit('pong', {'timestamp': datetime.now().isoformat()})

    def emit_progress(self, job_id: str, data: Dict[str, Any]):
        """
        Emit progress update to all clients subscribed to job

        Args:
            job_id: Job identifier
            data: Progress data (progress, stage, eta, etc.)
        """
        data['job_id'] = job_id
        data['timestamp'] = datetime.now().isoformat()

        self.socketio.emit('generation_progress', data, room=job_id)
        track_websocket_message('progress')  # Track metrics
        logger.debug(f"[ORFEAS] Progress update sent for job {job_id}: {data.get('progress', 0)}%")

    def emit_stage_change(self, job_id: str, stage: str, stage_progress: int = 0):
        """
        Emit stage change notification

        Args:
            job_id: Job identifier
            stage: New stage name
            stage_progress: Progress within stage (0-100)
        """
        self.socketio.emit('stage_change', {
            'job_id': job_id,
            'stage': stage,
            'stage_progress': stage_progress,
            'timestamp': datetime.now().isoformat()
        }, room=job_id)

        track_websocket_message('stage_change')  # Track metrics
        logger.info(f"[ORFEAS] Stage change for job {job_id}: {stage}")

    def emit_completion(self, job_id: str, success: bool, result: Optional[Dict[str, Any]] = None):
        """
        Emit job completion notification

        Args:
            job_id: Job identifier
            success: Whether job completed successfully
            result: Optional result data (file paths, metrics, etc.)
        """
        self.socketio.emit('generation_complete', {
            'job_id': job_id,
            'success': success,
            'result': result or {},
            'timestamp': datetime.now().isoformat()
        }, room=job_id)

        track_websocket_message('complete')  # Track metrics
        logger.info(f"[ORFEAS] Job {job_id} completion: {'success' if success else 'failure'}")

    def emit_error(self, job_id: str, error: str, recoverable: bool = False):
        """
        Emit error notification

        Args:
            job_id: Job identifier
            error: Error message
            recoverable: Whether error is recoverable
        """
        self.socketio.emit('generation_error', {
            'job_id': job_id,
            'error': error,
            'recoverable': recoverable,
            'timestamp': datetime.now().isoformat()
        }, room=job_id)

        track_websocket_message('error')  # Track metrics
        logger.error(f"[ORFEAS] Error for job {job_id}: {error}")

    def broadcast(self, event: str, data: Dict[str, Any]):
        """
        Broadcast message to all connected clients

        Args:
            event: Event name
            data: Event data
        """
        data['timestamp'] = datetime.now().isoformat()
        self.socketio.emit(event, data)
        logger.debug(f"[ORFEAS] Broadcast {event} to all clients")

    def get_connected_clients(self) -> int:
        """Get number of connected clients"""
        with self._lock:
            return len(self.clients)

    def get_client_info(self, sid: str) -> Optional[Dict[str, Any]]:
        """Get information about specific client"""
        with self._lock:
            if sid not in self.clients:
                return None

            client = self.clients[sid]
            return {
                'sid': client.sid,
                'connected_at': client.connected_at.isoformat(),
                'last_seen': client.last_seen.isoformat(),
                'ip_address': client.ip_address,
                'user_agent': client.user_agent,
                'rooms': list(client.rooms),
                'metadata': client.metadata
            }

    def get_all_clients(self) -> list:
        """Get information about all connected clients"""
        with self._lock:
            return [self.get_client_info(sid) for sid in self.clients.keys()]

    def start_heartbeat_monitor(self, interval: int = 30, timeout: int = 60):
        """
        Start heartbeat monitoring thread

        Args:
            interval: Check interval in seconds
            timeout: Connection timeout in seconds
        """
        if self._heartbeat_thread is not None:
            logger.warning("[ORFEAS] Heartbeat monitor already running")
            return

        self._running = True

        def monitor():
            while self._running:
                time.sleep(interval)

                with self._lock:
                    dead_clients = []

                    for sid, client in self.clients.items():
                        if not client.is_alive(timeout):
                            dead_clients.append(sid)

                    for sid in dead_clients:
                        logger.warning(f"[ORFEAS] Client {sid} timed out, disconnecting")
                        try:
                            self.socketio.server.disconnect(sid)
                        except Exception as e:
                            logger.error(f"Error disconnecting {sid}: {e}")

                        if sid in self.clients:
                            del self.clients[sid]

                if dead_clients:
                    logger.info(f"[ORFEAS] Cleaned up {len(dead_clients)} dead connections")

        self._heartbeat_thread = threading.Thread(target=monitor, daemon=True)
        self._heartbeat_thread.start()
        logger.info(f"[ORFEAS] Heartbeat monitor started (interval: {interval}s, timeout: {timeout}s)")

    def stop_heartbeat_monitor(self):
        """Stop heartbeat monitoring thread"""
        self._running = False
        if self._heartbeat_thread:
            self._heartbeat_thread.join(timeout=5)
            self._heartbeat_thread = None
            logger.info("[ORFEAS] Heartbeat monitor stopped")

    def disconnect_client(self, sid: str):
        """Manually disconnect a client"""
        with self._lock:
            if sid in self.clients:
                try:
                    self.socketio.server.disconnect(sid)
                    del self.clients[sid]
                    logger.info(f"[ORFEAS] Client {sid} manually disconnected")
                except Exception as e:
                    logger.error(f"Error disconnecting client {sid}: {e}")


# Singleton instance
_websocket_manager: Optional[WebSocketManager] = None
_ws_lock = threading.Lock()


def initialize_websocket_manager(socketio: SocketIO) -> WebSocketManager:
    """
    Initialize WebSocket manager singleton

    Args:
        socketio: Flask-SocketIO instance

    Returns:
        WebSocketManager instance
    """
    global _websocket_manager

    with _ws_lock:
        if _websocket_manager is None:
            _websocket_manager = WebSocketManager(socketio)
            _websocket_manager.start_heartbeat_monitor()
            logger.info("[ORFEAS] WebSocket Manager singleton initialized")

        return _websocket_manager


def get_websocket_manager() -> Optional[WebSocketManager]:
    """
    Get WebSocket manager singleton

    Returns:
        WebSocketManager instance or None if not initialized
    """
    return _websocket_manager

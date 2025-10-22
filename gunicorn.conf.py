# =============================================================================
# ORFEAS AI 2D→3D Studio - Gunicorn Production Configuration
# =============================================================================
# ORFEAS AI Project
#
# Production WSGI server configuration for Flask backend
# Optimized for RTX 3090 GPU workloads and long-running 3D generation
# =============================================================================

import multiprocessing
import os
from typing import Any

# -----------------------------------------------------------------------------
# Server Socket
# -----------------------------------------------------------------------------
bind = "0.0.0.0:5000"
backlog = 2048

# -----------------------------------------------------------------------------
# Worker Processes
# -----------------------------------------------------------------------------
# Formula: (2 * CPU cores) + 1
# For 8-core system: (2 * 8) + 1 = 17 workers
# Adjusted down for GPU workloads (limit concurrent GPU operations)
workers = min(multiprocessing.cpu_count() * 2 + 1, 8)
worker_class = "sync"  # Use sync for long-running GPU tasks
worker_connections = 1000
max_requests = 1000  # Recycle workers after 1000 requests (prevent memory leaks)
max_requests_jitter = 50  # Add randomness to prevent all workers restarting at once
timeout = 300  # 5 minutes (long enough for 3D generation: ~82s + buffer)
graceful_timeout = 30  # 30 seconds for graceful shutdown
keepalive = 5  # Keep-alive connections

# -----------------------------------------------------------------------------
# Worker Lifecycle
# -----------------------------------------------------------------------------
def on_starting(server: Any) -> None:
    """
    Called just before the master process is initialized.
    """
    print("[ORFEAS] Gunicorn master process starting...")
    print(f"[ORFEAS] Workers: {workers}")
    print(f"[ORFEAS] Timeout: {timeout}s")
    print(f"[ORFEAS] Max requests per worker: {max_requests}")


def on_reload(server: Any) -> None:
    """
    Called to recycle workers during a reload via SIGHUP.
    """
    print("[ORFEAS] Gunicorn reloading...")


def when_ready(server: Any) -> None:
    """
    Called just after the server is started.
    """
    print("[ORFEAS] Gunicorn server ready!")
    print(f"[ORFEAS] Listening on: {bind}")


def pre_fork(server: Any, worker: Any) -> None:
    """
    Called just before a worker is forked.
    """
    print(f"[ORFEAS] Forking worker {worker.pid}...")


def post_fork(server: Any, worker: Any) -> None:
    """
    Called just after a worker has been forked.
    """
    print(f"[ORFEAS] Worker {worker.pid} forked successfully")


def pre_exec(server: Any) -> None:
    """
    Called just before a new master process is forked.
    """
    print("[ORFEAS] Pre-exec: Forking new master process...")


def pre_request(worker: Any, req: Any) -> None:
    """
    Called just before a worker processes the request.
    """
    worker.log.debug(f"[ORFEAS] {req.method} {req.path}")


def post_request(worker: Any, req: Any, environ: Any, resp: Any) -> None:
    """
    Called after a worker processes the request.
    """
    worker.log.debug(f"[ORFEAS] {req.method} {req.path} - {resp.status}")


def worker_int(worker: Any) -> None:
    """
    Called when a worker receives the SIGINT or SIGQUIT signal.
    """
    print(f"[ORFEAS] Worker {worker.pid} received INT/QUIT signal")


def worker_abort(worker: Any) -> None:
    """
    Called when a worker receives the SIGABRT signal.
    """
    print(f"[ORFEAS] Worker {worker.pid} aborted!")


def worker_exit(server: Any, worker: Any) -> None:
    """
    Called just after a worker has been exited.
    """
    print(f"[ORFEAS] Worker {worker.pid} exited")


# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
loglevel = os.getenv("LOG_LEVEL", "info").lower()
accesslog = "/app/logs/gunicorn_access.log"
errorlog = "/app/logs/gunicorn_error.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Capture output from Flask app
capture_output = True

# Redirect stdout/stderr to error log
enable_stdio_inheritance = True

# -----------------------------------------------------------------------------
# Process Naming
# -----------------------------------------------------------------------------
proc_name = "orfeas-backend"

# -----------------------------------------------------------------------------
# Server Mechanics
# -----------------------------------------------------------------------------
daemon = False  # Run in foreground (Docker handles daemonization)
pidfile = None  # No PID file needed in Docker
umask = 0
user = None  # Run as orfeas user (set in Dockerfile)
group = None
tmp_upload_dir = "/app/temp"

# -----------------------------------------------------------------------------
# SSL (if needed)
# -----------------------------------------------------------------------------
# keyfile = "/path/to/key.pem"
# certfile = "/path/to/cert.pem"

# -----------------------------------------------------------------------------
# Server Hooks
# -----------------------------------------------------------------------------
# Preload application code before worker processes are forked
# This can save RAM but may cause issues with GPU initialization
preload_app = False  # Set to False for GPU workloads to avoid CUDA fork issues

# -----------------------------------------------------------------------------
# Worker Timeouts
# -----------------------------------------------------------------------------
# Restart workers if they haven't completed a request in this time
# For 3D generation: 82s average + 2x buffer = 165s, rounded to 300s for safety
timeout = 300

# Graceful timeout: time to wait for workers to finish current requests
graceful_timeout = 30

# -----------------------------------------------------------------------------
# Security
# -----------------------------------------------------------------------------
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# -----------------------------------------------------------------------------
# Server Tuning
# -----------------------------------------------------------------------------
# Maximum number of pending connections
backlog = 2048

# SO_REUSEPORT flag on the listening socket
reuse_port = False

# Reuse TCP connections (keep-alive)
keepalive = 5

# -----------------------------------------------------------------------------
# Development/Debug (disable in production)
# -----------------------------------------------------------------------------
reload = False  # Auto-reload on code changes (dev only)
reload_engine = "auto"
reload_extra_files = []
spew = False  # Print every line executed (extreme debug only)
check_config = False

# -----------------------------------------------------------------------------
# Configuration Validation
# -----------------------------------------------------------------------------
print("=" * 80)
print("ORFEAS AI 2D→3D Studio - Gunicorn Configuration")
print("=" * 80)
print(f"Workers: {workers}")
print(f"Worker Class: {worker_class}")
print(f"Bind: {bind}")
print(f"Timeout: {timeout}s")
print(f"Graceful Timeout: {graceful_timeout}s")
print(f"Max Requests: {max_requests}")
print(f"Keep-Alive: {keepalive}s")
print(f"Preload App: {preload_app}")
print(f"Log Level: {loglevel}")
print(f"Access Log: {accesslog}")
print(f"Error Log: {errorlog}")
print("=" * 80)

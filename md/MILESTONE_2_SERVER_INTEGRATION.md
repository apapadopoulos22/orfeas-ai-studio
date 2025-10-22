# MILESTONE 2: SERVER INTEGRATION - IMPLEMENTATION PLAN

**Report Date:** October 16, 2025
**Milestone:** Milestone 2 - Server Integration

## # # Status:****IN PROGRESS

**Duration Estimate:** 8-12 hours

## # # Priority:****CRITICAL

---

## # # [STATS] MILESTONE 2 OVERVIEW

## # # Current System Status

**Overall Health:**  **GOOD** (Production running, some test failures)
**Integration Status:**  **PARTIAL** (Backend operational, frontend/backend sync issues)
**Test Coverage:**  **MODERATE** (115 integration tests collected, 5 failing)
**API Endpoints:**  **OPERATIONAL** (12+ endpoints active)
**WebSocket:**  **BASIC** (Connected but limited progress updates)

## # # Test Results Summary

```text
Integration Tests: 115 collected

-  PASSED: 110 tests (95.7%)
-  FAILED: 5 tests (4.3%)

  - test_generate_3d_different_formats (Timeout)
  - test_generate_3d_quality_levels (Timeout)
  - test_download_generated_model (Timeout)
  - test_concurrent_health_checks (Timeout)
  - test_concurrent_uploads (Timeout)

```text

## # # Critical Issues Identified

1. ⏱ Request timeouts during 3D generation (180s limit exceeded)

2. Concurrent request handling failures

3. Download endpoint timeouts

4. WebSocket progress updates incomplete

---

## # # [TARGET] MILESTONE 2 OBJECTIVES

## # # Primary Goals

1. **Fix All Integration Test Failures**

- Resolve timeout issues in generation tests
- Fix concurrent request handling
- Ensure download endpoints are responsive

1. **Complete WebSocket Integration**

- Implement real-time progress updates
- Add generation stage notifications
- Provide ETA calculations
- Handle error notifications

1. **Standardize API Endpoints**

- Audit frontend API calls vs backend routes
- Fix endpoint mismatches
- Document all endpoints
- Generate OpenAPI spec

1. **Performance Optimization**

- Reduce API response times
- Optimize concurrent request handling
- Implement request queueing
- Add caching layer

1. **Complete API Documentation**

- OpenAPI 3.0 specification
- Swagger UI integration
- Request/response examples
- Error code documentation

---

## # # [LAUNCH] PHASE 1: FIX INTEGRATION TESTS

**Duration:** 2-3 hours

## # # Priority:****CRITICAL (2)

## # # Task 1.1: Fix Generation Timeout Issues

**Problem:** 3D generation tests timeout after 180s

## # # Root Cause Analysis

```python

## Current issue in tests/conftest.py

def request_with_timeout(self, method, url, timeout=30, **kwargs):

    # Timeout too short for GPU-intensive operations

    # 3D generation can take 30-60+ seconds

```text

## # # Solution

```python

## tests/conftest.py - Update timeout handling

class TestClient:
    def request_with_timeout(self, method, url, timeout=None, **kwargs):
        """
        Smart timeout based on endpoint

        - Health checks: 10s
        - Uploads: 30s
        - Text-to-image: 60s
        - 3D generation: 300s (5 minutes)

        """

        # Determine appropriate timeout based on endpoint

        if '/api/generate-3d' in url:
            timeout = 300  # 5 minutes for 3D generation
        elif '/api/text-to-image' in url:
            timeout = 60   # 1 minute for image generation
        elif '/download/' in url:
            timeout = 60   # 1 minute for downloads
        elif timeout is None:
            timeout = 30   # Default 30s

        # Execute request with appropriate timeout

        return self._execute_request(method, url, timeout, **kwargs)

```text

## # # Files to Modify

- `backend/tests/conftest.py` - Update timeout logic
- `backend/tests/integration/test_api_endpoints.py` - Add longer timeouts for generation tests
- `backend/tests/integration/test_api_performance.py` - Fix concurrent test timeouts

## # # Task 1.2: Fix Concurrent Request Handling

**Problem:** Concurrent health checks and uploads fail

## # # Root Cause

```python

## Backend may not be handling concurrent requests properly

## Need to verify

## 1. Flask threading configuration

## 2. SocketIO async mode

## 3. Resource locking

```text

## # # Solution (2)

```python

## backend/main.py - Ensure proper threading

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

## Configure SocketIO with async mode

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',  #  Enable threading
    ping_timeout=60,
    ping_interval=25,
    max_http_buffer_size=50 * 1024 * 1024  # 50MB
)

## Ensure Flask runs in threaded mode

if __name__ == '__main__':
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=False,
        use_reloader=False,
        threaded=True  #  Enable threading
    )

```text

## # # Files to Modify (2)

- `backend/main.py` - Configure threading
- `backend/batch_processor.py` - Add thread-safe queue management
- `backend/gpu_manager.py` - Ensure thread-safe GPU allocation

## # # Task 1.3: Fix Download Endpoint Issues

**Problem:** Download endpoint timeouts

## # # Current Implementation Check

```python

## backend/main.py - Check download endpoint

@app.route('/download/<job_id>/<format>', methods=['GET'])
def download_model(job_id, format):
    """Download generated 3D model"""

    # Verify file exists

    # Return file with proper headers

```text

## # # Solution (3)

```python
@app.route('/download/<job_id>/<format>', methods=['GET'])
@track_request_metrics('download_model')
def download_model(job_id, format):
    """
    Download generated 3D model

    Supports: STL, OBJ, PLY, GLB formats
    """
    try:

        # Find job output

        output_path = find_job_output(job_id, format)

        if not output_path or not os.path.exists(output_path):
            logger.warning(f"[ORFEAS] File not found: {job_id}.{format}")
            return jsonify({'error': 'File not found'}), 404

        # Send file with proper headers

        return send_file(
            output_path,
            as_attachment=True,
            download_name=f"orfeas_model_{job_id}.{format}",
            mimetype=get_mimetype(format),
            max_age=0  # No caching
        )
    except Exception as e:
        logger.error(f"[ORFEAS] Download error: {str(e)}")
        return jsonify({'error': str(e)}), 500

```text

## # # Files to Modify (3)

- `backend/main.py` - Fix download endpoint
- `backend/tests/integration/test_api_endpoints.py` - Add download tests

## # # Task 1.4: Run Complete Test Validation

## # # Validation Steps

```powershell

## 1. Run integration tests with verbose output

cd backend
python -m pytest tests/integration/ -v --tb=short

## 2. Check specific failing tests

python -m pytest tests/integration/test_api_endpoints.py::TestGenerate3D::test_generate_3d_different_formats -v -s

## 3. Run performance tests

python -m pytest tests/integration/test_api_performance.py -v

## 4. Generate coverage report

python -m pytest tests/integration/ --cov=. --cov-report=html

## 5. Verify all tests pass

python -m pytest tests/integration/ -v

```text

## # # Success Criteria

- All 115 integration tests pass
- No timeout errors
- Concurrent requests handled properly
- Download endpoints responsive

---

## # # [LAUNCH] PHASE 2: WEBSOCKET INTEGRATION

**Duration:** 2-3 hours

## # # Priority:****HIGH

## # # Task 2.1: Implement Real-Time Progress Updates

## # # Current State

```javascript
// orfeas-studio.html - Basic WebSocket connection
socket = io('http://localhost:5000');
socket.on('generation_progress', function(data) {
    console.log('Progress:', data.progress);
});

```text

## # # Enhanced Implementation

## # # Backend (main.py)

```python
@socketio.on('start_generation')
def handle_generation_start(data):
    """
    Handle 3D generation start with real-time progress
    """
    job_id = data.get('job_id')
    client_sid = request.sid

    logger.info(f"[ORFEAS] Starting generation for job {job_id}, client {client_sid}")

    def progress_callback(stage, progress, eta_seconds=None):
        """Emit progress updates to client"""
        socketio.emit('generation_progress', {
            'job_id': job_id,
            'stage': stage,
            'progress': progress,
            'eta_seconds': eta_seconds,
            'timestamp': datetime.now().isoformat()
        }, room=client_sid)

    try:

        # Stage 1: Background removal (0-10%)

        progress_callback('background_removal', 0, 45)
        processed_image = processor.remove_background(image)
        progress_callback('background_removal', 10, 40)

        # Stage 2: Shape generation (10-60%)

        progress_callback('shape_generation', 10, 35)
        mesh = processor.generate_shape(
            processed_image,
            progress_callback=lambda p: progress_callback('shape_generation', 10 + int(p * 0.5), 30)
        )
        progress_callback('shape_generation', 60, 15)

        # Stage 3: Texture synthesis (60-90%)

        progress_callback('texture_synthesis', 60, 12)
        textured_mesh = processor.apply_texture(
            mesh,
            progress_callback=lambda p: progress_callback('texture_synthesis', 60 + int(p * 0.3), 8)
        )
        progress_callback('texture_synthesis', 90, 3)

        # Stage 4: Export and optimize (90-100%)

        progress_callback('export', 90, 2)
        output_path = export_mesh(textured_mesh, job_id)
        progress_callback('export', 100, 0)

        # Emit completion

        socketio.emit('generation_complete', {
            'job_id': job_id,
            'output_path': output_path,
            'success': True
        }, room=client_sid)

    except Exception as e:
        logger.error(f"[ORFEAS] Generation failed: {str(e)}")
        socketio.emit('generation_error', {
            'job_id': job_id,
            'error': str(e),
            'stage': stage
        }, room=client_sid)

```text

## # # Frontend (orfeas-studio.html)

```javascript
// Enhanced WebSocket handling
socket.on('generation_progress', function(data) {
    const { job_id, stage, progress, eta_seconds } = data;

    // Update progress bar
    updateProgressBar(progress);

    // Update stage indicator
    updateStageIndicator(stage);

    // Update ETA
    if (eta_seconds) {
        updateETA(eta_seconds);
    }

    // Log to console
    console.log(`[${job_id}] ${stage}: ${progress}% (ETA: ${eta_seconds}s)`);
});

socket.on('generation_complete', function(data) {
    const { job_id, output_path } = data;
    console.log(`Generation complete: ${output_path}`);

    // Hide progress
    hideProgressIndicator();

    // Load 3D model in viewer
    load3DModel(output_path);

    // Show success message
    showSuccessMessage('3D model generated successfully!');
});

socket.on('generation_error', function(data) {
    const { job_id, error, stage } = data;
    console.error(`Generation failed at ${stage}: ${error}`);

    // Hide progress
    hideProgressIndicator();

    // Show error message
    showErrorMessage(`Generation failed: ${error}`);
});

```text

## # # Files to Modify (4)

- `backend/main.py` - Add progress callback support
- `backend/hunyuan_integration.py` - Implement progress callbacks in generation
- `orfeas-studio.html` - Enhanced WebSocket handling
- `orfeas-3d-engine-hybrid.js` - Add progress UI components

## # # Task 2.2: Add Generation Stage Tracking

## # # Stages to Track

1. **Background Removal** (0-10%) - ~5 seconds

2. **Shape Generation** (10-60%) - ~25-35 seconds

3. **Texture Synthesis** (60-90%) - ~10-15 seconds

4. **Export & Optimize** (90-100%) - ~2-5 seconds

## # # Implementation

```python

## backend/hunyuan_integration.py

class Hunyuan3DProcessor:
    def generate_with_progress(self, image, progress_callback=None):
        """
        Generate 3D model with progress tracking

        Args:
            image: Input image (PIL Image or path)
            progress_callback: Callable(stage, progress, eta)
        """
        total_steps = 100

        # Stage 1: Background removal

        if progress_callback:
            progress_callback('background_removal', 0, 45)

        processed_image = self.rembg.remove_background(image)

        if progress_callback:
            progress_callback('background_removal', 10, 40)

        # Stage 2: Shape generation

        if progress_callback:
            progress_callback('shape_generation', 10, 35)

        # Hook into Hunyuan3D pipeline for per-step progress

        def shape_step_callback(step, total_steps):
            progress = 10 + int((step / total_steps) * 50)
            eta = (total_steps - step) * 0.7  # ~0.7s per step
            if progress_callback:
                progress_callback('shape_generation', progress, eta + 15)

        mesh = self.shapegen_pipeline(
            image=processed_image,
            num_inference_steps=50,
            callback=shape_step_callback
        )

        # Continue for texture and export...

        return mesh

```text

## # # Task 2.3: WebSocket Error Handling

## # # Error Types to Handle

1. Connection loss during generation

2. GPU out of memory

3. Invalid input images

4. Model loading failures
5. Export errors

## # # Implementation (2)

```python

## backend/main.py

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection during generation"""
    client_sid = request.sid
    logger.warning(f"[ORFEAS] Client disconnected: {client_sid}")

    # Check if client has active jobs

    active_jobs = job_queue.get_jobs_for_client(client_sid)

    for job_id in active_jobs:

        # Mark job as cancelled

        job_queue.cancel_job(job_id)
        logger.info(f"[ORFEAS] Cancelled job {job_id} due to client disconnect")

@socketio.on('cancel_generation')
def handle_cancel(data):
    """Handle generation cancellation"""
    job_id = data.get('job_id')
    logger.info(f"[ORFEAS] Cancelling job {job_id}")

    # Cancel job

    success = job_queue.cancel_job(job_id)

    # Emit cancellation confirmation

    emit('generation_cancelled', {
        'job_id': job_id,
        'success': success
    })

```text

## # # Files to Modify (5)

- `backend/main.py` - Add disconnect and cancel handlers
- `backend/batch_processor.py` - Implement job cancellation
- `orfeas-studio.html` - Add cancel button and disconnect handling

---

## # # [LAUNCH] PHASE 3: API ENDPOINT STANDARDIZATION

**Duration:** 2 hours

## # # Priority:****HIGH (2)

## # # Task 3.1: Audit All API Endpoints

## # # Current Endpoints (Backend)

```python

## Health & Monitoring

GET  /health                    # Health check
GET  /api/health                # API health
GET  /metrics                   # Prometheus metrics

## Image Processing

POST /api/upload-image          # Upload image for processing
POST /api/text-to-image         # Text → Image generation

## 3D Generation

POST /api/generate-3d           # Image → 3D model
GET  /api/job-status/<job_id>   # Check generation status

## Download

GET  /download/<job_id>/<format>  # Download model (STL, OBJ, etc.)

## Preview & Analysis

POST /api/analyze-stl           # Analyze STL file
POST /api/preview-3d            # Generate preview image

## Advanced Features

POST /api/batch-generate        # Batch processing
POST /api/optimize-mesh         # Mesh optimization
POST /api/apply-material        # Apply material preset

```text

## # # Frontend API Calls Audit

```javascript
// Check orfeas-studio.html for all fetch() calls
// Expected patterns:
fetch('/api/upload-image', ...)
fetch('/api/text-to-image', ...)
fetch('/api/generate-3d', ...)
fetch('/download/...')

```text

## # # Action Items

1. List all backend routes

2. List all frontend API calls

3. Identify mismatches

4. Fix inconsistencies
5. Document all endpoints

## # # Task 3.2: Fix Endpoint Mismatches

## # # Known Issues from TQM Report

```javascript
// WRONG: Frontend may call
fetch('/api/image-to-3d', ...)  //  Wrong endpoint

// CORRECT: Should be
fetch('/api/generate-3d', ...)  //  Correct endpoint

```text

## # # Search and Fix

```powershell

## Search for API calls in frontend

cd ..
Select-String -Path "orfeas-studio.html" -Pattern "fetch\(['\"].*api" -AllMatches

## Search for mismatched endpoints

Select-String -Path "orfeas-studio.html" -Pattern "image-to-3d|generate-3d" -AllMatches

```text

## # # Standardization Rules

```text

1. All API endpoints start with /api/

2. Use kebab-case (generate-3d not generateThreeD)

3. RESTful conventions:

   - GET for retrieval
   - POST for creation
   - PUT for updates
   - DELETE for deletion
4. Consistent naming:
   - /api/generate-3d (not /api/image-to-3d)
   - /api/upload-image (not /api/upload)
   - /api/job-status/<id> (not /api/status/<id>)

```text

## # # Task 3.3: Generate OpenAPI Specification

**Tool:** Use Flask-RESTX or manual OpenAPI 3.0 spec

## # # Implementation (3)

```python

## backend/api_models.py (expand existing)

from flask_restx import Api, Resource, fields, Namespace

## Create API documentation

api = Api(
    app,
    version='2.0.0',
    title='ORFEAS AI 2D→3D Studio API',
    description='Professional AI-powered 3D model generation',
    doc='/api/docs',
    prefix='/api'
)

## Define namespaces

ns_generation = Namespace('generation', description='3D model generation')
ns_upload = Namespace('upload', description='Image upload and processing')
ns_download = Namespace('download', description='Model download')

## Define models

upload_response = api.model('UploadResponse', {
    'job_id': fields.String(required=True, description='Job ID for tracking'),
    'status': fields.String(required=True, description='Processing status'),
    'message': fields.String(description='Status message')
})

generate_request = api.model('Generate3DRequest', {
    'job_id': fields.String(required=True, description='Job ID from upload'),
    'quality': fields.Integer(description='Quality level (1-10)', default=7),
    'format': fields.String(description='Output format (stl, obj, glb)', default='stl')
})

generate_response = api.model('Generate3DResponse', {
    'job_id': fields.String(required=True, description='Job ID'),
    'status': fields.String(required=True, description='Generation status'),
    'progress': fields.Integer(description='Progress percentage (0-100)'),
    'output_path': fields.String(description='Path to generated model'),
    'download_url': fields.String(description='Download URL')
})

## Document endpoints

@ns_generation.route('/generate-3d')
class Generate3D(Resource):
    @api.doc('generate_3d_model')
    @api.expect(generate_request)
    @api.response(200, 'Success', generate_response)
    @api.response(400, 'Invalid input')
    @api.response(500, 'Generation failed')
    def post(self):
        """
        Generate 3D model from uploaded image

        This endpoint takes a job_id from a previous image upload
        and generates a 3D model using Hunyuan3D-2.1 AI.
        """

        # Implementation...

```text

## # # Generate OpenAPI JSON

```python

## backend/generate_openapi.py

from main import app
import json

with app.app_context():
    spec = api.__schema__

    with open('openapi.json', 'w') as f:
        json.dump(spec, f, indent=2)

    print("OpenAPI spec generated: openapi.json")

```text

## # # Files to Create/Modify

- `backend/api_models.py` - Expand with complete API models
- `backend/main.py` - Integrate Flask-RESTX
- `backend/openapi.yaml` - Update complete spec
- `backend/generate_openapi.py` - Generate spec script

## # # Task 3.4: Setup Swagger UI

## # # Implementation (4)

```python

## backend/main.py - Add Swagger UI

from flask_swagger_ui import get_swaggerui_blueprint

## Swagger UI configuration

SWAGGER_URL = '/api/docs'
API_URL = '/openapi.yaml'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "ORFEAS AI 2D→3D Studio API",
        'layout': 'BaseLayout',
        'docExpansion': 'list',
        'defaultModelsExpandDepth': 2,
        'defaultModelExpandDepth': 2
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

logger.info(f"[ORFEAS] Swagger UI available at: http://localhost:5000{SWAGGER_URL}")

```text

## # # Serve OpenAPI Spec

```python
@app.route('/openapi.yaml')
def openapi_spec():
    """Serve OpenAPI specification"""
    return send_file('openapi.yaml', mimetype='text/yaml')

@app.route('/openapi.json')
def openapi_json():
    """Serve OpenAPI specification (JSON)"""
    return send_file('openapi.json', mimetype='application/json')

```text

## # # Access Documentation

- Swagger UI: <http://localhost:5000/api/docs>
- OpenAPI Spec (YAML): <http://localhost:5000/openapi.yaml>
- OpenAPI Spec (JSON): <http://localhost:5000/openapi.json>

---

## # # [LAUNCH] PHASE 4: PERFORMANCE OPTIMIZATION

**Duration:** 2-3 hours

## # # Priority:****MEDIUM

## # # Task 4.1: Implement Request Queueing

**Problem:** Concurrent requests may overwhelm GPU

## # # Solution: Enhanced Job Queue

```python

## backend/batch_processor.py - Enhance AsyncJobQueue

class EnhancedAsyncJobQueue:
    def __init__(self, max_workers=3, gpu_mgr=None):
        self.job_queue = Queue(maxsize=100)
        self.active_jobs = {}
        self.completed_jobs = {}
        self.max_workers = max_workers
        self.gpu_mgr = gpu_mgr
        self.workers = []

        # Start worker threads

        for i in range(max_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                daemon=True,
                name=f"JobWorker-{i}"
            )
            worker.start()
            self.workers.append(worker)

    def submit_job(self, job_type, priority=5, **kwargs):
        """
        Submit job to queue with priority

        Args:
            job_type: Type of job (text_to_image, generate_3d, etc.)
            priority: Priority 1-10 (10 = highest)

            **kwargs: Job parameters

        Returns:
            Job object with job_id
        """
        job_id = str(uuid.uuid4())
        job = {
            'job_id': job_id,
            'job_type': job_type,
            'priority': priority,
            'status': 'queued',
            'created_at': datetime.now(),
            'params': kwargs
        }

        # Add to queue

        try:
            self.job_queue.put((priority, job), timeout=5)
            logger.info(f"[ORFEAS] Job {job_id} queued (priority: {priority})")
            return job
        except Full:
            logger.error(f"[ORFEAS] Job queue full, rejecting job")
            raise QueueFullError("Job queue is full, please try again later")

    def _worker_loop(self):
        """Worker thread loop"""
        while True:
            try:

                # Get job from queue (blocks until available)

                priority, job = self.job_queue.get()
                job_id = job['job_id']

                logger.info(f"[ORFEAS] Worker processing job {job_id}")

                # Mark as active

                job['status'] = 'processing'
                self.active_jobs[job_id] = job

                # Check GPU availability

                if self.gpu_mgr and not self.gpu_mgr.can_process_job():
                    logger.warning(f"[ORFEAS] GPU unavailable, re-queueing job {job_id}")
                    self.job_queue.put((priority, job))
                    continue

                # Process job

                try:
                    result = self._process_job(job)
                    job['status'] = 'completed'
                    job['result'] = result
                    job['completed_at'] = datetime.now()
                except Exception as e:
                    logger.error(f"[ORFEAS] Job {job_id} failed: {str(e)}")
                    job['status'] = 'failed'
                    job['error'] = str(e)
                    job['failed_at'] = datetime.now()

                # Move to completed

                self.completed_jobs[job_id] = job
                del self.active_jobs[job_id]

                # Mark queue task done

                self.job_queue.task_done()

            except Exception as e:
                logger.error(f"[ORFEAS] Worker error: {str(e)}")

```text

## # # Files to Modify (6)

- `backend/batch_processor.py` - Enhance job queue
- `backend/main.py` - Integrate enhanced queue
- `backend/gpu_manager.py` - Add queue integration

## # # Task 4.2: Add Response Caching

## # # Implementation: Basic File-Based Cache

```python

## backend/cache_manager.py (new file)

import hashlib
import json
import os
from datetime import datetime, timedelta

class CacheManager:
    """
    Simple file-based cache for API responses
    """
    def __init__(self, cache_dir='cache', default_ttl=3600):
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        os.makedirs(cache_dir, exist_ok=True)

    def _get_cache_key(self, *args, **kwargs):
        """Generate cache key from arguments"""
        key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True)
        return hashlib.sha256(key_data.encode()).hexdigest()

    def get(self, key):
        """Get cached value"""
        cache_file = os.path.join(self.cache_dir, f"{key}.json")

        if not os.path.exists(cache_file):
            return None

        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)

            # Check expiration

            expiry = datetime.fromisoformat(cache_data['expiry'])
            if datetime.now() > expiry:
                os.remove(cache_file)
                return None

            return cache_data['value']
        except:
            return None

    def set(self, key, value, ttl=None):
        """Set cached value"""
        ttl = ttl or self.default_ttl
        expiry = datetime.now() + timedelta(seconds=ttl)

        cache_data = {
            'value': value,
            'expiry': expiry.isoformat(),
            'created_at': datetime.now().isoformat()
        }

        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)

    def cache_response(self, ttl=None):
        """Decorator for caching API responses"""
        def decorator(func):
            def wrapper(*args, **kwargs):

                # Generate cache key

                cache_key = self._get_cache_key(func.__name__, *args, **kwargs)

                # Try to get from cache

                cached = self.get(cache_key)
                if cached is not None:
                    logger.info(f"[ORFEAS] Cache hit for {func.__name__}")
                    return cached

                # Execute function

                result = func(*args, **kwargs)

                # Store in cache

                self.set(cache_key, result, ttl)
                logger.info(f"[ORFEAS] Cached result for {func.__name__}")

                return result
            return wrapper
        return decorator

## Usage in main.py

cache_manager = CacheManager()

@app.route('/api/text-to-image', methods=['POST'])
@cache_manager.cache_response(ttl=1800)  # Cache for 30 minutes
def text_to_image():

    # For identical prompts, return cached image

    prompt = request.json.get('prompt')

    # ... generate image ...

```text

## # # Files to Create

- `backend/cache_manager.py` - Cache implementation
- `backend/main.py` - Integrate caching

## # # Task 4.3: Optimize API Response Times

## # # Current Performance

```text
Health check: ~100ms   Good
Upload: ~150-300ms     Good
Text-to-image: ~5-15s  Acceptable
3D generation: ~30-60s  Acceptable (GPU-bound)

```text

## # # Optimizations

1. **Use orjson for JSON serialization** (already implemented)

2. **Compress responses**

3. **Optimize file operations**

4. **Database connection pooling** (when PostgreSQL added)

## # # Compression Implementation

```python

## backend/main.py - Add response compression

from flask_compress import Compress

app = Flask(__name__)
Compress(app)  #  Auto-compress responses > 500 bytes

## Configure compression

app.config['COMPRESS_MIMETYPES'] = [
    'application/json',
    'text/html',
    'text/css',
    'text/javascript'
]
app.config['COMPRESS_LEVEL'] = 6  # Compression level (1-9)
app.config['COMPRESS_MIN_SIZE'] = 500  # Minimum size to compress

```text

## # # Files to Modify (7)

- `backend/main.py` - Add compression
- `backend/requirements.txt` - Add flask-compress

---

## # # [LAUNCH] PHASE 5: COMPLETE TESTING & VALIDATION

**Duration:** 2 hours

## # # Priority:****HIGH (3)

## # # Task 5.1: Run Complete Test Suite

## # # Test Categories

```powershell

## 1. Unit tests

python -m pytest tests/unit/ -v

## 2. Integration tests

python -m pytest tests/integration/ -v

## 3. E2E tests

python -m pytest tests/e2e/ -v

## 4. Performance tests

python -m pytest tests/performance/ -v

## 5. Security tests

python -m pytest tests/security/ -v

## 6. All tests with coverage

python -m pytest --cov=. --cov-report=html --cov-report=term

```text

## # # Task 5.2: Manual Integration Testing

## # # Test Workflow

1. **Start Backend**

   ```powershell
   cd backend
   python main.py

   ```text

1. **Open Frontend**

   ```text
   http://localhost:5000/orfeas-studio.html

   ```text

1. **Test Complete Workflow**

- Text → Image generation
- Image → 3D model generation
- WebSocket progress updates
- Model download
- Format conversion
- Error handling

1. **Test API Documentation**

   ```text
   http://localhost:5000/api/docs

   ```text

## # # Task 5.3: Performance Benchmarking

## # # Benchmark Script

```python

## backend/tests/performance/benchmark_milestone2.py

import pytest
import time
import statistics
from test_client import TestClient

class TestMilestone2Performance:
    def test_api_response_times(self, client):
        """Benchmark API response times"""
        endpoints = [
            ('/health', 'GET'),
            ('/api/health', 'GET'),
            ('/metrics', 'GET'),
        ]

        results = {}
        for endpoint, method in endpoints:
            times = []
            for _ in range(10):
                start = time.time()
                response = client.get(endpoint)
                elapsed = time.time() - start
                times.append(elapsed * 1000)  # ms
                assert response.status_code == 200

            results[endpoint] = {
                'mean': statistics.mean(times),
                'median': statistics.median(times),
                'p95': sorted(times)[int(len(times) * 0.95)],
                'max': max(times)
            }

        # Assert performance requirements

        assert results['/health']['p95'] < 50  # < 50ms
        assert results['/api/health']['p95'] < 100  # < 100ms

        print("\nAPI Response Times (ms):")
        for endpoint, stats in results.items():
            print(f"{endpoint}: {stats['mean']:.2f}ms (P95: {stats['p95']:.2f}ms)")

    def test_concurrent_requests(self, client):
        """Test concurrent request handling"""
        import concurrent.futures

        def make_request():
            response = client.get('/health')
            return response.status_code == 200

        # Test with 10 concurrent requests

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in futures]

        # All requests should succeed

        assert all(results)
        print(f"\nConcurrent requests: {len(results)}/{len(results)} succeeded")

```text

## # # Task 5.4: Create Validation Report

## # # Report Template

```text

## Milestone 2: Server Integration - Validation Report

**Date:** October 16, 2025
**Status:**  COMPLETE

## Test Results

### Integration Tests

- Total: 115 tests
- Passed: 115 (100%)
- Failed: 0 (0%)
- Duration: X.XX seconds

### Performance Benchmarks

| Endpoint | Mean | P95 | Max |
|----------|------|-----|-----|
| /health | XXms | XXms | XXms |
| /api/health | XXms | XXms | XXms |
| /api/upload-image | XXms | XXms | XXms |

### WebSocket Integration

-  Real-time progress updates working
-  Generation stage tracking operational
-  Error notifications functional
-  Client disconnect handling working

### API Documentation

-  OpenAPI 3.0 specification generated
-  Swagger UI accessible at /api/docs
-  All endpoints documented
-  Request/response examples included

### Success Criteria

-  All integration tests passing
-  No timeout errors
-  WebSocket progress updates working
-  API documentation complete
-  Performance targets met

## Issues Found

None

## Recommendations

1. Continue to Milestone 3: Advanced Features

2. Monitor production metrics

3. Gather user feedback

```text

---

## # # [METRICS] SUCCESS CRITERIA

## # # Milestone 2 Completion Checklist

## # # Integration Tests

- All 115+ integration tests passing
- No timeout errors
- Concurrent requests handled properly
- Download endpoints responsive

## # # WebSocket Integration

- Real-time progress updates working
- Generation stage tracking (4 stages)
- ETA calculations accurate
- Error notifications functional
- Client disconnect handling

## # # API Standardization

- All endpoints audited
- Endpoint mismatches fixed
- OpenAPI 3.0 specification complete
- Swagger UI accessible

## # # Performance

- API response < 100ms (P95)
- Concurrent request support (10+ simultaneous)
- Response caching implemented
- Request queueing functional

## # # Documentation

- API documentation complete
- Swagger UI deployed
- Request/response examples
- Error codes documented

---

## # # [LAUNCH] IMPLEMENTATION TIMELINE

## # # Week 1 Schedule

## # # Day 1 (4 hours)

- Phase 1: Fix integration tests (2-3 hours)
- Task 1.1: Fix timeout issues
- Task 1.2: Fix concurrent handling
- Task 1.3: Fix download endpoint
- Task 1.4: Validate all tests pass

## # # Day 2 (4 hours)

- Phase 2: WebSocket integration (2-3 hours)
- Task 2.1: Real-time progress updates
- Task 2.2: Generation stage tracking
- Task 2.3: Error handling

## # # Day 3 (3 hours)

- Phase 3: API standardization (2 hours)
- Task 3.1: Audit endpoints
- Task 3.2: Fix mismatches
- Task 3.3: Generate OpenAPI spec
- Task 3.4: Setup Swagger UI

## # # Day 4 (3 hours)

- Phase 4: Performance optimization (2-3 hours)
- Task 4.1: Request queueing
- Task 4.2: Response caching
- Task 4.3: API optimization

## # # Day 5 (2 hours)

- Phase 5: Testing & validation (2 hours)
- Task 5.1: Complete test suite
- Task 5.2: Manual testing
- Task 5.3: Performance benchmarks
- Task 5.4: Validation report

**Total: 16 hours** (estimated)

---

## # # [SECURE] SECURITY CONSIDERATIONS

## # # Security Checklist for Milestone 2

## # # Input Validation

- All file uploads validated
- Request size limits enforced
- Content-type verification
- Filename sanitization

## # # Rate Limiting

- Per-IP rate limits
- Per-endpoint limits
- Queue size limits

## # # Error Handling

- No sensitive info in error messages
- Proper error logging
- Graceful degradation

## # # WebSocket Security

- CORS properly configured
- Connection limits enforced
- Disconnect handling
- Message validation

---

## # # [CONFIG] CONFIGURATION UPDATES

## # # Required Environment Variables

```bash

## backend/.env - Add new configurations

## WebSocket Configuration

WS_PING_TIMEOUT=60
WS_PING_INTERVAL=25
WS_MAX_CONNECTIONS=100

## Job Queue Configuration

MAX_CONCURRENT_JOBS=3
JOB_QUEUE_SIZE=100
JOB_TIMEOUT=300

## Cache Configuration

CACHE_ENABLED=true
CACHE_DIR=cache
CACHE_DEFAULT_TTL=3600

## API Configuration

API_RATE_LIMIT_PER_IP=100/hour
API_RESPONSE_COMPRESSION=true
API_MAX_REQUEST_SIZE=52428800  # 50MB

## Performance

FLASK_THREADED=true
SOCKETIO_ASYNC_MODE=threading

```text

---

## # # [IDEA] FUTURE ENHANCEMENTS

## # # Beyond Milestone 2

## # # Milestone 3: Advanced Features

- Model management system
- Project workspaces
- Advanced export formats
- Scene composition

## # # Milestone 4: Database Integration

- PostgreSQL migration
- User management
- Project persistence
- Job history

## # # Milestone 5: Enterprise Features

- Authentication & authorization
- Multi-tenancy
- Advanced analytics
- Custom model training

---

## # #

## # #   MILESTONE 2: SERVER INTEGRATION - READY TO BEGIN

## # # â•'                                                                              â•'

## # # â•' STATUS: Implementation plan complete                                         â•'

## # # â•' DURATION: 8-12 hours (5 days @ 2-4 hours/day)                              â•'

## # # â•' PRIORITY: CRITICAL                                                           â•'

## # # â•'                                                                              â•' (2)

## # # â•' FIRST TASK: Fix Integration Tests (Phase 1)                                 â•'

## # # â•' COMMAND: cd backend; python -m pytest tests/integration/ -v                 â•'

## # # â•'                                                                              â•' (3)

## # #  SUCCESS

## # #

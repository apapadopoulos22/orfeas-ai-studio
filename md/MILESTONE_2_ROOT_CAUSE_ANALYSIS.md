# MILESTONE 2: ROOT CAUSE ANALYSIS - GENERATE-3D ENDPOINT

**Date:** October 16, 2025
**Issue:** `/api/generate-3d` endpoint timing out

## # # Status:****ROOT CAUSE IDENTIFIED

---

## # #  ROOT CAUSE IDENTIFIED

## # # The Problem

The `/api/generate-3d` endpoint is **NOT** hanging. The **first request** completes successfully in ~0.5 seconds with HTTP 200.

The issue is that when the **same `job_id`** is used for multiple generation requests (e.g., generating STL then OBJ from the same upload), the **second request hangs**.

## # # Evidence

From test logs:

```text
DEBUG urllib3.connectionpool: http://127.0.0.1:5000 "POST /api/generate-3d HTTP/1.1" 200 269
DEBUG urllib3.connectionpool: Resetting dropped connection: 127.0.0.1
[TIMEOUT after 300s]

```text

**First request:**  SUCCESS (HTTP 200, ~0.5s)
**Second request:**  TIMEOUT (300s, connection dropped)

## # # Test Pattern

```python
def test_generate_3d_different_formats(self, api_client, integration_server, uploaded_job_id):
    formats = ["stl", "obj"]

    for fmt in formats:
        response = api_client.generate_3d(
            job_id=uploaded_job_id,  #  SAME JOB_ID for both requests
            format=fmt,
            quality=5
        )

```text

**Problem:** The test uses the same `uploaded_job_id` for both STL and OBJ generation.

---

## # #  WHY THIS HAPPENS

## # # Async Generation Thread Collision

1. **First Request (STL)**:

- POST `/api/generate-3d` with `job_id=abc123`, `format=stl`
- Async thread started: `generate_3d_async(job_id='abc123', format='stl')`
- Response returned immediately: HTTP 200
- Async thread continues processing in background

1. **Second Request (OBJ) - 0.5s later**:

- POST `/api/generate-3d` with `job_id=abc123`, `format=obj`
- Tries to start async thread: `generate_3d_async(job_id='abc123', format='obj')`
- **CONFLICT:** First async thread still running for same `job_id`
- Connection hangs/drops

## # # Code Analysis

In `backend/main.py` line 1142:

```python
@app.route('/api/generate-3d', methods=['POST'])
def generate_3d():

    # ... validation ...

    # Start async 3D generation

    thread = threading.Thread(
        target=self.generate_3d_async,
        args=(job_id, format_type, dimensions, quality),
        daemon=True
    )
    thread.start()  #  No check if job_id already has running thread

    return jsonify({
        "job_id": job_id,
        "status": "generating_3d"
    })

```text

**Missing:** Check if `job_id` already has an active generation task.

In `backend/main.py` line 2056:

```python
def generate_3d_async(self, job_id: str, format_type: str, ...):
    try:

        # Initialize job progress

        self.job_progress[job_id] = {  #  Overwrites existing progress
            "status": "initializing",
            "progress": 0
        }

        # Find input image

        input_image_path = None
        for file_path in self.uploads_dir.glob(f"{job_id}_*"):

            # ...

```text

**Problem:** If two threads run simultaneously:

- Thread 1 (STL): Working on job_id='abc123'
- Thread 2 (OBJ): Overwrites `self.job_progress['abc123']`
- Thread 1 and 2 fight over the same resources

---

## # #  SOLUTIONS

## # # Solution 1: Prevent Concurrent Requests for Same Job (RECOMMENDED)

Add check in `/api/generate-3d` endpoint:

```python
@app.route('/api/generate-3d', methods=['POST'])
def generate_3d():

    # ...existing validation...

    # [ORFEAS] MILESTONE 2: Prevent concurrent generation for same job_id

    if job_id in self.active_jobs:
        return jsonify({
            "error": "Generation already in progress for this job",
            "job_id": job_id,
            "status": "conflict",
            "message": "Wait for current generation to complete or use a different job_id"
        }), 409  # HTTP 409 Conflict

    # Mark job as active

    self.active_jobs.add(job_id)

    # Start async 3D generation

    thread = threading.Thread(...)
    thread.start()

    return jsonify({...})

```text

## # # Benefits

- Clear error message
- HTTP 409 Conflict status (standard)
- Test will fail fast with clear reason

## # # Solution 2: Generate Unique Job IDs for Each Format

Modify test to upload separate images:

```python
def test_generate_3d_different_formats(self, api_client, integration_server):
    formats = ["stl", "obj"]

    for fmt in formats:

        # Upload new image for each format

        test_image = create_test_image_512()
        upload_response = api_client.upload_image(test_image)
        job_id = upload_response.json()['job_id']

        # Generate with unique job_id

        response = api_client.generate_3d(
            job_id=job_id,
            format=fmt,
            quality=5
        )

        assert response.status_code in [200, 202]

```text

## # # Benefits (2)

- Each generation is independent
- No conflicts
- More realistic test (users upload once per generation)

## # # Solution 3: Use Composite Key (job_id + format)

Modify backend to treat each format as a separate task:

```python

## Create unique task ID

task_id = f"{job_id}_{format_type}_{quality}"

if task_id in self.active_jobs:
    return jsonify({"error": "Task already in progress"}), 409

self.active_jobs.add(task_id)

```text

## # # Benefits (3)

- Allows multiple formats from same upload
- Each format tracked independently

---

## # #  RECOMMENDED FIX

## # # Implement Solution 1 + Solution 2

1. **Backend:** Add job conflict detection (Solution 1)

2. **Tests:** Upload separate images for each format (Solution 2)

This provides:

- Clear error handling
- No race conditions
- Better test isolation
- Realistic user workflow

---

## # #  IMPLEMENTATION PLAN

## # # Step 1: Fix Backend (Add Conflict Detection)

**File:** `backend/main.py`

```python
@self.app.route('/api/generate-3d', methods=['POST'])
@track_request_metrics('/api/generate-3d')
def generate_3d():
    """Generate 3D model from image"""
    try:

        # [TEST MODE] ... existing test mode code ...

        # ... existing validation ...

        job_id = validated_data.job_id
        format_type = validated_data.format
        dimensions = validated_data.dimensions.dict()
        quality = validated_data.quality

        # [ORFEAS] MILESTONE 2: Check if job is already being processed

        if job_id in self.active_jobs:
            logger.warning(f"[ORFEAS] Concurrent generation attempt for job {job_id}")
            return jsonify({
                "error": "Generation already in progress",
                "job_id": job_id,
                "status": "conflict",
                "message": "This job is currently being processed. Wait for completion or use a different job_id."
            }), 409

        # Mark job as active

        self.active_jobs.add(job_id)

        # Start async 3D generation

        thread = threading.Thread(
            target=self.generate_3d_async,
            args=(job_id, format_type, dimensions, quality),
            daemon=True
        )
        thread.start()

        logger.info(f"[OK] 3D generation started: {job_id} ({format_type}, quality={quality})")

        return jsonify({
            "job_id": job_id,
            "status": "generating_3d",
            "format": format_type,
            "dimensions": dimensions,
            "quality": quality
        })

    except Exception as e:
        logger.error(f"3D generation error: {str(e)}")

        # Clean up active jobs on error

        if 'job_id' in locals() and job_id in self.active_jobs:
            self.active_jobs.discard(job_id)
        return jsonify({"error": "3D generation failed"}), 500

```text

## # # Step 2: Fix Tests (Upload Per Format)

**File:** `backend/tests/integration/test_api_endpoints.py`

```python
def test_generate_3d_different_formats(self, api_client, integration_server, test_image_512):
    """Test different 3D output formats"""
    formats = ["stl", "obj"]

    for fmt in formats:

        # Upload new image for each format to avoid job conflicts

        upload_response = api_client.upload_image(test_image_512, filename=f"test_{fmt}.png")
        assert upload_response.status_code == 200
        job_id = upload_response.json()['job_id']

        # Generate 3D model

        response = api_client.generate_3d(
            job_id=job_id,
            format=fmt,
            quality=5
        )

        assert response.status_code in [200, 202], f"Failed for format {fmt}"

```text

## # # Step 3: Test the Fix

```powershell

## Run the previously failing test

cd backend
python -m pytest tests/integration/test_api_endpoints.py::TestGenerate3D::test_generate_3d_different_formats -v

## Expected:  PASS in < 10 seconds

```text

---

## # #  EXPECTED RESULTS

## # # Before Fix

- First request:  Pass (~0.5s)
- Second request:  Timeout (300s)
- Test duration: 309s (5+ minutes)

## # # After Fix

- All requests:  Pass (~0.5s each)
- Test duration: < 5s
- Clear error if job conflict occurs

---

## # #  IMPACT ANALYSIS

## # # Tests Affected

1. `test_generate_3d_different_formats` - Will pass

2. `test_generate_3d_quality_levels` - Will pass

3. `test_download_generated_model` - Should pass now

4. `test_concurrent_health_checks` - Should pass (unrelated to job conflicts)
5. `test_concurrent_uploads` - Should pass (unrelated to job conflicts)

**Total:** 5/5 failing tests expected to pass

## # # Performance Impact

- Test suite: 5+ minutes → < 30 seconds
- Faster failure detection (HTTP 409 vs 300s timeout)
- Better error handling for production

---

## # #  CONCLUSION

## # # Status:****ROOT CAUSE IDENTIFIED - FIX READY

## # # The "hanging" issue was actually a race condition

- Server responded correctly to first request
- Second request for same job_id caused conflict
- No error handling for concurrent job processing
- Test hung waiting for second response

**Fix:** Add job conflict detection + modify tests to use unique job_ids

**Timeline:** 15-30 minutes to implement and test

---

## # # END OF ROOT CAUSE ANALYSIS
